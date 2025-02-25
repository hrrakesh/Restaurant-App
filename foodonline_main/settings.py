from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast= bool)

ALLOWED_HOSTS = ['127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    "accounts",
    "vendor",
    "menu",
    "marketplace",
    "django.contrib.gis",
    "customers",
    "orders",
]

AUTH_USER_MODEL = "accounts.User"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    "orders.request_object.RequestObjectMiddleware"
]

ROOT_URLCONF = 'foodonline_main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                "accounts.context_processors.get_vendor",
                "accounts.context_processors.get_user_profile",
                "accounts.context_processors.get_google_api",
                "accounts.context_processors.get_pay_pal_id",
                
                "marketplace.context_processors.get_cart_counter",
                "marketplace.context_processors.get_cart_amount",
            ],
        },
    },
]

WSGI_APPLICATION = 'foodonline_main.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.postgresql', # plane db 
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # spatial db
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR/'static'
STATICFILES_DIRS = [
    'foodonline_main/static',
]

# Media Files Configurations
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR/'media'


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

# email configuration

import smtplib


# password = config('password')

from_mail = ''

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = from_mail
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = ''
DEFAULT_ALERT_FROM_EMAIL = ''
DEFAULT_NOTIFICATION_FROM_EMAIL = ''
DEFAULT_NOTIFICATION_FROM_EMAIL_NEWS_ALERT = ''
DEFAULT_NOTIFICATION_ORDER_CONFIRMATION = ''

GOOGLE_API_KEY = config('GOOGLE_API_KEY')
PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID')


import os

os.environ['PATH'] = os.path.join(BASE_DIR, 'env\Lib\site-packages\osgeo') + ';' + os.environ['PATH']
os.environ['PROJ_LIB'] = os.path.join(BASE_DIR, 'env\Lib\site-packages\osgeo\data\proj') + ';' + os.environ['PATH']
GDAL_LIBRARY_PATH = os.path.join(BASE_DIR, 'env\Lib\site-packages\osgeo\gdal.dll')

SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'


#paypal usage yes or no
USE_PAY_PAL = True
USE_RAZOR_PAY = True


RZP_KEY_ID = config('RZP_KEY_ID')
RZP_KEY_SECRET = config('RZP_KEY_SECRET')
