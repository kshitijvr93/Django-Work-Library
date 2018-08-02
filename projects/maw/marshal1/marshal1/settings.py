"""
Django settings for marshal1 project.

All settings from maw_settings.XXX varaiables must be set in the
django-server-launching OS user's file $MY_SECRETS_FOLDER/maw_settings.py

"""

import os, sys, os.path
MY_SECRETS_FOLDER = os.environ['MY_SECRETS_FOLDER']
sys.path.append(os.path.abspath(MY_SECRETS_FOLDER))
print ("Using MY_SECRETS_FOLDER='{}'".format(MY_SECRETS_FOLDER))

# IMPORT SETTINGS FOR MARSHALING APPLICATION WEBSITE (MAW) settings
#from maw_settings import *
import maw_settings

#print("Got maw_settings.MODULES_FOLDER={}"
#  .format(maw_settings.MODULES_FOLDER))
#sys.stdout.flush()

sys.path.append(maw_settings.MODULES_FOLDER)

# Some MAW extract,translate, load utilities, some others too.
#import etl
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

DEBUG = maw_settings.DJANGO_DEBUG
ALLOWED_HOSTS = maw_settings.DJANGO_ALLOWED_HOSTS
print(f"USING: ALLOWED_HOSTS={ALLOWED_HOSTS}")
sys.stdout.flush()

# Application definition

INSTALLED_APPS = [
    #'maw_home.apps.MawHomeConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_json_widget',
    'django_mptt_admin',
    # 'nested_admin', # Not: use this xor nested_inline
    'nested_inline', # Note: use this xor nested_admin
    'social_django',
    'ckeditor',
    'ckeditor_uploader',
    # Apps under UF source control
    'cuba_libro.apps.CubaLibroConfig',
    'hathitrust.apps.HathitrustConfig',
    'lcroyster.apps.LcroysterConfig',
    'mptt',
    'snow.apps.SnowConfig',
    'submit.apps.SubmitConfig',
]

STATIC_URL = '/static/'

MEDIA_ROOT = maw_settings.MAW_ABSOLUTE_PATH_MEDIA_ROOT
print("USING: maw_settings.MAW_ABSOLUTE_PATH_MEDIA_ROOT={}"
    .format(maw_settings.MAW_ABSOLUTE_PATH_MEDIA_ROOT))

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
        # see:
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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
    'social_core.backends.open_id.OpenIdAuth',
    #'social_core.backends.google.GoogleOpenID',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.facebook.FacebookOAuth2',

    'django.contrib.auth.backends.ModelBackend',
)

#{ AuthAlreadyAssociated - trying this workaround
#see https://stackoverflow.com/questions/13018147/authalreadyassociated-exception-in-django-social-auth
#and see 20170314 answer
# Seems to work if only using googleOAuth2, but then twitter and github logins
# and relogins fail..
# If comment this out, google-OAuth2 relogins give AuthAlreadyAssociated error,
#but relogins for both twitter and github go OK with no issues...
#
'''
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.user.user_details',
)
'''
#}

SOCIAL_AUTH_GITHUB_KEY = maw_settings.GITHUB_CLIENT_ID
SOCIAL_AUTH_GITHUB_SECRET = maw_settings.GITHUB_CLIENT_SECRET
SOCIAL_AUTH_TWITTER_KEY = maw_settings.SOCIAL_AUTH_TWITTER_KEY
SOCIAL_AUTH_TWITTER_SECRET = maw_settings.SOCIAL_AUTH_TWITTER_SECRET
SOCIAL_AUTH_FACEBOOK_KEY=maw_settings.SOCIAL_AUTH_FACEBOOK_KEY
SOCIAL_AUTH_FACEBOOK_SECRET=maw_settings.SOCIAL_AUTH_FACEBOOK_SECRET

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=maw_settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=maw_settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET

#{ See: https://stackoverflow.com/questions/21968004/how-to-get-user-email-with-python-social-auth-with-facebook-and-save-it

SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id,name,email',
}
#}

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

DATABASES = {}

# cuba_libra env
cuba_libro_env = maw_settings.CUBA_LIBRO_ENV

if cuba_libro_env == 'test':
    DATABASES.update({
        'cuba_libro_connection': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'maw1_db_test',
            'USER': maw_settings.ARCHCOLL_MYSQL_USER,
            'PASSWORD': maw_settings.ARCHCOLL_MYSQL_PASSWORD,
            'HOST': '10.241.33.139',
            'PORT': '3306',
        } })
elif cuba_libro_env == 'local':
    DATABASES.update({
        'cuba_libro_connection': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'maw1_db',
            'USER': maw_settings.MYSQL_LOCAL_USER,
            'PASSWORD': maw_settings.MYSQL_LOCAL_PASSWORD,
            'HOST': '127.0.0.1',
            'PORT': '3306',
        } })
else:
    msg = (f"ERROR:maw_settings.CUBA_LIBRO_ENV '{maw_settings.CUBA_LIBRO_ENV}'"
        " not implemented.")
    raise ValueError(msg)

# Keep submit  project ENV settings separated for flexibility:

submit_env = maw_settings.SUBMIT_ENV
print("USING: maw_settings.SUBMIT_ENV={}"
    .format(maw_settings.SUBMIT_ENV))
sys.stdout.flush()

if submit_env == 'test2': # Experiment later with this one
    DATABASES.update({'submit_connection' : {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'submit_test',
        'USER': maw_settings.TEST_PSQL_USER,
        'PASSWORD': maw_settings.TEST_PSQL_PASSWORD,
        'HOST': '10.241.33.139',
        'PORT': '5432',
        'TIME_ZONE': None,
        #'OPTIONS' : {
        #    # Heed a warning during manage.py migrate runs
        #    'init_command' : "SET sql_mode='STRICT_ALL_TABLES';",
        #    },
        },
    })
elif submit_env == 'test':
    # Use this for local tests on mysql database
    DATABASES.update({'submit_connection' : {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'submit',
        'USER': maw_settings.TEST_MYSQL_SUBMIT_USER,
        'PASSWORD': maw_settings.TEST_MYSQL_SUBMIT_PASSWORD,
        'HOST': '10.241.33.139',
        'PORT': '5432',
        'TIME_ZONE': None,
        },
    })
elif submit_env == 'local':
    # Use this for local tests on mysql database
    DATABASES.update({'submit_connection' : {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'submit',
        'USER': maw_settings.LOCAL_MYSQL_SUBMIT_USER,
        'PASSWORD': maw_settings.LOCAL_MYSQL_SUBMIT_PASSWORD,
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'TIME_ZONE': None,
        },
    })
else:
    msg="ERROR:Setting SUBMIT_ENV '{}' not implemented.".format(submit_env)
    raise ValueError(msg)

# For app "snow"  - stick with submit database too. Will need some joins
# among submit and snow tables
DATABASES['snow_connection'] = DATABASES['submit_connection']
d = DATABASES['snow_connection']
print("CONNECTION snow_connection: engine={}, dbname={}"
  .format(d['ENGINE'], d['NAME']))
sys.stdout.flush()

lcroyster_env = maw_settings.LCROYSTER_ENV
if lcroyster_env == 'production':
    DATABASES.update({'lcroyster_connection' : {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'LCRoysterproject',
        'USER': 'LCRoysterproject',
        'PASSWORD': maw_settings.OYSTER_MYSQL_PRODUCTION_PASSWORD,
        #'HOST': 'ict-prod-hosting02.mysql.osg.ufl.edu',
        #'PORT': '3354',
        'HOST': 'ict-prod-hosting05.mysql.osg.ufl.edu',
        'PORT': '3359',
        'TIME_ZONE': None,
        'OPTIONS' : {
            # Heed a warning during manage.py migrate runs
            'init_command' : "SET sql_mode='STRICT_ALL_TABLES';",
            },
        },
    })
elif lcroyster_env == 'test':
    DATABASES.update({'lcroyster_connection': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lcroyster1_test',
        'USER': maw_settings.LCROYSTER_TEST_MYSQL_USER,
        'PASSWORD': maw_settings.LCROYSTER_TEST_MYSQL_PASSWORD,
        'HOST': '10.241.33.139',
        'PORT': '3306',
        'TIME_ZONE': None,
        'OPTIONS' : {
            # Heed a warning during manage.py migrate runs
            'init_command' : "SET sql_mode='STRICT_ALL_TABLES';",
            },
        },
    })
elif lcroyster_env == 'local':
    DATABASES.update({'lcroyster_connection' : {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lcroyster1',
        'USER': maw_settings.LCROYSTER_LOCAL_MYSQL_USER,
        'PASSWORD': maw_settings.LCROYSTER_LOCAL_MYSQL_PASSWORD,
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'TIME_ZONE': None,
        'OPTIONS' : {
            # Heed a warning during manage.py migrate runs
            'init_command' : "SET sql_mode='STRICT_ALL_TABLES';",
            },
        },
    })
else:
    msg="ERROR:Setting LCROYSTER_ENV is not in ['production','local','test']"
    raise ValueError(msg)

# END LCROYSTER_ENV sensitive settings


if maw_settings.ENV == 'test':
    DATABASES.update({
        # This db will hold users and groups info
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            # The maw1_default_db database will host misc django default data
            'NAME': 'maw1_default_db',
            'USER': maw_settings.MYSQL_ARCHCOLL_TEST_USER,
            'PASSWORD': maw_settings.MYSQL_ARCHCOLL_TEST_PASSWORD,
            'HOST': '10.241.33.139',
            'PORT': '3306',
        },
        'maw1_db_connection': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'maw1_db_test',
            'USER': maw_settings.MYSQL_ARCHCOLL_TEST_USER,
            'PASSWORD': maw_settings.MYSQL_ARCHCOLL_TEST_PASSWORD,
            'HOST': '10.241.33.139',
            'PORT': '3306',
        },
        'hathitrust_connection': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'maw1_db_test',
            'USER': maw_settings.MYSQL_ARCHCOLL_TEST_USER,
            'PASSWORD': maw_settings.MYSQL_ARCHCOLL_TEST_PASSWORD,
            'HOST': '10.241.33.139',
            'PORT': '3306',
        },
    }) # maw_settings.ENV = 'test'
elif maw_settings.ENV == 'local':
    DATABASES.update({
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            # The maw1_default_db database will host misc django default
            # data
            'NAME': 'maw1_default_db',
            'USER': maw_settings.MYSQL_LOCAL_USER,
            'PASSWORD': maw_settings.MYSQL_LOCAL_PASSWORD,
            'HOST': '127.0.0.1',
            'PORT': '3306',
        },
        'maw1_db_connection': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'maw1_db',
            'USER': maw_settings.MYSQL_LOCAL_USER,
            'PASSWORD': maw_settings.MYSQL_LOCAL_PASSWORD,
            'HOST': '127.0.0.1',
            'PORT': '3306',
        },
        'hathitrust_connection': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'maw1_db',
            'USER': maw_settings.MYSQL_LOCAL_USER,
            'PASSWORD': maw_settings.MYSQL_LOCAL_PASSWORD,
            'HOST': '127.0.0.1',
            'PORT': '3306',
        },
    }) # END ENV LOCAL DATABASES
else:
    msg = ("Bad maw_settings.ENV name='{}' given for user. "
    "Not found in ['local','test','production']".format(maw_settings.ENV) )
    raise ValueError(msg)

# END ENVIRONMENT DATABASE SETTINGS

DATABASE_ROUTERS = [
    'cuba_libro.models.Cuba_LibroRouter',
    'hathitrust.models.HathiRouter',
    'lcroyster.models.LcroysterRouter',
    'snow.models.SnowRouter',
    'submit.models.SubmitRouter',
]

for cname, cdict in DATABASES.items():
    print ("\nCONNECTION NAME='{}'".format(cname))
    for key, val in cdict.items():
        if (key == 'PASSWORD'):
            continue
        print("\t{}={}".format(key,val))

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
#{See https://fosstack.com/how-to-add-google-authentication-in-django/
# These should be set here in settings.py rather than any urls.py

LOGIN_REDIRECT_URL = "/admin"
LOGOUT_REDIRECT_URL = "/login"
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
#}

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
