# -*- coding: utf-8 -*-

from django.contrib import admin
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _

from .forms import TextEntityForm
from .models import Entity, Text, TextEntity, SingleLineTextField


class TextEntityInline(admin.StackedInline):
    extra = 1
    fieldsets = [
        (None, {'fields': ['text', 'entity', 'start', 'end', 'value']}),
    ]
    form = TextEntityForm
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={'autocomplete': 'off'})
        },
    }
    model = TextEntity


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name']}),
    ]
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={'autocomplete': 'off'})
        },
    }
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['content', 'language']}),
    ]
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={'autocomplete': 'off'})
        },
    }
    inlines = (TextEntityInline,)
    list_display = ('content', 'language')
    list_filter = ('language',)
    search_fields = ('content', 'language__name', 'language__code')
    ordering = ('content',)
