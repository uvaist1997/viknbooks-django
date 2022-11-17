import os
from datetime import timedelta
from pathlib import Path

from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = "-&=8@5(*cr2a*w20vq&4d%zx%_9)3xv6&(^r6a_5^o(@#+%7n="

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# ALLOWED_HOSTS = ['192.168.1.14']
ALLOWED_HOSTS = ["192.168.1.22", "*"]
# ALLOWED_HOSTS = ['www.erp.vikncodes.com','erp.vikncodes.com','http://www.erp.vikncodes.com/']
# ALLOWED_HOSTS = ['www.demo.viknbooks.com','demo.viknbooks.com']


# Application definition

INSTALLED_APPS = [
    "rest_framework",
    "registration",
    "el_pagination",
    "versatileimagefield",
    "pwa",
    "corsheaders",
    "mailqueue",
    "django_rest_passwordreset",
    "django_inlinecss",
    "users.apps.AccountsConfig",
    "celery_progress",
    "django_user_agents",

    "ckeditor",
    "django_elasticsearch_dsl",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    # 'django.contrib.sites',
    "brands",
    "web",
    "main",
    "accounts",
    "inventories",
    "payrolls",
    "administrations",

    'django.contrib.sites',
    # 'core'
]
ELASTICSEARCH_DSL = {
    "default": {"hosts": "localhost:9200"},
}
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "users.middleware.OneSessionPerUserMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
]

# CORS_ORIGIN_ALLOW_ALL = True # If this is used then `CORS_ORIGIN_WHITELIST` will not have any effect
# CORS_ALLOW_CREDENTIALS = True
# CORS_ORIGIN_WHITELIST = [
#     'https://www.erp.vikncodes.com',
# ] # If this is used, then not need to use `CORS_ORIGIN_ALLOW_ALL = True`
# CORS_ORIGIN_REGEX_WHITELIST = [
#     'https://www.erp.vikncodes.com',
# ]

# If this is used then `CORS_ORIGIN_WHITELIST` will not have any effect
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    # 'http://192.168.1.20:8000',
    "http://localhost:8000",
]  # If this is used, then not need to use `CORS_ORIGIN_ALLOW_ALL = True`
CORS_ORIGIN_REGEX_WHITELIST = [
    "http://localhost:8000",
]

# CORS_ORIGIN_ALLOW_ALL = True # If this is used then `CORS_ORIGIN_WHITELIST` will not have any effect
# CORS_ALLOW_CREDENTIALS = True
# CORS_ORIGIN_WHITELIST = [
#     'https://www.demo.viknbooks.com',
# ] # If this is used, then not need to use `CORS_ORIGIN_ALLOW_ALL = True`
# CORS_ORIGIN_REGEX_WHITELIST = [
#     'https://www.demo.viknbooks.com',
# ]

ROOT_URLCONF = "testproject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "main.context_processors.main_context",
            ],
        },
    },
]

WSGI_APPLICATION = "testproject.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'thoufeeque',
#         'USER': 'vikncodes',
#         'PASSWORD': 'vikncodes123',
#         'HOST': 'localhost',
#         'PORT': '',
#         'DISABLE_SERVER_SIDE_CURSORS': True,
#     },
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'viknbooks_olddb',
#         'USER': 'vikncodes',
#         'PASSWORD': 'vikncodes123',
#         'HOST': 'localhost',
#         'PORT': ''
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "viknbooks",
        "USER": "vikncodes",
        "PASSWORD": "vikncodes123",
        "HOST": "localhost",
        "PORT": "",
    }
}
# MASTER===============
SITE_ID = 1
# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


AUTHENTICATION_BACKENDS = (
    "users.backend.EmailOrUsernameModelBackend",
    "django.contrib.auth.backends.ModelBackend",
)


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# SSO--------------
# SIMPLE_JWT = {
#     "ACCESS_TOKEN_LIFETIME": timedelta(days=365),
#     "REFRESH_TOKEN_LIFETIME": timedelta(days=730),
#     "ROTATE_REFRESH_TOKENS": True,
#     "BLACKLIST_AFTER_ROTATION": True,
# }
SSO_JWT_PUBLIC_KEY_PATH = os.path.join(
    Path(BASE_DIR).parent, 'config', 'sso_jwt_key.pub')
    
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=365),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=730),
    'ROTATE_REFRESH_TOKENS': True,
    # 'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'RS256',
    'SIGNING_KEY': None,
    'VERIFYING_KEY': open(SSO_JWT_PUBLIC_KEY_PATH).read(),
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',
}
# SSO END-------------

# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=1),
#     'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=30),
#     'ROTATE_REFRESH_TOKENS': False,
#     'BLACKLIST_AFTER_ROTATION': True,
#     'UPDATE_LAST_LOGIN': True,

#     'ALGORITHM': 'HS256',
#     'SIGNING_KEY': '',
#     'VERIFYING_KEY': None,
#     'AUDIENCE': None,
#     'ISSUER': None,

#     'AUTH_HEADER_TYPES': ('Bearer',),
#     'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
#     'USER_ID_FIELD': 'username',
#     'USER_ID_CLAIM': 'user_id',

#     'JTI_CLAIM': 'jti',
# }

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11211",
    }
}

USER_AGENTS_CACHE = "default"


LOGIN_URL = "/app/accounts/register/"
LOGOUT_URL = "/app/accounts/logout/"
LOGIN_REDIRECT_URL = "/companies/"

DATE_INPUT_FORMATS = ["%d-%m-%Y"]

VERSATILEIMAGEFIELD_SETTINGS = {
    "cache_length": 2592000,
    "cache_name": "versatileimagefield_cache",
    "jpeg_resize_quality": 70,
    "sized_directory_name": "__sized__",
    "filtered_directory_name": "__filtered__",
    "placeholder_directory_name": "__placeholder__",
    "create_images_on_demand": True,
    "image_key_post_processor": None,
    "progressive_jpeg": False,
}

# REST_FRAMEWORK = { 'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema' }

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# CELERY SETTINGS
# Celery Settings
BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"

MAILQUEUE_LIMIT = 100
MAILQUEUE_QUEUE_UP = True

ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_AUTO_LOGIN = True
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
ACCOUNT_EMAIL_VERIFICATION = "none"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "support@vikncodes.com"
EMAIL_HOST_PASSWORD = "blbgfqqjgezxahlc"
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = "support@vikncodes.com"
DEFAULT_BCC_EMAIL = "support@vikncodes.com"

DEFAULT_REPLY_TO_EMAIL = "support@vikncodes.com"
SERVER_EMAIL = "support@vikncodes.com"
EMAIL_USE_TLS = True
ADMIN_EMAIL = "support@vikncodes.com"


PWA_APP_NAME = "Vikn Books"
PWA_APP_DESCRIPTION = "My app description"
PWA_APP_THEME_COLOR = "#0A0302"
PWA_APP_BACKGROUND_COLOR = "#ffffff"
PWA_APP_DISPLAY = "standalone"
PWA_APP_SCOPE = "/"
PWA_APP_ORIENTATION = "any"
PWA_APP_START_URL = "/"
PWA_APP_STATUS_BAR_COLOR = "default"
PWA_APP_ICONS = [{"src": "/static/images/my_app_icon.png", "sizes": "167x167"}]
PWA_APP_ICONS_APPLE = [{"src": "/static/images/my_apple_icon.png", "sizes": "167x167"}]
PWA_APP_SPLASH_SCREEN = [
    {
        "src": "/static/images/icons/splash-640x1136.png",
        "media": "(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)",
    }
]
PWA_APP_DIR = "ltr"
PWA_APP_LANG = "en-US"
PWA_APP_DEBUG_MODE = False


LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)
LANGUAGES = (
    ("ar", _("Arabic")),
    ("en", _("English")),
)
LANGUAGE_CODE = "en-us"


TIME_ZONE = "Asia/Riyadh"

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_URL = "/static/"
STATIC_FILE_ROOT = os.path.join(BASE_DIR, "static")
STATIC_ROOT = os.path.join(BASE_DIR, "static/css")
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
