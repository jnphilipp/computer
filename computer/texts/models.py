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
"""Texts Django app models."""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Entity(models.Model):
    """Entity model."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    name = models.CharField(max_length=1024, unique=True, verbose_name=_("Name"))
    parent = models.ForeignKey(
        "Entity",
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="children",
        verbose_name=_("Parent"),
    )

    def __str__(self) -> str:
        """Name."""
        return self.name

    class Meta:
        """Meta."""

        ordering = ("name",)
        verbose_name = _("Entity")
        verbose_name_plural = _("Entities")


class Trigger(models.Model):
    """Trigger model."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    text = models.CharField(max_length=1024, verbose_name=_("Text"))
    intent = models.ForeignKey(
        "intents.Intent",
        models.CASCADE,
        related_name="triggers",
        verbose_name=_("Intent"),
    )
    language = models.CharField(
        max_length=10, choices=settings.LANGUAGES, verbose_name=_("Language")
    )

    def to_dict(self) -> dict[str, str | dict]:
        """Convert this model to a dictionary."""
        return {
            "text": self.text,
            "language": self.language,
            "intent": self.intent.name,
            "entities": [e.to_dict() for e in self.entities.all()],
        }

    def __str__(self) -> str:
        """Name."""
        return self.text

    class Meta:
        """Meta."""

        ordering = ("language",)
        unique_together = ("text", "language")
        verbose_name = _("Trigger")
        verbose_name_plural = _("Triggers")


class TriggerEntity(models.Model):
    """Trigger entity model."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    trigger = models.ForeignKey(
        Trigger, models.CASCADE, related_name="entities", verbose_name=_("Trigger")
    )
    entity = models.ForeignKey(
        Entity, models.CASCADE, related_name="triggers", verbose_name=_("Entity")
    )
    start = models.PositiveIntegerField(verbose_name=_("Start"))
    end = models.PositiveIntegerField(verbose_name=_("End"))
    value = models.CharField(max_length=256, verbose_name=_("Value"))

    def to_dict(self) -> dict[str, int | str | dict[str, str | None]]:
        """Convert this model to a dictionary."""
        return {
            "start": self.start,
            "end": self.end,
            "value": self.value,
            "entity": {
                "name": self.entity.name,
                "parent": self.entity.parent.name if self.entity.parent else None,
            },
        }

    def __str__(self) -> str:
        """Name."""
        return self.value

    class Meta:
        """Meta."""

        ordering = ("trigger", "start", "end")
        verbose_name = _("Trigger entity")
        verbose_name_plural = _("Trigger entities")


class Attribute(models.Model):
    """Attribute model."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    key = models.CharField(max_length=256, verbose_name=_("Key"))
    value = models.CharField(
        max_length=512, blank=True, null=True, verbose_name=_("Value")
    )

    def __str__(self) -> str:
        """Name."""
        return f"{self.key}: {self.value}" if self.value else self.key

    class Meta:
        """Meta."""

        ordering = ("key", "value")
        unique_together = ("key", "value")
        verbose_name = _("Attribute")
        verbose_name_plural = _("Attributes")


class Answer(models.Model):
    """Answer model."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    text = models.TextField(verbose_name=_("Text"))
    language = models.CharField(
        max_length=10, choices=settings.LANGUAGES, verbose_name=_("Language")
    )
    attributes = models.ManyToManyField(
        Attribute, blank=True, related_name="answers", verbose_name=_("Attributes")
    )

    def __str__(self) -> str:
        """Name."""
        return self.text

    class Meta:
        """Meta."""

        ordering = ("language",)
        unique_together = ("text", "language")
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")
