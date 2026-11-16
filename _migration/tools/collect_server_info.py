"""在服务器上运行（只读）：采集两个后端的数据结构、数据快照与部署信息，打包为 zip。

用法（本地）：ssh ... 'python3 - <home>' < collect_server_info.py
只用标准库，兼容服务器自带的 Python 3.10。
不修改任何线上文件：数据库用 sqlite 备份 API 拷贝快照；.env 只记录键名，不记录值。
"""
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

HOME = Path(sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~'))
TS = time.strftime('%Y%m%d-%H%M%S')
OUT = HOME / f'merge_backup_{TS}'
OUT.mkdir()

DBS = {
    'topik': HOME / 'player3/backend/db.sqlite3',
    'course': HOME / 'course_system/backend/db.sqlite3',
}
SENSITIVE_COLS = {'password', 'session_data', 'token', 'key'}


def write(rel, text):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


def sh(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        return r.stdout + (('\n[stderr]\n' + r.stderr) if r.stderr.strip() else '')
    except Exception as e:  # noqa: BLE001
        return f'[error] {e}'


def describe_db(name, src):
    snap = OUT / 'db' / f'{name}.sqlite3'
    snap.parent.mkdir(parents=True, exist_ok=True)
    s = sqlite3.connect(f'file:{src}?mode=ro', uri=True)
    d = sqlite3.connect(snap)
    s.backup(d)
    d.close()
    s.close()

    con = sqlite3.connect(snap)
    con.row_factory = sqlite3.Row
    info = {'source': str(src), 'tables': {}}
    ddl = []
    for row in con.execute("select type, name, tbl_name, sql from sqlite_master where sql is not null order by type, name"):
        ddl.append(row['sql'] + ';')
    write(f'schema/{name}.sql', '\n\n'.join(ddl) + '\n')

    tables = [r[0] for r in con.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name")]
    for t in tables:
        q = t.replace('"', '""')
        cols = [dict(r) for r in con.execute(f'pragma table_info("{q}")')]
        fks = [dict(r) for r in con.execute(f'pragma foreign_key_list("{q}")')]
        idx = []
        for r in con.execute(f'pragma index_list("{q}")'):
            r = dict(r)
            r['columns'] = [c['name'] for c in con.execute(f'pragma index_info("{r["name"]}")')]
            idx.append(r)
        count = con.execute(f'select count(*) from "{q}"').fetchone()[0]
        for c in cols:
            cn = c['name'].replace('"', '""')
            c['value_types'] = {r[0]: r[1] for r in con.execute(f'select typeof("{cn}"), count(*) from "{q}" group by 1')}
            c['max_length'] = con.execute(f'select max(length("{cn}")) from "{q}"').fetchone()[0]
            c['distinct'] = con.execute(f'select count(distinct "{cn}") from "{q}"').fetchone()[0]
        samples = []
        for r in con.execute(f'select * from "{q}" limit 5'):
            r = dict(r)
            for k in r:
                if k in SENSITIVE_COLS and r[k] is not None:
                    r[k] = '<redacted>'
                elif isinstance(r[k], bytes):
                    r[k] = f'<{len(r[k])} bytes>'
            samples.append(r)
        info['tables'][t] = {'rows': count, 'columns': cols, 'foreign_keys': fks, 'indexes': idx, 'samples': samples}

    if 'django_migrations' in tables:
        info['migrations'] = [dict(r) for r in con.execute('select app, name, applied from django_migrations order by id')]
    con.close()
    write(f'schema/{name}.json', json.dumps(info, ensure_ascii=False, indent=2, default=str))

    # 便于阅读的摘要
    lines = [f'# {name}  ({src})', '']
    for t, v in info['tables'].items():
        lines.append(f'## {t}  rows={v["rows"]}')
        for c in v['columns']:
            lines.append(f'  - {c["name"]:<28} {c["type"]:<14} notnull={c["notnull"]} pk={c["pk"]} '
                         f'types={c["value_types"]} maxlen={c["max_length"]} distinct={c["distinct"]}')
        for fk in v['foreign_keys']:
            lines.append(f'  FK {fk["from"]} -> {fk["table"]}.{fk["to"]}')
        lines.append('')
    write(f'schema/{name}.summary.txt', '\n'.join(lines))


def env_keys(path):
    if not path.exists():
        return None
    keys = []
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            keys.append(line.split('=', 1)[0].strip())
    return keys


def main():
    for name, src in DBS.items():
        describe_db(name, src)

    # course 的 B 站链接数据（txt）与 media（很小，完整拷贝）
    cb = HOME / 'course_system/backend'
    for d in cb.glob('bilibili*'):
        if d.is_dir():
            shutil.copytree(d, OUT / 'course' / d.name)
    if (cb / 'media').exists():
        shutil.copytree(cb / 'media', OUT / 'course' / 'media')

    # topik 的 media 体量大（视频 80G+），只记录清单
    write('media/topik_manifest.tsv', sh(
        f"cd {HOME}/player3/backend/media && find . -type f -printf '%s\\t%TY-%Tm-%Td %TH:%TM\\t%p\\n' | sort -k3"))
    write('media/topik_du.txt', sh(f'cd {HOME}/player3/backend/media && du -sh * && du -sh --max-depth=2 . | sort -k2'))
    write('media/course_manifest.tsv', sh(f"cd {cb}/media && find . -type f -printf '%s\\t%p\\n'"))

    # 环境变量：只记录键名
    envs = {
        'topik .env.production': HOME / 'player3/backend/.env.production',
        'course .env': HOME / 'course_system/.env',
    }
    write('env_keys.json', json.dumps({k: env_keys(v) for k, v in envs.items()}, ensure_ascii=False, indent=2))

    # 运行环境与部署配置
    for proj in ('player3', 'course_system'):
        p = HOME / proj
        write(f'runtime/{proj}.txt', '\n'.join([
            '## python', sh(f'{p}/.venv/bin/python -V'),
            '## pip freeze', sh(f'{p}/.venv/bin/python -m pip freeze 2>/dev/null || /snap/bin/uv pip freeze --python {p}/.venv/bin/python'),
            '## pyvenv.cfg', sh(f'cat {p}/.venv/pyvenv.cfg'),
            '## tree (depth 2, excluding media/.venv)', sh(f'cd {p} && find . -maxdepth 2 -not -path "./.venv*" -not -path "*/media/*" | sort'),
        ]))
        for f in ('pyproject.toml', 'uv.lock', '.python-version'):
            if (p / f).exists():
                shutil.copy2(p / f, OUT / 'runtime' / f'{proj}.{f.lstrip(".")}')
    write('runtime/system.txt', '\n'.join([
        '## os', sh('cat /etc/os-release; uname -a'),
        '## uv', sh('/snap/bin/uv --version; /snap/bin/uv python list --only-installed'),
        '## disk', sh(f'df -h {HOME}'),
        '## services', sh('systemctl status player3 course-backend nginx --no-pager -n 0'),
        '## crontab', sh('crontab -l'),
        '## listening', sh('ss -ltnp 2>/dev/null'),
    ]))
    cfg = OUT / 'config'
    cfg.mkdir()
    for f in ['/etc/systemd/system/player3.service', '/etc/systemd/system/course-backend.service']:
        if os.path.exists(f):
            shutil.copy2(f, cfg)
    ng = cfg / 'nginx'
    ng.mkdir()
    for f in Path('/etc/nginx/conf.d').glob('*'):
        if f.is_file():
            shutil.copy2(f, ng)
    sn = Path('/etc/nginx/snippets/learning_star_proxy.conf')
    if sn.exists():
        shutil.copy2(sn, ng)

    archive = shutil.make_archive(str(OUT), 'zip', root_dir=OUT.parent, base_dir=OUT.name)
    print(archive)


main()
