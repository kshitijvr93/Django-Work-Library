from django.conf.urls import url
from django.urls import include, path, re_path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views

#NB: typically this is included from a urls.py with url prefix 'hathitrust/'

urlpatterns = [
    # { May move next 2 lines to use maw_home.views.home later
    re_path(route=r'^$', view=views.home, name='home'),
    path(route=r'home', view=views.home, name='cuba_libro_home'),
    # }
    path(route=r'index', view=views.index, name='index'),

    # { Support for social_django if served from cuba_libro app
    # Note: github would have to register
    #.../cuba_libro/oauth/complete/github for github logins to work
    #and must omment-out namespace='social' in all other url.py files
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    #url(r'^oauth/', include('social_django.urls', namespace='social')),  # <--
    # }
]
