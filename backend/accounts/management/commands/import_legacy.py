"""把合并前两个站点（topik / course）的数据导入统一数据库。

    python manage.py import_legacy --topik <topik db.sqlite3> --course <course db.sqlite3> --bilibili <bilibili 目录>
    默认只预览（在事务里执行后回滚），加 --apply 才写入。可重复执行：已存在的记录跳过。

规则：
- 用户以 topik 为准：保留 id、密码哈希、管理员身份、注册时间（旧登录令牌里的 user_id 因此继续有效）。
- 只在 course 存在且有可用密码的用户原样并入（原密码可直接登录）；course 里由统一登录自动建的占位用户（无可用密码）忽略。
- course 的 display_name 合并到同名用户。
- topik 的目录权限全部归到语言 ko（韩语），pdf 类型改名为 file。
- 科目保留 id；bilibili/<科目名小写>.txt 每行导入为一条课程视频，同科目内重复链接跳过。
"""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import User
from courses.links import parse_line, video_key
from courses.models import CourseVideo, Subject
from languages.models import Language, LanguageCategory, MediaPermission

KIND_MAP = {'video': 'video', 'audio': 'audio', 'pdf': 'file'}


class DryRun(Exception):
    pass


def utc(value):
    """旧库的时间是无时区的 UTC 字符串。"""
    if not value:
        return None
    dt = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def rows(db: Path, sql: str) -> list[dict]:
    con = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute(sql)]
    finally:
        con.close()


class Command(BaseCommand):
    help = '导入合并前 topik / course 两个站点的数据（默认预览，--apply 写入）'

    def add_arguments(self, parser):
        parser.add_argument('--topik', required=True, type=Path, help='topik 的 db.sqlite3')
        parser.add_argument('--course', required=True, type=Path, help='course 的 db.sqlite3')
        parser.add_argument('--bilibili', required=True, type=Path, help='course 的 bilibili/ 目录')
        parser.add_argument('--apply', action='store_true', help='真正写入（默认只预览）')

    def handle(self, *args, **opts):
        for k in ('topik', 'course', 'bilibili'):
            if not opts[k].exists():
                raise CommandError(f'找不到 {opts[k]}')
        self.log: list[str] = []
        try:
            with transaction.atomic():
                self.import_users(opts['topik'], opts['course'])
                self.import_permissions(opts['topik'])
                self.import_courses(opts['course'], opts['bilibili'])
                if not opts['apply']:
                    raise DryRun
        except DryRun:
            self.log.append('\n（预览模式，未写入。确认无误后加 --apply）')
        else:
            self.log.append('\n已写入。')
        self.stdout.write('\n'.join(self.log))

    # ── 用户 ────────────────────────────────────────────────────────────────
    def import_users(self, topik_db: Path, course_db: Path):
        topik = rows(topik_db, 'select * from user_user order by id')
        course = {r['username']: r for r in rows(course_db, 'select * from auth_user order by id')}
        self.user_map: dict[int, User] = {}   # topik id → 新用户
        self.log.append('== 用户')

        def take_email(email):
            email = (email or '').strip() or None
            if email and User.objects.filter(email=email).exists():
                self.log.append(f'   ! 邮箱 {email} 已被占用，置空')
                return None
            return email

        for r in topik:
            c = course.get(r['username'])
            display = (c or {}).get('display_name') or ''
            u = User.objects.filter(username=r['username']).first()
            if u:
                self.log.append(f'  = {r["username"]}：已存在，跳过')
            else:
                if User.objects.filter(pk=r['id']).exists():
                    raise CommandError(f'id {r["id"]} 已被其他用户占用，目标库应为空库')
                u = User(
                    id=r['id'], username=r['username'], password=r['password'],
                    email=take_email(r['email']), first_name=r['first_name'], last_name=r['last_name'],
                    is_staff=bool(r['is_staff']), is_superuser=bool(r['is_superuser']), is_active=bool(r['is_active']),
                    date_joined=utc(r['date_joined']), last_login=utc(r['last_login']), display_name=display,
                )
                u.save()
                self.log.append(f'  + {u.username}（id {u.id}，topik{"，管理员" if u.is_staff else ""}'
                                f'{"，显示名 " + display if display else ""}）')
            self.user_map[r['id']] = u

        topik_names = {r['username'] for r in topik}
        for name, c in course.items():
            if name in topik_names:
                continue
            if not c['password'] or c['password'].startswith('!'):
                self.log.append(f'  - {name}：course 自动建立的占位用户（无可用密码），忽略')
                continue
            if User.objects.filter(username=name).exists():
                self.log.append(f'  = {name}：已存在，跳过')
                continue
            u = User(
                username=name, password=c['password'], email=take_email(c['email']),
                first_name=c['first_name'], last_name=c['last_name'],
                is_staff=bool(c['is_staff']) or c.get('role') == 'admin', is_superuser=bool(c['is_superuser']),
                is_active=bool(c['is_active']), date_joined=utc(c['date_joined']), last_login=utc(c['last_login']),
                display_name=c.get('display_name') or '',
            )
            u.save()
            self.log.append(f'  + {name}（新 id {u.id}，仅 course，保留原密码）')

    # ── 权限 ────────────────────────────────────────────────────────────────
    def import_permissions(self, topik_db: Path):
        cat, _ = LanguageCategory.objects.get_or_create(name='东亚语言')
        ko, _ = Language.objects.get_or_create(slug='ko', defaults={'name': '韩语', 'category': cat})
        perms = rows(topik_db, 'select user_id, media_type, root_dir from permission_mediapermission order by id')
        added = 0
        for p in perms:
            u = self.user_map.get(p['user_id'])
            if not u:
                self.log.append(f'  ! 权限指向不存在的用户 id {p["user_id"]}，跳过')
                continue
            _, created = MediaPermission.objects.get_or_create(
                user=u, language=ko, media_type=KIND_MAP[p['media_type']], root_dir=p['root_dir'])
            added += created
        self.log.append(f'== 权限：{len(perms)} 条 → 新增 {added} 条（全部归入 {ko.name}/{ko.slug}）')

    # ── 科目与视频 ──────────────────────────────────────────────────────────
    def import_courses(self, course_db: Path, bili_dir: Path):
        self.log.append('== 科目与视频')
        for r in rows(course_db, 'select * from api_subject order by id'):
            s, created = Subject.objects.get_or_create(id=r['id'], defaults={
                'name': r['name'], 'description': r['description'], 'icon': r['icon'],
                'color': r['color'], 'keywords': r['keywords'],
            })
            txt = bili_dir / f'{r["name"].lower().replace(" ", "_")}.txt'
            n_add = n_dup = n_bad = 0
            if txt.exists():
                for i, line in enumerate(txt.read_text(encoding='utf-8').splitlines()):
                    if not line.strip():
                        continue
                    v = parse_line(line)
                    if not v:
                        n_bad += 1
                        self.log.append(f'     ! {txt.name} 第 {i + 1} 行没有链接，跳过：{line[:60]}')
                        continue
                    key = video_key(v['url'])
                    if s.videos.filter(video_key=key).exists():
                        n_dup += 1
                        continue
                    CourseVideo.objects.create(subject=s, sort_order=i + 1, video_key=key, **v)
                    n_add += 1
            self.log.append(f'  {"+" if created else "="} {s.id} {s.name}：{txt.name if txt.exists() else "无链接文件"}'
                            f' 新增 {n_add} 条，重复跳过 {n_dup}，无效 {n_bad}')
