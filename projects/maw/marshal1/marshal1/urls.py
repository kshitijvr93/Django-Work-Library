"""marshal1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, path, re_path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views
from django.conf.urls import url
from django.views.generic.base import TemplateView

# Set admin site display title
admin.site.site_header = "UF Libraries Marshaling Apps Web (MAW) Admin"
urlpatterns = [
    # path('', include('maw_home.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    # path('home/', include('maw_home.urls')),
    path('am4ir/', include('hathitrust.urls')),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('am4ir/', include('hathitrust.urls')),
    path('aspace/', include('hathitrust.urls')),
    path('cattleman/', include('hathitrust.urls')),
    #20180817 - I told google oauth2 login to redirect to cuba_libro,
    #but just tweak next now , because prefer home now, but should change google
    #account project setting later to go to home
    #path('cuba_libro/', include('cuba_libro.urls')),
    #path('cuba_libro/', TemplateView.as_view(template_name='home.html')),
    path('cuba_libro/', include('cuba_libro.urls')),
    path('dps/', include('dps.urls')),
    path('elsevier/', include('hathitrust.urls')),
    path('hathitrust/', include('hathitrust.urls')),
    path('ifas_citations/', include('hathitrust.urls')),
    path('lcroyster/', include('lcroyster.urls')),

    #older django 2.0 line
    #path('login/', auth_views.login, name='login'),
    # new to django 2.1
    path('login/', auth_views.LoginView.as_view(), name='login'),

    #path('logout/', auth_views.logout, name='logout'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('oauth/', include('social_django.urls',namespace='social')),
    #path('login/', auth_views.login, name='login'),
    #path('logout/', auth_views.logout, name='logout'),
    #path('logout-then-login/', auth_views.logout_then_login,
    #    name='logout-then-login'),
    #Add as experiment ..
    #path('complete/', include('cuba_libro.urls')),
    path('rvp/', include('hathitrust.urls')),
    #re_path(r'^$', include('maw_home.urls')),
    #path('login/', auth_views.login, name='login'),
    #path('logout/', auth_views.logout, name='logout'),

    #url(r'^login/$', auth_views.login, name='login'),
    # path('successfully_logged_out/', views.successfully_logged_out),
    #url(r'^logout/$', auth_views.logout, name='logout',
    #{'next_page':'login/'} ),

    #url(r'^admin/', admin.site.urls),
]
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
