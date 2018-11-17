"""
Django settings for marshal1 project.

All settings from maw_settings.XXX varaiables must be set in the
django-server-launching OS user's file $MY_SECRETS_FOLDER/maw_settings.py

"""

import os, sys, os.path
MY_SECRETS_FOLDER = 'C:\\Users\\kshit\\MY_SECRETS_FOLDER'
#MY_SECRETS_FOLDER = os.environ['MY_SECRETS_FOLDER']
sys.path.append(os.path.abspath(MY_SECRETS_FOLDER))
print ("Using MY_SECRETS_FOLDER='{}'".format(MY_SECRETS_FOLDER))

# IMPORT SETTINGS FOR MARSHALING APPLICATION WEBSITE (MAW) settings
# from maw_settings import *
import maw_settings

#print("Got maw_settings.MODULES_FOLDER={}"
#  .format(maw_settings.MODULES_FOLDER))
sys.stdout.flush()

sys.path.append(maw_settings.MODULES_FOLDER)
print (f'Using MODULES_FOLDER={maw_settings.MODULES_FOLDER},'
       f' sys.path={sys.path}')
sys.stdout.flush()

# Some MAW extract,translate, load utilities, some others too.
#import etl
print("Using sys.path={}".format(repr(sys.path)))

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
print(f"Using BASE_DIR={BASE_DIR} for this project")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = maw_settings.DJANGO_SECRET_KEY

DEBUG = maw_settings.DJANGO_DEBUG
ALLOWED_HOSTS = maw_settings.DJANGO_ALLOWED_HOSTS
print(f"USING: ALLOWED_HOSTS={ALLOWED_HOSTS}")
#sys.stdout.flush()

# {https://stackoverflow.com/questions/34114427/django-upgrading-to-1-9-error-appregistrynotready-apps-arent-loaded-yet
# may fix apps not ready yet when using multiprocessing
# must add AFTER import maw_settings
#import django
#django.setup()
#}


# Application definition
INSTALLED_APPS = [
    #'maw_home.apps.MawHomeConfig',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_json_widget',
    'django_mptt_admin',
    'django_admin_listfilter_dropdown',
    # 'nested_admin', # Not: use this xor nested_inline
    'nested_inline', # Note: use this xor nested_admin
    'social_django',
    # 'channels',
    'ckeditor',
    'ckeditor_uploader',
    'import_export',
    'mptt',
    # Apps under UF source control
    'dps.apps.DpsConfig',
    'cuba_libro.apps.CubaLibroConfig',
    # Hathtitrust has fkey to dps, so dps precedes above..
    'hathitrust.apps.HathitrustConfig',
    'subject_app.apps.SubjectAppConfig',
    'lcroyster.apps.LcroysterConfig',
    'profile.apps.ProfileConfig',    
    'snow.apps.SnowConfig',
    'submit.apps.SubmitConfig',
]

if DEBUG == False:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': maw_settings.CACHES_DEFAULT_LOCATION,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.clilent.DefaultClient',
            }
        },
    }

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            # Change next line to a maw_setting soon..
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
        },
        "ROUTING": "chat.routing.channel_routing",
    },
}

#{ Settings for app import_export
# https://django-import-export.readthedocs.io/en/latest/installation.html
IMPORT_EXPORT_PERMISSION_CODE = 'add'
IMPORT_EXPORT_USE_TRANSACTIONS = True
#} Settings for app import_export

# Avoid using AUTH_USER_MODEL, rather use get_user_model(), see
# https://wsvincent.com/django-referencing-the-user-model/
# AUTH_USER_MODEL = 'users.CustomUser'

STATIC_URL = '/static/'
STATIC_ROOT = maw_settings.STATIC_ROOT
print(f"STATIC_ROOT={STATIC_ROOT}")
#Set up some static file management.
#See https://docs.djangoproject.com/en/2.1/intro/tutorial06/
#See https://docs.djangoproject.com/en/2.1/ref/settings/
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

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
    'django.contrib.admindocs.middleware.XViewMiddleware',
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
            'USER': maw_settings.TEST_MYSQL_USER,
            'PASSWORD': maw_settings.TEST_MYSQL_PASSWORD,
            'HOST': '10.241.33.139',
            'PORT': '3306',
        } })
elif cuba_libro_env == 'local':
    DATABASES.update({
        'cuba_libro_connection': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'maw1_db',
            'USER': maw_settings.LOCAL_MYSQL_USER,
            'PASSWORD': maw_settings.LOCAL_MYSQL_PASSWORD,
            'HOST': '127.0.0.1',
            'PORT': '3306',
        } })
else:
    msg = (f"ERROR:maw_settings.CUBA_LIBRO_ENV '{maw_settings.CUBA_LIBRO_ENV}'"
        " not implemented.")
    raise ValueError(msg)

# Keep submit  project ENV settings separated for flexibility:
# use try-except to phase-in this code to work with older maw_settings.py files
try:
    dps_env = maw_settings.DPS_ENV
except AttributeError:
    dps_env = ''

print(f"USING: maw_settings.DPS_ENV={dps_env}")

#20180829 - standardize on postgresql for dps database needs
# TODO: create a production psql database  named dps
DPS_UFDC_FOLDER = maw_settings.DPS_UFDC_FOLDER
print(f"settings.py: DPS_UFDC_FOLDER={DPS_UFDC_FOLDER}")
#sys.stdout.flush()

if dps_env == 'test': # Experiment later with this one
    DATABASES.update({'dps_connection' : {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dps',
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
elif dps_env == 'local': # Experiment later with this one
    DATABASES.update({'dps_connection' : {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dps',
        'USER': maw_settings.LOCAL_PSQL_USER,
        'PASSWORD': maw_settings.LOCAL_PSQL_PASSWORD,
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'TIME_ZONE': None,
        },
    })
else:
    #Future: if var django_database_dict_dps exists, do:
    # DATABASES.update({'dps_connection': django_database_dict_dps})
    msg=(f"ERROR:Setting DPS_ENV '{dps_env}' not implemented.")
    raise ValueError(msg)

# Ensure that some apps (dps, snow, submit for now)
# that do inter-app table joins and foreign
# key references use the same database connection.

dbc = DATABASES['dps_connection']
DATABASES['snow_connection'] = dbc
DATABASES['submit_connection'] = dbc

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

# Start checks for hathitrust_env settings
hathitrust_env = maw_settings.HATHITRUST_ENV
if hathitrust_env == 'test':
    DATABASES.update({
        # This db will hold users and groups info
        'hathitrust_connection': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'dps',
            'USER': maw_settings.TEST_PSQL_USER,
            'PASSWORD': maw_settings.TEST_PSQL_PASSWORD,
            'HOST': '10.241.33.139',
            'PORT': '5432',
            'TIME_ZONE': None,
        },
    }) # hathitrust_env = 'test'
elif hathitrust_env == 'local':
    DATABASES.update({
        'hathitrust_connection': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'dps',
            'USER': maw_settings.LOCAL_PSQL_USER,
            'PASSWORD': maw_settings.LOCAL_PSQL_PASSWORD,
            'HOST': '127.0.0.1',
            'PORT': '5432',
            'TIME_ZONE': None,
        },
    }) # END ENV LOCAL DATABASES
else:
    msg = ( f"Bad maw_settings.HATHITRUST_ENV name='{hathitrust_env}'. "
      "Not found in ['xlocal','test']" )
    raise ValueError(msg)
# END Checks for hathitrust_env


# Start checks for hathitrust_env settings
subject_app_env = maw_settings.SUBJECT_APP_ENV
if subject_app_env == 'test':
    DATABASES.update({
        # This db will hold users and groups info
        'subject_app_connection': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'dps',
            'USER': maw_settings.TEST_PSQL_USER,
            'PASSWORD': maw_settings.TEST_PSQL_PASSWORD,
            'HOST': '10.241.33.139',
            'PORT': '5432',
            'TIME_ZONE': None,
        },
    }) # hathitrust_env = 'test'
elif subject_app_env == 'local':
    DATABASES.update({
        'subject_app_connection': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'dps',
            'USER': maw_settings.LOCAL_PSQL_USER,
            'PASSWORD': maw_settings.LOCAL_PSQL_PASSWORD,
            'HOST': '127.0.0.1',
            'PORT': '5432',
            'TIME_ZONE': None,
        },
    }) # END ENV LOCAL DATABASES
else:
    msg = ( f"Bad maw_settings.SUBJECT_APP_ENV name='{subject_app_env}'. "
      "Not found in ['xlocal','test']" )
    raise ValueError(msg)
# END Checks for hathitrust_env

if maw_settings.ENV == 'test':
    DATABASES.update({
        # This db will hold users and groups info
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'maw1_default_db',
            'USER': maw_settings.TEST_MYSQL_USER,
            'PASSWORD': maw_settings.TEST_MYSQL_PASSWORD,
            'HOST': '10.241.33.139',
            'PORT': '3306',
        },
        'maw1_db_connection': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'maw1_db_test',
            'USER': maw_settings.TEST_MYSQL_USER,
            'PASSWORD': maw_settings.TEST_MYSQL_PASSWORD,
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
            'USER': maw_settings.LOCAL_MYSQL_USER,
            'PASSWORD': maw_settings.LOCAL_MYSQL_PASSWORD,
            'HOST': '127.0.0.1',
            'PORT': '3306',
        },
        'maw1_db_connection': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'maw1_db',
            'USER': maw_settings.LOCAL_MYSQL_USER,
            'PASSWORD': maw_settings.LOCAL_MYSQL_PASSWORD,
            'HOST': '127.0.0.1',
            'PORT': '3306',
        },
    }) # END ENV LOCAL DATABASES
else:
    msg = ("Bad maw_settings.ENV name='{}' given for user. "
    "Not found in ['local','test']".format(maw_settings.ENV) )
    raise ValueError(msg)

# END some settings dependent on maw_settings.ENV

# END ENVIRONMENT DATABASE SETTINGS

DATABASE_ROUTERS = [
    'cuba_libro.models.Cuba_LibroRouter',
    'dps.models.DpsRouter',
    'hathitrust.models.HathiRouter', 
    'subject_app.models.SubjectAppRouter',   
    'lcroyster.models.LcroysterRouter',
    'snow.models.SnowRouter',
    'submit.models.SubmitRouter',
]

# At server startup, print the databases in use
#
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

LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
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

print(f"BASE_DIR={BASE_DIR}")
# Do NOT tack on the last 'marshal1' here, rather use it as the
# first part of the 'url' in templates
STATICFILES_DIRS = [ os.path.join(
    BASE_DIR, 'static',
    ), ]

print(f'Using STATICFILES_DIRS={STATICFILES_DIRS}')

###################################
