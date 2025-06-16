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
"""Profiles Django app admin."""

from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from .forms import UserCreationForm
from .models import NLURequest, Profile, User


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    """User admin."""

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
    add_form = UserCreationForm
    exclude = ("username",)
    fieldsets = auth_admin.UserAdmin.fieldsets
    fieldsets[0][1]["fields"] = ("email", "password")
    fieldsets[1][1]["fields"] = ("first_name", "last_name")
    list_display = ("email", "first_name", "last_name", "is_active", "is_staff")
    ordering = ("email",)
    search_fields = (
        "email",
        "first_name",
        "last_name",
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Profiles admin."""

    fieldsets = [
        (None, {"fields": ["user", "avatar", "preferences"]}),
    ]
    list_display = ("user",)
    ordering = ("user",)


@admin.register(NLURequest)
class NLURequestAdmin(admin.ModelAdmin):
    """NLU request admin."""

    def get_queryset(self, request):
        return NLURequest.objects.annotate(
            response_time=F("updated_at") - F("created_at")
        )

    @admin.display(ordering="response_time", description=_("Response time"))
    def show_response_time(self, inst):
        """Show response time."""
        return inst.response_time

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "user",
                    "params",
                    "nlu_model_output",
                    "intent_output",
                    "answer",
                ]
            },
        ),
    ]
    list_display = (
        "user",
        "params",
        "nlu_model_output",
        "intent_output",
        "answer",
        "show_response_time",
    )
    list_filter = ("user", "updated_at")
    ordering = ("-updated_at",)
    readonly_fields = (
        "user",
        "params",
        "nlu_model_output",
        "intent_output",
        "answer",
        "updated_at",
    )
