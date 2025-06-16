# Copyright (C) 2017-2025 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
#
# Computer - personal assistant.
#
# This file is part of computer.
#
# computer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# computer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with computer. If not, see <http://www.gnu.org/licenses/>
"""Profiles Django app urls."""


from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views


app_name = "profiles"
urlpatterns = [
    path("", views.ProfileView.as_view(), name="profile"),
    # path('password/', views.password_change, name='password_change'),
    # path('password/done/', views.password_change_done, name='password_change_done'),
    path(
        "password/reset/",
        auth_views.PasswordResetView.as_view(
            template_name="profiles/password_reset_form.html"
        ),
        name="password_reset",
    ),
    path(
        "password/reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="profiles/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password/reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="profiles/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset_confirm.html",
        ),
        name="password_reset_confirm",
    ),
    path(
        "signin/",
        auth_views.LoginView.as_view(template_name="profiles/signin.html"),
        name="signin",
    ),
    path(
        "signout/",
        auth_views.LogoutView.as_view(template_name="profiles/signout.html"),
        name="signout",
    ),
]
