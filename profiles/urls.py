# -*- coding: utf-8 -*-

from django.urls import path
from . import views


app_name = 'profiles'
urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),

    path('password/', views.password_change, name='password_change'),
    path('password/done/', views.password_change_done,
         name='password_change_done'),
    path('password/reset/', views.password_reset, name='password_reset'),
    path('password/reset/done/', views.password_reset_done,
         name='password_reset_done'),
    path('password/reset/complete/', views.password_reset_complete,
         name='password_reset_complete'),
    path('password/reset/confirm/<uidb64>/<token>/',
         views.password_reset_confirm, name='password_reset_confirm'),

    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('signup/', views.signup, name='signup'),
]
