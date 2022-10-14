import os
from os.path import dirname
import environ
from dotenv import load_dotenv

BASE_DIR = dirname(dirname(dirname(dirname(os.path.abspath(__file__)))))

load_dotenv(os.path.join(BASE_DIR, ".env"))

CONTENT_DIR = os.path.join(BASE_DIR, 'content')
LOGIN_REDIRECT_URL = 'home'
AUTH_USER_MODEL = 'account.UrlUser'
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760 # 10mb = 10 * 1024 *1024
USE_REMEMBER_ME = True
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'bootstrap4',
    'main',
    'account', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'URL_Shortener.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(CONTENT_DIR, 'templates')],
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

WSGI_APPLICATION = 'URL_Shortener.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE'  : 'django.db.backends.postgresql',
        'NAME'    : os.getenv('DATABASE_NAME'),
        'USER'    : os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST'    : os.getenv('DATABASE_HOST'),
        'PORT'    : os.getenv('DATABASE_PORT') 
    }
}

ENABLE_USER_ACTIVATION = True
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS       = True
EMAIL_HOST          = os.getenv('EMAIL_HOST') 
EMAIL_HOST_USER     = os.getenv('EMAIL_HOST_USER')
DEFAULT_FROM_EMAIL  = os.getenv('DEFAULT_FROM_EMAIL') 
SERVER_EMAIL        = os.getenv('SERVER_EMAIL')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT          = int(os.getenv('EMAIL_PORT'))



AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'account.backends.CaseInsensitiveModelBackend',
]

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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_ROOT = os.path.join(CONTENT_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(CONTENT_DIR, 'media')
MEDIA_URL  = '/media/'

STATICFILES_DIRS = [
    os.path.join(CONTENT_DIR, 'assets'), 
    os.path.join(CONTENT_DIR, 'media')
]
TEMP = os.path.join(CONTENT_DIR, 'media/temp')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
