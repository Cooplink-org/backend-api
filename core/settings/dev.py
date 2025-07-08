from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

PAYMENT_MODE = 'development'

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

INTERNAL_IPS = [
    '127.0.0.1',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
