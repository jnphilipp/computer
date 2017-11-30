# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _

from .forms import UserCreationForm
from .models import Profile, SingleLineTextField, User


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    add_form = UserCreationForm
    exclude = ('username',)
    fieldsets = auth_admin.UserAdmin.fieldsets
    fieldsets[0][1]['fields'] = ('email', 'password')
    fieldsets[1][1]['fields'] = ('first_name', 'last_name')
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={'autocomplete': 'off'})
        },
    }
    list_display = ('email', 'first_name', 'last_name', 'is_active',
                    'is_staff')
    ordering = ('email',)
    search_fields = ('email', 'first_name', 'last_name',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['user']}),
    ]
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={'autocomplete': 'off'})
        },
    }
    ordering = ('user',)
