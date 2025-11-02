from firstblog.password import validate_password_length
import os
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables from .env file in project root
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Now use environment variables
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG') == 'True'
GOOGLE_OAUTH_CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
GITHUB_OAUTH_CLIENT_ID = os.environ.get('GITHUB_OAUTH_CLIENT_ID')
GITHUB_OAUTH_CLIENT_SECRET = os.environ.get('GITHUB_OAUTH_CLIENT_SECRET')
DATABASE_NAME = os.environ.get('DATABASE_NAME')
DATABASE_USER = os.environ.get('DATABASE_USER')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE_PORT = os.environ.get('DATABASE_PORT')
DATABASE_ENGINE = os.environ.get('DATABASE_ENGINE')


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1:8000']


# Application definition
AUTH_USER_MODEL = 'firstblog.CustomUser'

INSTALLED_APPS = [
    # Unfold admin customization
    'unfold',
    'unfold.contrib.filters',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'firstblog',
    'firstblog.templatetags',
    # third-party apps
    'multiselectfield',
    'tinymce',

    # Allauth and crispy forms can be added here later
    'allauth',
    'allauth.account',

    'allauth.socialaccount',

    # Add the providers you want to enable:
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
]


TINYMCE_DEFAULT_CONFIG = {
    'height': 500,
    'width': '100%',
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'theme': 'silver',
    'plugins': '''
        advlist autolink lists link image charmap print preview anchor
        searchreplace visualblocks code fullscreen insertdatetime media table
        paste code help wordcount
    ''',
    'toolbar': '''
        undo redo | formatselect | bold italic backcolor |
        alignleft aligncenter alignright alignjustify |
        bullist numlist outdent indent | link image media |
        table | removeformat | help
    ''',
    'menubar': 'file edit view insert format tools table help',
    'branding': False,
    'promotion': False,
    'content_css': '/static/css/tinymce-content.css',  
    'content_style': '''
        body {
            font-family: Arial, sans-serif;
            font-size: 14px;
            margin: 20px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 8px 12px;
            text-align: left;
        }
        th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        a {
            color: #667eea;
            text-decoration: underline;
        }
        a:hover {
            color: #5a67d8;
        }
    ''',
    'table_default_attributes': {
        'border': '1'
    },
    'table_default_styles': {
        'border-collapse': 'collapse',
        'width': '100%'
    },
    'link_assume_external_targets': True,
    'link_title': False,
    'paste_data_images': True,
}

MIDDLEWARE = [
    "allauth.account.middleware.AccountMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'blogproject.urls'

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

WSGI_APPLICATION = 'blogproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE'),
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.environ.get('DATABASE_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

# settings.py
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#         'OPTIONS': {
#             'min_length': 8,
#         }
#     },
#     {
#         'NAME': 'path.to.custom.password_validators.CustomValidator',
#         'OPTIONS': {
#             'option1': 'value1',
#             'option2': 'value2',
#         }
#     },
# ]

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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIR = (os.path.join(BASE_DIR, 'static'))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'




UNFOLD = {
    "SITE_TITLE": "Blog Admin",
    "SITE_HEADER": "Blog Administration",
    "SITE_SUBHEADER": "Welcome to Blog Admin",
    "SITE_LOGO": {
        # "light": lambda request: static("logo-light.svg"),  # light mode
        # "dark": lambda request: static("logo-dark.svg"),  # dark mode
    },
    }
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGIN_METHOD = {'email', 'username'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_UNIQUE_EMAIL = True
CRISPY_TEMPLATE_PACK = 'bootstrap4'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': GOOGLE_OAUTH_CLIENT_ID,
            'secret': GOOGLE_OAUTH_CLIENT_SECRET ,
            'key': ''
        }
    },
    'github': {
        'APP': {
            'client_id': GITHUB_OAUTH_CLIENT_ID,
            'secret': GITHUB_OAUTH_CLIENT_SECRET,
            'key': ''
        }
    }
}