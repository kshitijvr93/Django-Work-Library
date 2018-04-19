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

# Set admin site display title
admin.site.site_header = "UF Libraries Marshaling Apps Web (MAW) Admin"
urlpatterns = [
    # path('', include('maw_home.urls')),
    # path('home/', include('maw_home.urls')),
    path('am4ir/', include('hathitrust.urls')),
    path('admin/', admin.site.urls),
    path('am4ir/', include('hathitrust.urls')),
    path('aspace/', include('hathitrust.urls')),
    path('cattleman/', include('hathitrust.urls')),
    path('cuba_libro/', include('cuba_libro.urls')),
    path('elsevier/', include('hathitrust.urls')),
    path('hathitrust/', include('hathitrust.urls')),
    path('ifas_citations/', include('hathitrust.urls')),
    path('lcroyster/', include('lcroyster.urls')),
    path('oauth/', include('social_django.urls',namespace='social')),
    path('rvp/', include('hathitrust.urls')),
    #re_path(r'^$', include('maw_home.urls')),
    path('login/', auth_views.login, name='login'),
    path('logout/', auth_views.logout, name='logout'),
]
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'home'
