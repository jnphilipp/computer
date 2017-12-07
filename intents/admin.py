# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db.models import Count
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _
from texts.models import SingleLineTextField as TSingleLineTextField, Text

from .models import Answer, Attribute, Intent, SingleLineTextField


class AnswerInline(admin.TabularInline):
    extra = 1
    fieldsets = [
        (None, {
            'fields':['text', 'language', 'intent', 'required_attributes']
        }),
    ]
    filter_horizontal = ('required_attributes',)
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
    def get_queryset(self, request):
        return Answer.objects.annotate(Count('required_attributes'))

    def required_attributes_count(self, inst):
        return inst.required_attributes__count

    fieldsets = [
        (None, {'fields': ['text', 'language', 'intent']}),
        (_('Attributes'), {'fields': ['required_attributes']}),
    ]
    filter_horizontal = ('required_attributes',)
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={
                'autocomplete': 'off',
                'style': 'min-width: 50%;'
            })
        },
    }
    list_display = ('text', 'language', 'intent', 'required_attributes_count')
    list_filter = ('intent', 'language')
    required_attributes_count.admin_order_field = 'required_attributes__count'
    required_attributes_count.short_description = _('Number of Attributes')
    search_fields = ('text', 'language__code', 'language__name',
                     'intent__name')
    ordering = ('intent', 'language')


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['key', 'value']}),
    ]
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={
                'autocomplete': 'off',
                'style': 'min-width: 50%;'
            })
        },
    }
    list_display = ('key', 'value')
    search_fields = ('key', 'value')
    ordering = ('key', 'value')
