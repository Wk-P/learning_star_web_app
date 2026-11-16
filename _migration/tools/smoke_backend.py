import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, sys.argv[1])
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
media = Path(tempfile.mkdtemp())
os.environ['MEDIA_ROOT'] = str(media)
import django  # noqa: E402

django.setup()
from django.conf import settings  # noqa: E402
from django.test import Client  # noqa: E402
from django.test.utils import setup_test_environment  # noqa: E402
from rest_framework_simplejwt.tokens import RefreshToken  # noqa: E402

from accounts.models import User  # noqa: E402

setup_test_environment()
settings.ALLOWED_HOSTS = ['*']
ko = media / 'languages/ko'
(ko / 'videos/直播课/第1课').mkdir(parents=True)
(ko / 'videos/直播课/第1课/playlist.m3u8').write_text('#EXTM3U')
(ko / 'videos/直播课/第1课/a.ts').write_bytes(b'x' * 100)
(ko / 'videos/秘密班/第2课').mkdir(parents=True)
(ko / 'videos/秘密班/第2课/playlist.m3u8').write_text('#EXTM3U')
(ko / 'audios/47_TOPIK2').mkdir(parents=True)
(ko / 'audios/47_TOPIK2/1.mp3').write_bytes(b'0123456789')
(ko / 'files/TOPIK2_真题').mkdir(parents=True)
(ko / 'files/TOPIK2_真题/卷子.hwp').write_bytes(b'h')

def client(u):
    tok = RefreshToken.for_user(u)
    tok['username'], tok['is_staff'] = u.username, u.is_staff
    return Client(HTTP_AUTHORIZATION=f'Bearer {tok.access_token}'), str(tok.access_token)

ok = True
def check(name, cond, extra=''):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + name, extra if not cond else '')

admin = User.objects.get(username='admin')
stu = User.objects.get(username='soar009')   # 线上权限：video 102届TOPIK保命班、topik韩语课
a, _ = client(admin)
s, s_tok = client(stu)

r = s.get('/api/languages/'); check('分类树', r.status_code == 200 and r.json()[0]['languages'][0]['slug'] == 'ko', r.content[:200])
r = a.get('/api/languages/ko/video/'); check('管理员看全部视频文件夹', r.status_code == 200 and len(r.json()) == 2, r.content[:300])
r = s.get('/api/languages/ko/video/'); check('学生无权限目录被过滤', r.status_code == 200 and r.json() == [], r.content[:300])
a.put('/api/languages/permissions/users/%d/' % stu.id, {'ko': {'video': ['直播课'], 'audio': ['47_TOPIK2'], 'file': []}}, content_type='application/json')
r = s.get('/api/languages/ko/video/'); check('授权后可见', len(r.json()) == 1 and r.json()[0]['path'] == ['直播课'], r.content[:300])
url = r.json()[0]['items'][0]['url']; check('URL 格式', url == '/media/languages/ko/videos/直播课/第1课/playlist.m3u8', url)
r = Client().get('/media/languages/ko/videos/直播课/第1课/a.ts', HTTP_COOKIE=f'access_token={s_tok}'); check('cookie 访问媒体', r.status_code == 200)
r = s.get('/media/languages/ko/videos/秘密班/第2课/playlist.m3u8'); check('无权限媒体 403', r.status_code == 403)
r = Client().get('/media/languages/ko/videos/直播课/第1课/a.ts'); check('未登录 401', r.status_code == 401)
r = s.get('/media/languages/ko/audios/47_TOPIK2/1.mp3', HTTP_RANGE='bytes=2-5'); check('Range 206', r.status_code == 206 and b''.join(r.streaming_content) == b'2345')
r = s.get('/media/languages/ko/videos/直播课/../秘密班/第2课/playlist.m3u8'); check('路径穿越拦截', r.status_code in (403, 404), r.status_code)
r = a.get('/api/languages/ko/file/'); check('资料 hwp', r.json()[0]['items'][0]['ext'] == 'hwp')
r = a.get('/api/languages/permissions/tree/'); check('权限树', 'ko' in r.json() and r.json()['ko']['video'][0]['label'], r.content[:200])
r = s.get('/api/languages/me/permissions/'); check('我的权限', r.json()['ko']['video'] == ['直播课'], r.content)
r = s.get('/api/courses/subjects/'); check('科目 9 个', len(r.json()) == 9)
r = s.get('/api/courses/subjects/9/videos/'); check('衣食住行 21 条', len(r.json()) == 21 and 'levels' in r.json()[0])
r = a.post('/api/courses/admin/subjects/1/videos/', {'line': '测试 https://www.bilibili.com/video/BV1KN411n7pp/?p=2', 'levels': ['入门']}, content_type='application/json')
check('重复链接 409', r.status_code == 409, r.content)
r = a.post('/api/courses/admin/subjects/1/videos/', {'line': '测试 https://youtu.be/dQw4w9WgXcQ', 'levels': ['入门'], 'tags': '新,好'}, content_type='application/json')
check('新增视频', r.status_code == 201 and r.json()['tags'] == ['YouTube', '新', '好'], r.content)
vid = r.json()['id']
r = a.patch(f'/api/courses/admin/subjects/1/videos/{vid}/', {'url': 'https://www.bilibili.com/video/BV1xx411c7mD'}, content_type='application/json')
check('改链接换平台标签', r.json()['tags'][0] == 'B站', r.content)
r = a.delete(f'/api/courses/admin/subjects/1/videos/{vid}/'); check('删除视频', r.status_code == 204)
r = s.post('/api/courses/admin/subjects/', {'name': 'x'}, content_type='application/json'); check('学生不能管理科目', r.status_code == 403)
r = Client().post('/api/accounts/register/', {'username': 'newbie', 'password': '123456'}, content_type='application/json'); check('注册', r.status_code == 201, r.content)
r = Client().post('/api/auth/token/', {'username': 'newbie', 'password': '123456'}, content_type='application/json'); check('登录', r.status_code == 200 and 'access' in r.json())
r = s.patch('/api/accounts/me/', {'display_name': '测试名'}, content_type='application/json'); check('改显示名', r.json()['display_name'] == '测试名')
r = a.get('/api/accounts/users/'); check('用户列表', len(r.json()) == 6, len(r.json()))
User.objects.filter(username='newbie').delete()
stu.display_name = ''; stu.save()
a.put('/api/languages/permissions/users/%d/' % stu.id, {'ko': {'video': ['102届TOPIK保命班', 'topik韩语课']}}, content_type='application/json')
print('ALL OK' if ok else 'SOME FAILED')
