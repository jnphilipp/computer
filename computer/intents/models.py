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
"""Intents Django app models."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Intent(models.Model):
    """Intent model."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    name = models.CharField(max_length=256, unique=True, verbose_name=_("Name"))
    answers = models.ManyToManyField(
        "texts.Answer", blank=True, related_name="intents", verbose_name=_("Answers")
    )

    def __str__(self) -> str:
        """Name."""
        return self.name

    def to_dict(self) -> dict[str, str | list[dict]]:
        """Convert this model to a dictionary."""
        return {
            "name": self.name,
            "answers": [answer.to_dict() for answer in self.answers.all()],
        }

    class Meta:
        """Meta."""

        ordering = ("name",)
        verbose_name = _("Intent")
        verbose_name_plural = _("Intents")
