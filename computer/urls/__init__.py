# -*- coding: utf-8 -*-
"""computer URL Configuration

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

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import RedirectView

from .. import views


admin.site.site_header = _('computer administration')


urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('admin/', admin.site.urls),
    path('api/', include('computer.urls.api')),
    path('profiles/', include('profiles.urls')),

    path('favicon.ico', RedirectView.as_view(url='/static/images/icon.png')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
