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
"""Profiles Django app config."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProfilesConfig(AppConfig):
    """Profiles app cofnig."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "profiles"
    verbose_name = _("Profile")
    verbose_name_plural = _("Profiles")
