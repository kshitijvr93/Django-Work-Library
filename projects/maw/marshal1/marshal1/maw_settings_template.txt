# This is file maw_settings.py, written in Python.
#
# The developer must have an environment variable named MY_SECRETS
# And that variable must have the path of the folder containing this file,
# in the same format that
# the host operating system uses to express folder path names.
#
# This file must be kept in the user my_secrets folder,
# which folder must also have an empty file named __init__.py
#
# This file is used by the MAW django project, and the variable names are
# required for use by that project's settings.py file.
# All developer passwords must be in THIS file, plus a MAW_ENV variable that
# should be set to 'local' for developers working on their own host machine.
#
# This file must never be put in the git project directory, because that would
# make your secret passwords available to others, which is a violation of
# best security practices.
#
# The settings are a mix of strictly secrets, like passwords and varibles with "SECRET" in
# their names, and other user-customizable settings.

# MAW_ABSOLUTE_PATH_MEDIA_ROOT='C:\\rvp\\git\\citrus\\projects\\maw\\marshal1\\media_root'
MAW_ABSOLUTE_PATH_MEDIA_ROOT='{maw_absolute_path_media_root}'

#ENV = 'local'
ENV = '{my_env_for_webserver}'

#MYSQL_LOCAL_USER='podengo'
MYSQL_LOCAL_USER='{my_mysql_local_user}'
#MYSQL_LOCAL_PASSWORD='xxxxx'
MYSQL_LOCAL_PASSWORD='{my_mysql_local_password}'

#MYSQL_TEST_USER='podengo'
MYSQL_TEST_USER='{my_mysql_test_user}'
#MYSQL_TEST_PASSWORD='xxxxx'
MYSQL_TEST_PASSWORD='{my_mysql_test_password}'

MYSQL_ARCHCOLL_USER='rvp'
#MYSQL_ARCHCOLL_USER='my_mysql_archcoll_user'
#MYSQL_ARCHCOLL_PASSWORD='xxxxx'
MYSQL_ARCHCOLL_PASSWORD='{my_mysql_archcoll_password}'

# LCROYSTER_ENV = 'production'
# LCROYSTER_ENV = 'test'
LCROYSTER_ENV = 'my_lcroyster_env'

LCROYSTER_TEST_MYSQL_USER=MYSQL_ARCHCOLL_USER
LCROYSTER_TEST_MYSQL_PASSWORD=MYSQL_ARCHCOLL_PASSWORD

# LCROYSTER_ENV = 'local'
# LCROYSTER_ENV = 'test'
# LCROYSTER_ENV = 'production'
LCROYSTER_ENV = 'local'

LCROYSTER_LOCAL_MYSQL_USER = MYSQL_LOCAL_USER
LCROYSTER_LOCAL_MYSQL_PASSWORD = MYSQL_LOCAL_PASSWORD

SUBMIT_ENV = 'test'
SUBMIT_USER = 'maw'
#SUBMIT_USER = '{my_submit_user}'
SUBMIT_TEST_PASSWORD = 'xxxxx'

# May need a per-app ENV - may want to test some in prod and others in local or test, etc.
# Only used for ENV of 'production'
# OYSTER_MYSQL_PRODUCTION_PASSWORD = 'abcdef'
OYSTER_MYSQL_PRODUCTION_PASSWORD = '{my_oyster_production_password}'

# some applications that also depend on the above secret passwords.
# applications depends on where your MAW git repo is installed

#MODULES_FOLDER = 'C:\\rvp\\git\\citrus\\modules'
MODULES_FOLDER = 'my_source_machine_module_folder'

GITHUB_CLIENT_ID='930806d28d17954bdb2d'
#GITHUB_CLIENT_SECRET='abcdefhijklmnopqrstuvwxyz'
GITHUB_CLIENT_SECRET='{my_github_client_secret}'

SOCIAL_AUTH_TWITTER_KEY = 'rbonQDOorBi94HkCiaO5fhfeP'
SOCIAL_AUTH_TWITTER_SECRET = 'alphabetsoup'
SOCIAL_AUTH_TWITTER_SECRET = 'my_twitter_secret_soup'

SOCIAL_AUTH_FACEBOOK_KEY='240994606641311'
# SOCIAL_AUTH_FACEBOOK_SECRET='secret soup'
SOCIAL_AUTH_FACEBOOK_SECRET='{my_facebook_secret_soup}'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=('50296076588-bda5otvmq85btcl9mvb5aidpmuruigab'
  '.apps.googleusercontent.com')
#SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET='kCv9axH1qBAjYlbwYBmErIwl'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET='{my_google_secret_soup}'

# more maw_settings.py for lcroyster import application mainly
# Test configs of lcroyster stuff for import_sensor_data.py program
# NEXT SECTION IS FOR IFAS USERS to run the LCROYSTER IMPORT PROGRAM:

my_project_params = {

    'lcroyster': {
        'sensor_observations_input_folder' :
             'T:\\WEC\\Groups\\Oyster Project\\project_task\\'
             't7_data_management\\wq\\data\\new_data\\',

        'database_connections' : {
            # NOTE: DB connection name used by import_buoy_sensor_data.py
            # is 'lcroyster'. Others here are placeholders for copy-pasting.

            'lcroyster' : {
                # Note driver mysqldb requires "include mysqlclient"
                'dialect': 'mysql',
                'driver': 'mysqldb',
                # 'user': 'podengo',
                'user': '{my_lcroyster_database_user_name}',
                # 'password': 'password',
                'password': '{my_data_base_password',
                'host': '127.0.0.1',
                'port': '3306',
                'dbname' : 'lcroyster1',
                # NOTE: MUST SET utf8 on connections!
                'charset': 'utf8',
                'format' : (
                  '{dialect}+{driver}://{user}:{password}@'
                  '{host}:{port}/{dbname}?charset={charset}'),
                 },
            'lcroyster_local' : {
                # Note driver mysqldb requires "include mysqlclient"
                'dialect': 'mysql',
                'driver': 'mysqldb',
                # 'user': 'podengo',
                'user': '{my_local_lcroyster1_database_user_name}',
                # 'password': 'password',
                'password': '{my_lcroyster_local_data_base_password',
                'host': '127.0.0.1',
                'port': '3306',
                'dbname' : 'lcroyster1',
                # NOTE: MUST SET utf8 on connections!
                'charset': 'utf8',
                'format' : (
                  '{dialect}+{driver}://{user}:{password}@'
                  '{host}:{port}/{dbname}?charset={charset}'),
                 },
            'lcroyster_production': {
                # Note driver mysqldb requires "import mysqlclient"
                'dialect': 'mysql',
                'driver': 'mysqldb',
                #'user': 'LCRoysterproject',
                'user': 'LCRoysterproject',
                'password': OYSTER_MYSQL_PRODUCTION_PASSWORD,
                'host': 'ict-prod-hosting05.mysql.osg.ufl.edu',
                'port': '3359',
                'dbname' : 'LCRoysterproject',
                # NOTE: MUST SET utf8 on connections!
                'charset': 'utf8',
                'format' : (
                  '{dialect}+{driver}://{user}:{password}@'
                  '{host}:{port}/{dbname}?charset={charset}'),
                 }, # end settings for lcroyster production database
            }, # end database_connections
        }, # end project lcroyster settings
    } # end my_project_params
