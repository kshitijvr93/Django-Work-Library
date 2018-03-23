"""
Django settings for marshal1 project.

Generated by 'django-admin startproject' using Django 1.11.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

APPEND_SLAH = True
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
    'hathitrust.apps.HathitrustConfig',
    'cuba_libro.apps.CubaLibroConfig',
    'maw_home.apps.MawHomeConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

STATIC_URL = '/static/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'marshal1.urls'

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

WSGI_APPLICATION = 'marshal1.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DB_ENGINE_BACKENDS_STANDARD=['sqlite3','postgresql','mysql','oracle']

# NB: Databases is really a dictionary of connecton name keys, and each
# value is a dictionary of django-reserved names to designate connecton info to
# a particular databse.
#
DATABASES = {
    # This db will hold users and groups info
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # The maw1_default_db database will host misc django default data
        'NAME': 'maw1_default_db',
        'USER': 'podengo',
        'PASSWORD': '20MY18sql!',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
    'uflib_oyster_db': {
    },
    'maw1_db_connection': {
        'ENGINE': 'django.db.backends.mysql',
        # The maw1_db database will host hathitrust and probably
        # some other maw apps
        'NAME': 'maw1_db',
        'USER': 'podengo',
        'PASSWORD': '20MY18sql!',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
    'hathitrust_connection': {
        'ENGINE': 'django.db.backends.mysql',
        # The maw1_db database will host hathitrust and probably
        # some other maw apps
        'NAME': 'maw1_db',
        'USER': 'podengo',
        'PASSWORD': '20MY18sql!',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
    'cuba_libro_connection': {
        'ENGINE': 'django.db.backends.mysql',
        # The maw1_db database will host hathitrust and probably
        # some other maw apps
        'NAME': 'maw1_db',
        'USER': 'podengo',
        'PASSWORD': '20MY18sql!',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
}

'''
    'lcroyster_prod_connection': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'LCRoysterproject',
        'USER': 'LCRoysterproject',
        'PASSWORD': 'HLLV6Pske0vTzhIZfSya',
        'HOST': 'ict-prod-hosting02.mysql.osg.ufl.edu',
        'PORT': '3354',
        'OPTIONS' : {
            # Heed a warning during manage.py migrate runs
            'init_command' : "SET sql_mode='STRICT_ALL_TABLES';",
        },
    },
'''

DATABASE_ROUTERS = [
    'hathitrust.models.HathiRouter',
    'cuba_libro.models.Cuba_LibroRouter',
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
