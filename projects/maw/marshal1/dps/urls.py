from django.conf.urls import url
from django.urls import include, path, re_path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views

#NB: typically this is included from a urls.py with url prefix 'hathitrust/'

urlpatterns = [
    # re_path(route=r'^$', view=views.home, name='home'),
    path(route=r'out_mets', view=views.out_mets, name='out_mets'),
    path(route=r'out_mets', view=views.out_mets, name='input_xis'),
    path(route=r'add_topic_terms', view=views.topic_terms, name='input_xis'),
]
