# -*- coding: utf-8 -*-

from django.urls import path
from .. import views


app_name = 'api'
urlpatterns = [
    path(r'v1/nlu/', views.nlu),
]
