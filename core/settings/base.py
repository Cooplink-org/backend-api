import os
from pathlib import Path
from decouple import config
import structlog

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me')

DEBUG = config('DEBUG', default=False, cast=bool)

# Enhanced ALLOWED_HOSTS configuration
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'e009-213-230-93-69.ngrok-free.app',
    'c5c2-213-230-93-60.ngrok-free.app',
    '.herokuapp.com',
    '.vercel.app',
    '.lovable.app',
    '.pythonanywhere.com',
    '.railway.app',
    '.cooplink.uz',
    'cooplink.uz',
    'www.cooplink.uz',
    'api.cooplink.uz',
]

# Add custom ALLOWED_HOSTS from environment
if config('ALLOWED_HOSTS', default=''):
    ALLOWED_HOSTS.extend(config('ALLOWED_HOSTS').split(','))

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
    'drf_spectacular',
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

# Templates needed for Django admin and API documentation
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='defaultdb'),
        'USER': config('DB_USER', default='avnadmin'),
        'PASSWORD': config('DB_PASSWORD', default='AVNS_8LO-3eOT9gvprUEFL2X'),
        'HOST': config('DB_HOST', default='pg-2940a079-djangocourse37-983a.j.aivencloud.com'),
        'PORT': config('DB_PORT', default='25822'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/0'),
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

# Static files only for admin and API docs
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
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Cooplink API',
    'DESCRIPTION': 'A platform for developers to buy and sell code/projects',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5500',
    'https://e009-213-230-93-69.ngrok-free.app',
    'https://cooplink.uz',
    'https://www.cooplink.uz',
    'https://api.cooplink.uz',
    'https://*.vercel.app',
    'https://*.lovable.app',
    'https://*.pythonanywhere.com',
]

if config('CORS_ALLOWED_ORIGINS', default=''):
    CORS_ALLOWED_ORIGINS.extend(config('CORS_ALLOWED_ORIGINS').split(','))

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False  # Never allow all origins in production

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5500',
    'https://cooplink.uz',
    'https://e009-213-230-93-69.ngrok-free.app',
    'https://www.cooplink.uz',
    'https://api.cooplink.uz',
    'https://*.vercel.app',
    'https://*.lovable.app',
    'https://*.pythonanywhere.com',
]

if config('CSRF_TRUSTED_ORIGINS', default=''):
    CSRF_TRUSTED_ORIGINS.extend(config('CSRF_TRUSTED_ORIGINS').split(','))

CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# GitHub OAuth Configuration
GITHUB_CLIENT_ID = config('GITHUB_CLIENT_ID', default='')
GITHUB_CLIENT_SECRET = config('GITHUB_CLIENT_SECRET', default='')
GITHUB_REDIRECT_URI = config('GITHUB_REDIRECT_URI', default='http://localhost:3000/auth/github/callback')

# Feature Flags
ENABLE_ANALYTICS = config('ENABLE_ANALYTICS', default=True, cast=bool)
ENABLE_NOTIFICATIONS = config('ENABLE_NOTIFICATIONS', default=True, cast=bool)
ENABLE_PAYMENT_GATEWAY = config('ENABLE_PAYMENT_GATEWAY', default=True, cast=bool)

# Performance & Limits
API_RATE_LIMIT_PER_MINUTE = config('API_RATE_LIMIT_PER_MINUTE', default=60, cast=int)
API_RATE_LIMIT_PER_HOUR = config('API_RATE_LIMIT_PER_HOUR', default=1000, cast=int)
MAX_UPLOAD_SIZE = config('MAX_UPLOAD_SIZE', default=104857600, cast=int)  # 100MB
FILE_UPLOAD_MAX_MEMORY_SIZE = config('FILE_UPLOAD_MAX_MEMORY_SIZE', default=5242880, cast=int)  # 5MB

# Maintenance
MAINTENANCE_MODE = config('MAINTENANCE_MODE', default=False, cast=bool)
MAINTENANCE_MESSAGE = config('MAINTENANCE_MESSAGE', default='Site is under maintenance. Please check back soon.')

MIRPAY_KASSA_ID = config('MIRPAY_KASSA_ID', default='1413')
MIRPAY_API_KEY = config('MIRPAY_API_KEY', default='13ee7a1299bc5ced2e749899658a69c8')
MIRPAY_BASE_URL = config('MIRPAY_BASE_URL', default='https://mirpay.uz/api')
MIRPAY_SUCCESS_URL = config('MIRPAY_SUCCESS_URL', default='')
MIRPAY_FAILURE_URL = config('MIRPAY_FAILURE_URL', default='')

RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Create logs directory if it doesn't exist
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
            'maxBytes': 1024*1024*5,  # 5MB
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

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Static files configuration for API-only
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Django Unfold Configuration
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

# Environment callback for Django Unfold
def environment_callback(request):
    """Return environment info for Django Unfold"""
    return {
        "name": "Development" if DEBUG else "Production",
        "color": "#10b981" if DEBUG else "#ef4444",
    }
