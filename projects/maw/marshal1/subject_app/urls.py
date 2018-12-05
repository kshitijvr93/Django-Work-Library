from django.conf.urls import url
from django.urls import include, path, re_path
from . import views

#NB: typically this is included from a urls.py with url prefix 'subject_app/'
urlpatterns = [
    path(route='', view=views.subject_api, name='subject_api_request'),
    
]
