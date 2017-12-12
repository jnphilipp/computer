# -*- coding: utf-8 -*-

from computer.fields import SingleLineTextField
from django.contrib import admin
from django.db.models import Count
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _
from texts.models import Trigger

from .models import Intent


class TriggerInline(admin.TabularInline):
    extra = 1
    fieldsets = [
        (None, {'fields': ['text', 'language', 'intent']}),
    ]
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={
                'style': 'min-width: 75%;'
            })
        },
    }
    model = Trigger


@admin.register(Intent)
class IntentAdmin(admin.ModelAdmin):
    def answers_count(self, inst):
        return inst.answers.count()

    answers_count.admin_order_field = 'answers_count'
    answers_count.short_description = _('Number of Answers')
    fieldsets = [
        (None, {'fields': ['name']}),
        (_('Answers'), {'fields': ['answers']})
    ]
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={
                'style': 'min-width: 50%;'
            })
        },
    }
    filter_horizontal = ('answers',)
    inlines = (TriggerInline,)
    list_display = ('name', 'answers_count')
    ordering = ('name',)
    search_fields = ('name',)
