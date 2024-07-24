"""
Django settings for gennis_platform project.

Generated by 'django-admin startproject' using Django 4.2.13.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = 'django-insecure-8!t!6$g#(34ro((m-7t$#(zek1=b=y2ltslop@w71$^6)wb_rc'

SECRET_KEY = 'django-insecure-ic2opu2tndxc7=#h6l!u!o_0o8-olxsk6#@o8be165!6&j!o!j'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'user.apps.UserConfig',
    'system.apps.SystemConfig',
    'location.apps.LocationConfig',
    'branch.apps.BranchConfig',
    'permissions.apps.PermissionsConfig',
    'language.apps.LanguageConfig',
    'group.apps.GroupConfig',
    'payments.apps.PaymentsConfig',
    'students.apps.StudentsConfig',
    'subjects.apps.SubjectsConfig',
    'teachers.apps.TeachersConfig',
    'rooms.apps.RoomsConfig',
    'class.apps.ClassConfig',
    'overhead.apps.OverheadConfig',
    'attendances.apps.AttendancesConfig',
    'time_table.apps.TimeTableConfig',
    'lead.apps.LeadConfig',
    'books.apps.BooksConfig',
    'drf_yasg',
    'djoser',
    'django_cron',
    'corsheaders',
]

MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware', 'django.middleware.security.SecurityMiddleware',
              'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware',
              'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware',
              'django.contrib.messages.middleware.MessageMiddleware',
              'django.middleware.clickjacking.XFrameOptionsMiddleware', ]

ROOT_URLCONF = 'gennis_platform.urls'

TEMPLATES = [
    {'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [BASE_DIR / 'templates'], 'APP_DIRS': True,
     'OPTIONS': {'context_processors': ['django.template.context_processors.debug',
                                        'django.template.context_processors.request',
                                        'django.contrib.auth.context_processors.auth',
                                        'django.contrib.messages.context_processors.messages', ], }, }, ]

WSGI_APPLICATION = 'gennis_platform.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql', 'NAME': 'gennis_platform', 'USER': 'postgres',
                         'PASSWORD': '123', 'HOST': 'localhost', 'PORT': '5432'}}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_USER_MODEL = 'user.CustomUser'

AUTH_PASSWORD_VALIDATORS = [{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
                            {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
                            {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
                            {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', }, ]

REST_FRAMEWORK = {'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination', 'PAGE_SIZE': 2,

                  'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer',
                                               'rest_framework.renderers.BrowsableAPIRenderer', ],

                  'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny', ],

                  'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework_simplejwt.authentication.JWTAuthentication',
                                                     'rest_framework.authentication.BasicAuthentication',
                                                     'rest_framework.authentication.SessionAuthentication', ]}
SIMPLE_JWT = {'ACCESS_TOKEN_LIFETIME': timedelta(minutes=600), 'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
              'ROTATE_REFRESH_TOKENS': False, 'BLACKLIST_AFTER_ROTATION': False, 'UPDATE_LAST_LOGIN': False,

              'ALGORITHM': 'HS256', 'SIGNING_KEY': SECRET_KEY, 'VERIFYING_KEY': None, 'AUDIENCE': None, 'ISSUER': None,
              'JWK_URL': None, 'LEEWAY': 0,

              'AUTH_HEADER_TYPES': ('JWT',), 'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION', 'USER_ID_FIELD': 'id',
              'USER_ID_CLAIM': 'user_id',
              'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

              'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',), 'TOKEN_TYPE_CLAIM': 'token_type',

              'JTI_CLAIM': 'jti',

              'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp', 'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
              'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1), }
SWAGGER_SETTINGS = {"SECURITY_DEFINITIONS": {"Bearer": {"type": "apiKey", "name": "Authorization", "in": "header", }},
                    "USE_SESSION_AUTH": True, }
# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_ROOT = BASE_DIR / 'media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
