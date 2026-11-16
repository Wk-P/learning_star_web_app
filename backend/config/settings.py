"""Learning Star 后端：语言学习 + 课程，一个项目、一个数据库、一套账号。

配置全部来自环境变量；本地开发与服务器都读取仓库根目录的 .env（模板 .env.example，不进 git）。
"""
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent      # backend/
ROOT_DIR = BASE_DIR.parent                              # 仓库根目录 / 服务器部署目录
load_dotenv(ROOT_DIR / '.env')


def env_list(name: str, default: str = '') -> list[str]:
    return [x.strip() for x in os.environ.get(name, default).split(',') if x.strip()]


DEBUG = os.environ.get('DEBUG', 'False') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY') or ('django-insecure-dev-only' if DEBUG else None)
if not SECRET_KEY:
    raise RuntimeError('缺少 SECRET_KEY（见 .env.example）')

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',

    'accounts',
    'languages',
    'courses',
]

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ── 数据目录：数据库与媒体文件都在这里，部署永不覆盖 ──────────────────────────
DATA_DIR = Path(os.environ.get('DATA_DIR') or BASE_DIR / 'data')
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATA_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 媒体：MEDIA_ROOT/languages/<语言 slug>/{videos,audios,files}/<顶层目录>/...
# 只能经 /media/ 受保护视图访问（校验登录与目录权限）
MEDIA_URL = '/media/'
MEDIA_ROOT = Path(os.environ.get('MEDIA_ROOT') or DATA_DIR / 'media')

DATA_UPLOAD_MAX_MEMORY_SIZE = 52_428_800
FILE_UPLOAD_MAX_MEMORY_SIZE = 52_428_800

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': False,
    # 沿用线上的 JWT_SIGNING_KEY：切换后已登录用户不会被踢下线
    'SIGNING_KEY': os.environ.get('JWT_SIGNING_KEY') or SECRET_KEY,
}

# 前端与后端同域（nginx / vite 代理），一般不需要 CORS；本地直连后端调试时可配置
CORS_ALLOWED_ORIGINS = env_list('CORS_ALLOWED_ORIGINS')
