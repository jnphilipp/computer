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
"""Texts Django app admin."""

from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from .forms import TriggerEntityForm
from .models import Answer, Attribute, Entity, Trigger, TriggerEntity


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Answer admin."""

    def get_queryset(self, request):
        """Get queryset."""
        return Answer.objects.annotate(
            attributes_count=Count("attributes", distinct=True),
            intents_count=Count("intents", distinct=True),
        )

    @admin.display(ordering="attributes_count", description=_("Number of Attributes"))
    def attributes_count(self, inst) -> int:
        """Attributes count."""
        return inst.attributes_count

    @admin.display(ordering="intents_count", description=_("Number of Intents"))
    def intents_count(self, inst) -> int:
        """Intents count."""
        return inst.intents_count

    fieldsets = [
        (None, {"fields": ["text", "language"]}),
        (_("Attributes"), {"fields": ["attributes"]}),
    ]
    filter_horizontal = ("attributes",)
    list_display = ("text", "language", "attributes_count", "intents_count")
    list_filter = ("language", "attributes")
    ordering = ("text",)
    search_fields = ("text",)


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    """Attribute admin."""

    fieldsets = [
        (None, {"fields": ["key", "value"]}),
    ]
    list_display = ("key", "value")
    ordering = ("key", "value")
    search_fields = ("key", "value")


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    """Entity admin."""

    def get_queryset(self, request):
        """Get queryset."""
        return Entity.objects.annotate(
            triggers_count=Count("triggers", distinct=True),
        )

    @admin.display(ordering="triggers_count", description=_("Number of Triggers"))
    def triggers_count(self, inst):
        """Triggers count."""
        return inst.triggers_count

    fieldsets = [
        (None, {"fields": ["name", "parent"]}),
    ]
    list_display = ("name", "parent", "triggers_count")
    list_filter = ("parent",)
    ordering = ("name",)
    search_fields = ("name",)


class TriggerEntityInline(admin.TabularInline):
    """Trigger entity inline admin."""

    extra = 1
    fieldsets = [
        (None, {"fields": ["trigger", "entity", "start", "end", "value"]}),
    ]
    form = TriggerEntityForm
    model = TriggerEntity


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    """Trigger admin."""

    def get_queryset(self, request):
        """Get queryset."""
        return Trigger.objects.annotate(entities_count=Count("entities"))

    @admin.display(ordering="entitites_count", description=_("Number of Entities"))
    def entities_count(self, inst):
        """Entities count."""
        return inst.entities_count

    fieldsets = [
        (None, {"fields": ["text", "language", "intent"]}),
    ]
    inlines = (TriggerEntityInline,)
    list_display = ("text", "language", "intent", "entities_count")
    list_filter = ("intent", "language")
    ordering = ("text",)
    search_fields = ("text", "language")
