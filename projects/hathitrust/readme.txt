This 'hathitrust' project was assigned to me in August 2017.
See .../docs/features.txt for info on the feature set, some of which this code under this folder hierarchy will implement.

See .../docs/architecture.txt for architecture used

Running a development server:
Go to subfolder marshal1, and in a shell issue
a cli command:

For linux bash shell:
  $ workon py36 #to make sure you are running python 3.6
  $ python manage.py runserver

OR for windows with python 3.6 installed as the default python,
and also from a terminal in that folder:
  $ winpty python.exe manage.py runserver

Then in a local browser, try: 127.0.0.1:8000/admin


and see also in folder ...marshal1/hathtrust urls.py and subfolders
to see urls that are handled by the django website code
that you may test from the browser location field.
