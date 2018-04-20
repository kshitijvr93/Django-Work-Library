"""
Django settings for marshal1 project.

Modified to first discover some environmental settings and define some
settings from the executing user's my_secrets folder and its python files.

After that, the rest was originally Generated by 'django-admin startproject'
using Django 1.11.5.
"""

import os, sys, os.path
MY_SECRETS_FOLDER = os.environ['MY_SECRETS_FOLDER']
sys.path.append(os.path.abspath(MY_SECRETS_FOLDER))
# print ("Using MY_SECRETS_FOLDER='{}'".format(MY_SECRETS_FOLDER))

# IMPORT SETTINGS FOR MARSHALING APPLICATION WEBSITE (MAW) settings
from maw_settings import *
sys.path.append(MAW_MODULES_FOLDER)

# Some MAW extract,translate, load utilities, some others too.
import etl
#print("Using sys.path={}".format(repr(sys.path)))


########## ORIGINAL DJANGO SETTINGS #############
"""
For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

APPEND_SLASH = True
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@0-(8hq&*mj^ctt!x%118=s5w1c^l^)#6j*a#710se@)76jmwb'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    #'maw_home.apps.MawHomeConfig',
    'hathitrust.apps.HathitrustConfig',
    'cuba_libro.apps.CubaLibroConfig',
    'lcroyster.apps.LcroysterConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'ckeditor',
    'ckeditor_uploader',
]

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media_root','')

# RVP EXPERIMENT MEDIA_URL
MEDIA_URL =  '/media/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'marshal1.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Override with project root templates folder, see
        # https://docs.djangoproject.com/en/2.0/howto/overriding-templates/
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.github.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',

    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_GITHUB_KEY = GITHUB_CLIENT_ID
SOCIAL_AUTH_GITHUB_SECRET = GITHUB_CLIENT_SECRET
SOCIAL_AUTH_TWITTER_KEY = MAW_SOCIAL_AUTH_TWITTER_KEY
SOCIAL_AUTH_TWITTER_SECRET = MAW_SOCIAL_AUTH_TWITTER_SECRET
SOCIAL_AUTH_FACEBOOK_KEY=MAW_SOCIAL_AUTH_FACEBOOK_KEY
SOCIAL_AUTH_FACEBOOK_SECRET=MAW_SOCIAL_AUTH_FACEBOOK_SECRET

#Facebook balks because django local runserver is on http.. potential
# solution is from: https://github.com/python-social-auth/social-app-django/issues/132
# This may ruin twitter and github though...
# SOCIAL_AUTH_REDIRECT_IS_HTTPS = True


WSGI_APPLICATION = 'marshal1.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DB_ENGINE_BACKENDS_STANDARD=['sqlite3','postgresql','mysql','oracle']

# NB: Databases is really a dictionary of connecton name keys, and each
# value is a dictionary of django-reserved names to designate connecton info to
# a particular databse.
# NOTE: These database NAME values cannot be changed without changing the
# app.py config in the apps that use them

if MAW_ENV == 'production':
    DATABASES['lcroyster_connection'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'LCRoysterproject',
        'USER': 'LCRoysterproject',
        'PASSWORD': MAW_OYSTER_MYSQL_PRODUCTION_PASSWORD,
        'HOST': 'ict-prod-hosting02.mysql.osg.ufl.edu',
        'PORT': '3354',
        'OPTIONS' : {
            # Heed a warning during manage.py migrate runs
            'init_command' : "SET sql_mode='STRICT_ALL_TABLES';",
        },
    }
elif MAW_ENV == 'local':
    DATABASES = {
        # This db will hold users and groups info
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            # The maw1_default_db database will host misc django default data
            'NAME': 'maw1_default_db',
            'USER': MAW_MYSQL_LOCAL_USER,
            'PASSWORD': MAW_MYSQL_LOCAL_PASSWORD,
            'HOST': '127.0.0.1',
            'PORT': '3306',
        },
        'maw1_db_connection': {
            'ENGINE': 'django.db.backends.mysql',
            # The maw1_db database will host hathitrust and probably
            # some other maw apps
            'NAME': 'maw1_db',
            'USER': MAW_MYSQL_LOCAL_USER,
            'PASSWORD': MAW_MYSQL_LOCAL_PASSWORD,
            'HOST': '127.0.0.1',
            'PORT': '3306',
        },
        'lcroyster_connection': {
            'ENGINE': 'django.db.backends.mysql',
            # The maw1_db database will host hathitrust and probably
            # some other maw apps
            'NAME': 'lcroyster1',
            'USER': MAW_MYSQL_LOCAL_USER,
            'PASSWORD': MAW_MYSQL_LOCAL_PASSWORD,
            'HOST': '127.0.0.1',
            'PORT': '3306',
        },
        'hathitrust_connection': {
            'ENGINE': 'django.db.backends.mysql',
            # The maw1_db database will host hathitrust and probably
            # some other maw apps
            'NAME': 'maw1_db',
            'USER': MAW_MYSQL_LOCAL_USER,
            'PASSWORD': MAW_MYSQL_LOCAL_PASSWORD,
            'HOST': '127.0.0.1',
            'PORT': '3306',
        },
        'cuba_libro_connection': {
            'ENGINE': 'django.db.backends.mysql',
            # The maw1_db database will host hathitrust and probably
            # some other maw apps
            'NAME': 'maw1_db',
            'USER': MAW_MYSQL_LOCAL_USER,
            'PASSWORD': MAW_MYSQL_LOCAL_PASSWORD,
            'HOST': '127.0.0.1',
            'PORT': '3306',
        },
    } # END DATABASES
else:
    msg = ("Bad MAW_ENV name='{}' given for user. "
    "Not found in ['local','test','production']".format(MAW_ENV) )
    raise ValueError(msg)

# END ENVIRONMENT DATABSE SETTINGS


DATABASE_ROUTERS = [
    'hathitrust.models.HathiRouter',
    'cuba_libro.models.Cuba_LibroRouter',
    'lcroyster.models.LcroysterRouter',
]


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

from django.urls import reverse_lazy

LOGIN_REDIRECT_URL = "/admin"


## not sure if ckeditor needs this?
SITE_ID = 1
#

####################################
    ##  CKEDITOR CONFIGURATION ##
####################################

CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js'

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = "pillow"

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': None,
    },
}

###################################
