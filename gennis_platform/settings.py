import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'adsda')
from celery.schedules import crontab

classroom_server = os.getenv('CLASSROOM_SERVER')
# classroom_server = "http://192.168.1.11:5001"
gennis_server = os.getenv('GENNIS_SERVER')
BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000')

DEBUG = os.getenv('DEBUG', True)

# ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    # "silk",
    'unfold',
    'drf_spectacular',
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
    'rest_framework',
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
    'channels',
    'ui',
    'terms',
    'parents',
    'parties',
    'apps.investor.apps.InvestorConfig',
    'maintenance.apps.MaintenanceConfig',
    "report",
    'surveys'
]

MIDDLEWARE = [
    # 'silk.middleware.SilkyMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # "tasks.middlewear.RecurringTaskMiddleware",
    "tasks.middlewear.ApiLogMiddleware",
]

ROOT_URLCONF = 'gennis_platform.urls'

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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
ASGI_APPLICATION = 'your_project.asgi.application'
WSGI_APPLICATION = 'gennis_platform.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    },
    'management': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('MANAGEMENT_DB_NAME'),
        'USER': os.getenv('MANAGEMENT_DB_USER'),
        'PASSWORD': os.getenv('MANAGEMENT_DB_PASSWORD'),
        'HOST': os.getenv('MANAGEMENT_DB_HOST'),
        'PORT': os.getenv('MANAGEMENT_DB_PORT', '5432'),
    },
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
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('JWT', "Bearer"),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

CELERY_BEAT_SCHEDULE = {
    "update-students-class-in-august": {
        "task": "group.tasks.update_class_task",
        "schedule": crontab(minute=0, hour=0, day_of_month="10", month_of_year="8"),
    },

    # Run every 1st day of every month at 00:00
    "update-students-debts": {
        "task": "students.tasks.update_student_debt",
        "schedule": crontab(minute=0, hour=0, day_of_month="1"),  # month_of_year="*" is optional
        # If you really want “every 2 months” etc, use:
        # "schedule": crontab(minute=0, hour=0, day_of_month="1", month_of_year="*/2"),
    },

    # Every Saturday at 00:00
    "update-school-time-table": {
        "task": "school_time_table.tasks.update_school_time_table_task",
        "schedule": crontab(minute=0, hour=0, day_of_week="sunday"),
        # "schedule": crontab(minute="*/1"),
    },

    # Daily at 21:00
    "investor_report_daily": {
        "task": "apps.investor.tasks.snapshot_investor_month",
        "schedule": crontab(minute=0, hour=21),
    },
    "lesson_plan": {
        "task": "lesson_plan.tasks.create_lesson_plans",
        # "schedule": crontab(minute=0, hour=0),
        "schedule": crontab(minute="*/1"),

    },
    "daily_summary_task": {
        "task": "encashment.tasks.daily_summary",
        "schedule": crontab(minute=0, hour=20),
        # "schedule": crontab(minute="*/1"),

    },
    # "update_deleted_students_debts": {
    #     "task": "students.tasks.update_deleted_students_debts",
    #     # "schedule": crontab(minute=0, hour=0, day_of_month="1"),
    #     "schedule": crontab(minute="*/1")
    #
    # },

}

CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static_admin/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [BASE_DIR / "staticfiles"]

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# SILKY_PYTHON_PROFILER = True
CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000", "https://school.gennis.uz",
                        "https://office.gennis.uz",
                        "http://localhost:3000", "http://0.0.0.0:8000", "http://100.81.196.80:3000",
                        'http://100.94.144.113:8000', 'http://100.124.167.36:3000']
REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = 'drf_spectacular.openapi.AutoSchema'

SPECTACULAR_SETTINGS = {
    'TITLE': 'Turon Platform API',
    'DESCRIPTION': 'Turon platformasi uchun to\'liq REST API.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'CONTACT': {'name': 'Backend Team'},
    'LICENSE': {'name': 'MIT'},
    'COMPONENT_SPLIT_REQUEST': True,
    'DISABLE_ERRORS_AND_WARNINGS': True,
    'SORT_OPERATIONS': False,
}
