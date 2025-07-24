import os
from pathlib import Path
import environ

env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')

DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'unfold',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'storages',
    'django_ratelimit',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.projects',
    'apps.news',
    'apps.payments',
    'apps.analytics',
    'apps.admin_panel',
    'apps.qa',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_ratelimit.middleware.RatelimitMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
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

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres://user:password@host:port/dbname')
}


CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

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
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}


CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=['http://localhost:3000'])
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=['http://localhost:3000'])

CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

GITHUB_CLIENT_ID = env('GITHUB_CLIENT_ID', default='')
GITHUB_CLIENT_SECRET = env('GITHUB_CLIENT_SECRET', default='')
GITHUB_REDIRECT_URI = env('GITHUB_REDIRECT_URI', default='http://localhost:3000/auth/github/callback')

ENABLE_ANALYTICS = env.bool('ENABLE_ANALYTICS', default=True)
ENABLE_NOTIFICATIONS = env.bool('ENABLE_NOTIFICATIONS', default=True)
ENABLE_PAYMENT_GATEWAY = env.bool('ENABLE_PAYMENT_GATEWAY', default=True)

API_RATE_LIMIT_PER_MINUTE = env.int('API_RATE_LIMIT_PER_MINUTE', default=60)
API_RATE_LIMIT_PER_HOUR = env.int('API_RATE_LIMIT_PER_HOUR', default=1000)
MAX_UPLOAD_SIZE = env.int('MAX_UPLOAD_SIZE', default=104857600)
FILE_UPLOAD_MAX_MEMORY_SIZE = env.int('FILE_UPLOAD_MAX_MEMORY_SIZE', default=5242880)

MAINTENANCE_MODE = env.bool('MAINTENANCE_MODE', default=False)
MAINTENANCE_MESSAGE = env('MAINTENANCE_MESSAGE', default='Site is under maintenance. Please check back soon.')

MIRPAY_KASSA_ID = env('MIRPAY_KASSA_ID', default='1413')
MIRPAY_API_KEY = env('MIRPAY_API_KEY', default='')
MIRPAY_BASE_URL = env('MIRPAY_BASE_URL', default='https://mirpay.uz/api')
MIRPAY_SUCCESS_URL = env('MIRPAY_SUCCESS_URL', default='')
MIRPAY_FAILURE_URL = env('MIRPAY_FAILURE_URL', default='')

RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'django.log',
            'maxBytes': 1024*1024*5,
            'backupCount': 3,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

UNFOLD = {
    "SITE_TITLE": "Cooplink Admin",
    "SITE_HEADER": "Cooplink Administration",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: "https://cdn-icons-png.flaticon.com/512/1828/1828911.png",
        "dark": lambda request: "https://cdn-icons-png.flaticon.com/512/1828/1828911.png",
    },
    "SITE_LOGO": {
        "light": lambda request: "https://cdn-icons-png.flaticon.com/512/1828/1828911.png",
        "dark": lambda request: "https://cdn-icons-png.flaticon.com/512/1828/1828911.png",
    },
    "SITE_SYMBOL": "🚀",
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/png",
            "href": lambda request: "https://cdn-icons-png.flaticon.com/512/1828/1828911.png",
        },
    ],
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": "core.settings.environment_callback",
    "DASHBOARD_CALLBACK": "core.admin.dashboard_callback",
    "THEME": "dark",
    "LOGIN": {
        "image": lambda request: "https://images.unsplash.com/photo-1557804506-669a67965ba0?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1974&q=80",
        "redirect_after": lambda request: "/admin/",
    },
    "STYLES": [
        lambda request: "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
    ],
    "SCRIPTS": [
        lambda request: "https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js",
    ],
    "COLORS": {
        "primary": {
            "50": "239 246 255",
            "100": "219 234 254",
            "200": "191 219 254",
            "300": "147 197 253",
            "400": "96 165 250",
            "500": "59 130 246",
            "600": "37 99 235",
            "700": "29 78 216",
            "800": "30 64 175",
            "900": "30 58 138",
            "950": "23 37 84",
        },
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇺🇸",
                "uz": "🇺🇿",
                "ru": "🇷🇺",
            },
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
    },
    "TABS": [
        {
            "models": [
                "accounts.user",
            ],
            "items": [
                {
                    "title": "Profile",
                    "icon": "person",
                    "link": "/admin/accounts/user/{id}/change/",
                },
                {
                    "title": "Projects",
                    "icon": "work",
                    "link": "/admin/projects/project/?user__id__exact={id}",
                },
            ],
        },
        {
            "models": [
                "projects.project",
            ],
            "items": [
                {
                    "title": "Details",
                    "icon": "info",
                    "link": "/admin/projects/project/{id}/change/",
                },
                {
                    "title": "Analytics",
                    "icon": "analytics",
                    "link": "/admin/analytics/project/{id}/",
                },
            ],
        },
    ],
}

def environment_callback(request):
    return {
        "name": "Development" if DEBUG else "Production",
        "color": "#10b981" if DEBUG else "#ef4444",
    }
