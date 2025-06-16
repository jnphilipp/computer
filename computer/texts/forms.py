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
"""Texts Django app forms."""

from django import forms
from django.contrib import admin as admin_module
from django.utils.translation import gettext_lazy as _

from .models import TriggerEntity


class TriggerEntityForm(forms.ModelForm):
    """Trigger entity form."""

    def clean(self):
        """Clean."""
        cleaned_data = super(TriggerEntityForm, self).clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")
        text = cleaned_data.get("trigger").text
        value = cleaned_data.get("value")

        if start > end:
            raise forms.ValidationError(_("End needs to be larger than start."))
        if start > len(text) or end > len(text):
            raise forms.ValidationError(
                _("Start and ends need to be smaller than text length.")
            )

        extracted = text[start:end]
        if extracted != value:
            raise forms.ValidationError(
                _(
                    'The extracted text "%(extracted)s" does not match the '
                    + 'given text "%(value)s".'
                )
                % {"extracted": extracted, "value": value}
            )

    class Meta:
        model = TriggerEntity
        fields = ("start", "end", "value")
