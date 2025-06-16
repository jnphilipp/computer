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
"""Profiles Django app forms."""

from django.contrib.auth import forms, get_user_model
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


# class PasswordChangeForm(forms.PasswordChangeForm):
#     def __init__(self, *args, **kwargs):
#         super(PasswordChangeForm, self).__init__(*args, **kwargs)
#         self.fields['new_password1'].help_text = \
#             mark_safe(self.fields['new_password1'].help_text)


# class SetPasswordForm(forms.SetPasswordForm):
#     def __init__(self, *args, **kwargs):
#         super(SetPasswordForm, self).__init__(*args, **kwargs)
#         self.fields['new_password1']. \
#             help_text = mark_safe(self.fields['new_password1'].help_text)


class UserChangeForm(forms.UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields["password"].help_text = mark_safe(self.fields["password"].help_text)

    class Meta(forms.UserChangeForm.Meta):
        model = get_user_model()
        fields = ("email", "password", "first_name", "last_name")


class UserCreationForm(forms.UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields["password1"].help_text = mark_safe(
            self.fields["password1"].help_text
        )

    class Meta(forms.UserCreationForm.Meta):
        model = get_user_model()
        fields = ("email", "first_name")
