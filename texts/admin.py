# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db.models import Count
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _

from .forms import TextEntityForm
from .models import Entity, Text, TextEntity, SingleLineTextField


class TextEntityInline(admin.TabularInline):
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
    def get_queryset(self, request):
        return Text.objects.annotate(entities_count=Count('entities'))

    def entities_count(self, inst):
        return inst.entities_count

    entities_count.admin_order_field = 'entities_count'
    entities_count.short_description = _('Number of Entities')
    fieldsets = [
        (None, {'fields': ['content', 'language', 'intent']}),
    ]
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={
                'autocomplete': 'off',
                'style': 'min-width: 50%;'
            })
        },
    }
    inlines = (TextEntityInline,)
    list_display = ('content', 'language', 'intent', 'entities_count')
    list_filter = ('language', 'intent')
    search_fields = ('content', 'language__name', 'language__code')
    ordering = ('content',)
