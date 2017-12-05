# -*- coding: utf-8 -*-

from django.contrib import admin
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _
from texts.models import SingleLineTextField as TSingleLineTextField, Text

from .models import Answer, Intent, SingleLineTextField


class AnswerInline(admin.TabularInline):
    extra = 1
    fieldsets = [
        (None, {'fields': ['text', 'language', 'intent']}),
    ]
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={
                'autocomplete': 'off',
                'style': 'min-width: 75%;'
            })
        },
    }
    model = Answer


class TextInline(admin.TabularInline):
    extra = 1
    fieldsets = [
        (None, {'fields': ['content', 'language', 'intent']}),
    ]
    formfield_overrides = {
        TSingleLineTextField: {
            'widget': TextInput(attrs={
                'autocomplete': 'off',
                'style': 'min-width: 75%;'
            })
        },
    }
    model = Text


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
    inlines = (TextInline, AnswerInline)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['text', 'language', 'intent']}),
    ]
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={
                'autocomplete': 'off',
                'style': 'min-width: 50%;'
            })
        },
    }
    list_display = ('text', 'language', 'intent')
    list_filter = ('intent', 'language')
    search_fields = ('text', 'language__code', 'language__name',
                     'intent__name')
    ordering = ('intent', 'language')
