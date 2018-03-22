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

# Set admin site display title
admin.site.site_header = "UF Libraries Marshaling Apps Web (MAW) Admin"
urlpatterns = [
    # path('', include('maw_home.urls')),
    # path('home/', include('maw_home.urls')),
    path('admin/', admin.site.urls),
    path('am4ir/', include('hathitrust.urls')),
    path('aspace/', include('hathitrust.urls')),
    path('cattleman/', include('hathitrust.urls')),
    path('cuba_libro/', include('hathitrust.urls')),
    path('elsevier/', include('hathitrust.urls')),
    path('hathitrust/', include('hathitrust.urls')),
    path('ifas_citations/', include('hathitrust.urls')),
    path('lcroyster/', include('lcroyster.urls')),
    path('rvp/', include('hathitrust.urls')),
]
