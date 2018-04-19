from django.conf.urls import url
from django.urls import include, path, re_path
from . import views

#NB: typically this is included from a urls.py with url prefix 'hathitrust/'

urlpatterns = [
    re_path(route=r'^$', view=views.home, name='home'),
    path(route=r'home', view=views.home, name='home'),
]
