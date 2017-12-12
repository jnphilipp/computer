# -*- coding: utf-8 -*-

from django.contrib import admin
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _

from .models import Country, Language


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'locale_name', 'code', 'phone_prefix']}),
    ]
    list_display = ('name', 'locale_name', 'code')
    search_fields = ('name', 'locale_name', 'code')
    ordering = ('code',)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'code']}),
        (_('Countries'), {'fields': ['countries']}),
    ]
    filter_horizontal = ('countries',)
    list_display = ('name', 'code')
    list_filter = ('countries',)
    search_fields = ('name', 'code')
    ordering = ('code',)
