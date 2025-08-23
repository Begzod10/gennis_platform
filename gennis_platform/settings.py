import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')
from celery.schedules import crontab

classroom_server = os.getenv('CLASSROOM_SERVER')
gennis_server = os.getenv('GENNIS_SERVER')

DEBUG = False

# ALLOWED_HOSTS = ['*']
ALLOWED_HOSTS = ['school.gennis.uz', 'localhost', '127.0.0.1']

INSTALLED_APPS = [
    'unfold',
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
    'bot.apps.BotConfig',
    'rooms.apps.RoomsConfig',
    'capital.apps.CapitalConfig',
    'overhead.apps.OverheadConfig',
    'attendances.apps.AttendancesConfig',
    'time_table.apps.TimeTableConfig',
    'lead.apps.LeadConfig',
    'classes.apps.ClassesConfig',
    'books.apps.BooksConfig',
    'observation.apps.ObservationConfig',
    'corsheaders',
    'school_time_table.apps.SchoolTimeTableConfig',
    'djoser',
    'tasks.apps.TasksConfig',
    'flows.apps.FlowsConfig',
    'lesson_plan.apps.LessonPlanConfig',
    'Calendar.apps.CalendarConfig',
    'encashment.apps.EncashmentConfig',
    "mobile.apps.MobileConfig",
    'django_filters',
    'ui',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gennis_platform.urls'

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'gennis_platform.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators


AUTH_USER_MODEL = 'user.CustomUser'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    # 'PAGE_SIZE': 10,  # number of items per page

    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('JWT',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

CELERY_BEAT_SCHEDULE = {
    "update-students-class-in-august": {
        "task": "group.tasks.update_class_task",
        "schedule": crontab(minute=0, hour=0, day_of_month="10", month_of_year="8"),
    },
    # "update-students-debts": {
    #     "task": "students.tasks.update_debts_task",
    #     # "schedule": crontab(minute=0, hour=0, day_of_month="20", month_of_year="8"),
    #     "schedule": crontab(minute="*/1"),
    # },
    "update-school-time-table": {
        "task": "school_time_table.tasks.update_school_time_table_task",
        "schedule": crontab(minute=0, hour=0, day_of_week="saturday")
        # "schedule": crontab(minute="*/1"),
    }
}

CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static_admin/'
STATIC_ROOT = BASE_DIR / 'static_admin'
MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
