# -*- coding: utf-8 -*-

from django.contrib import admin
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _

from .models import Intent, SingleLineTextField


@admin.register(Intent)
class IntentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name']}),
    ]
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={
                'autocomplete': 'off',
                'style': 'min-width: 50%;'
            })
        },
    }
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
