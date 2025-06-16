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
"""Intents Django app admin."""

from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from texts.models import Trigger

from .models import Intent


class TriggerInline(admin.TabularInline):
    """Trigger inline admin."""

    extra = 1
    fieldsets = [
        (None, {"fields": ["text", "language", "intent"]}),
    ]
    model = Trigger


@admin.register(Intent)
class IntentAdmin(admin.ModelAdmin):
    """Intent admin."""

    def get_queryset(self, request):
        """Get queryset."""
        return Intent.objects.annotate(
            answers_count=Count("answers", distinct=True),
            triggers_count=Count("triggers", distinct=True),
        )

    @admin.display(ordering="answers_count", description=_("Number of Answers"))
    def answers_count(self, inst):
        """Answers count."""
        return inst.answers_count

    @admin.display(ordering="triggers_count", description=_("Number of Triggers"))
    def triggers_count(self, inst):
        """Triggers count."""
        return inst.triggers_count

    fieldsets = [(None, {"fields": ["name"]}), (_("Answers"), {"fields": ["answers"]})]
    filter_horizontal = ("answers",)
    inlines = (TriggerInline,)
    list_display = ("name", "triggers_count", "answers_count")
    ordering = ("name",)
    search_fields = ("name",)
