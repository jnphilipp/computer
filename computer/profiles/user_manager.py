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
"""Profiles Django app user manager."""

from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """A custom user manager to deal with emails as unique identifiers for auth."""

    def _create_user(self, email, password, **extra_fields):
        """Creates and saves a user with the given email and password."""
        if not email:
            raise ValueError(_("The email must be set."))
        if "first_name" not in extra_fields:
            extra_fields["first_name"] = email
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        from .models import Profile

        Profile.objects.create(user=user)

        return user

    def create_superuser(self, email, password, **extra_fields):
        """Creates and saves a super user with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self._create_user(email, password, **extra_fields)
