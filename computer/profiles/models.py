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
"""Profiles Django app models."""

import os

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .user_manager import UserManager


def default_unique_visitor_id():
    """Create an unique visitor ID."""
    return "".join(["%02x" % h for h in os.urandom(8)])


def get_avatar_image_path(instance: models.Model, filename: str) -> str:
    """Get image path."""
    return os.path.join(
        "profiles",
        "avatar",
        instance.user.unique_visitor_id + os.path.splitext(filename)[1],
    )


class User(AbstractBaseUser, PermissionsMixin):
    """User."""

    objects = UserManager()
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    email = models.EmailField(unique=True, verbose_name=_("Email"))
    first_name = models.CharField(max_length=256, verbose_name=_("First name"))
    last_name = models.CharField(
        max_length=256, blank=True, null=True, verbose_name=_("Last name")
    )
    date_joined = models.DateTimeField(
        default=timezone.now, verbose_name=_("Date joined")
    )
    is_staff = models.BooleanField(
        _("Staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this site."),
    )
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. Unselect this "
            + "instead of deleting accounts."
        ),
    )
    unique_visitor_id = models.CharField(
        max_length=16,
        default=default_unique_visitor_id,
        unique=True,
        verbose_name=_("Unique visitor ID"),
    )

    def __str__(self) -> str:
        """Name."""
        return self.get_short_name()

    def get_full_name(self) -> str:
        """Get full name of a user."""
        return ("%s %s" % (self.first_name, self.last_name)).strip()

    def get_short_name(self) -> str:
        """Get short name of the user."""
        return self.first_name

    class Meta:
        """Meta."""

        ordering = ("email",)
        verbose_name = _("User")
        verbose_name_plural = _("Users")


class Profile(models.Model):
    """Profile."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        related_name="profile",
        verbose_name=_("User"),
    )
    avatar = models.ImageField(
        upload_to=get_avatar_image_path,
        max_length=150,
        verbose_name=_("Avatar"),
    )
    preferences = models.JSONField(default=dict, verbose_name=_("Preferences"))

    def __str__(self) -> str:
        """Name."""
        return self.user.get_short_name()

    class Meta:
        """Meta."""

        ordering = ("user",)
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")


class NLURequest(models.Model):
    """NLU request."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        blank=True,
        null=True,
        related_name="nlu_requests",
        verbose_name=_("User"),
    )
    params = models.JSONField(default=dict, verbose_name=_("Request parameters"))
    nlu_model_output = models.JSONField(
        default=dict, verbose_name=_("NLU model output")
    )
    intent_output = models.JSONField(default=dict, verbose_name=_("Intent output"))
    answer = models.TextField(verbose_name=_("Answer"))

    def __str__(self) -> str:
        """Name."""
        return (
            f"{self.user.get_short_name() if self.user else 'Anonymous'} "
            + "{self.updated_at}"
        )

    class Meta:
        """Meta."""

        ordering = ("user", "-updated_at")
        verbose_name = _("NLU request")
        verbose_name_plural = _("NLU requests")
