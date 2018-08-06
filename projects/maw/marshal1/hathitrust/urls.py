from django.conf.urls import url
from django.urls import include, path, re_path
from . import views

#NB: typically this is included from a urls.py with url prefix 'hathitrust/'
urlpatterns = [
    re_path(route=r'^$', view=views.index, name='index'),
    path(route=r'index', view=views.index, name='index'),
    re_path(r'^upload/$',view=views.file_upload, name='file_upload'),
    re_path(r'^upload/success/(?P<file_id>\d+)/$',view=views.upload_success,
        name='upload_success'),
    re_path(r'^download/(?P<file_id>\d+)/$',view=views.file_download,
        name='file_download'),
    re_path(r'^public/(?P<file_id>\d+)/$',view=views.public,
        name='public'),
    re_path(r'^testone/$',view=views.testone,
        name='testone'),
]
