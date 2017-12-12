# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth import forms as authforms, get_user_model
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


class AuthenticationForm(authforms.AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['password'].help_text = mark_safe(
            '<a href="%s">%s</a>' % (
                reverse('profiles:password_reset'),
                _('Forgot your password?')
            )
        )


class PasswordChangeForm(authforms.PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = \
            mark_safe(self.fields['new_password1'].help_text)


class SetPasswordForm(authforms.SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1']. \
            help_text = mark_safe(self.fields['new_password1'].help_text)


class UserChangeForm(authforms.UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget = forms.TextInput()
        self.fields['last_name'].widget = forms.TextInput()
        self.fields['password'].help_text = mark_safe(
            self.fields['password'].help_text
        )

    class Meta(authforms.UserChangeForm.Meta):
        model = get_user_model()
        fields = ('email', 'password', 'first_name', 'last_name')


class UserCreationForm(authforms.UserCreationForm):
    class Meta(authforms.UserCreationForm.Meta):
        model = get_user_model()
        fields = ('email',)
