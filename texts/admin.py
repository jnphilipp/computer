# -*- coding: utf-8 -*-

from computer.fields import SingleLineTextField
from django.contrib import admin
from django.db.models import Count
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _

from .forms import AnswerForm, TriggerEntityForm
from .models import Answer, Attribute, Entity, Trigger, TriggerEntity


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Answer.objects.annotate(
            attributes_count=Count('attributes', distinct=True),
            intents_count=Count('intents', distinct=True)
        )

    def attributes_count(self, inst):
        return inst.attributes_count

    def intents_count(self, inst):
        return inst.intents_count

    def save_model(self, request, obj, form, change):
        super(AnswerAdmin, self).save_model(request, obj, form, change)
        obj.intents.clear()
        for intent in form.cleaned_data['intents']:
             obj.intents.add(intent)

    def get_form(self, request, obj=None, **kwargs):
        ids = []
        if obj:
            ids = [o.pk for o in obj.intents.all()]
        self.form.base_fields['intents'].initial = ids
        return super(AnswerAdmin, self).get_form(request, obj, **kwargs)

    attributes_count.admin_order_field = 'attributes_count'
    attributes_count.short_description = _('Number of Attributes')
    fieldsets = [
        (None, {'fields': ['text', 'language']}),
        (_('Attributes'), {'fields': ['attributes']}),
        (_('Intents'), {'fields': ['intents']}),
    ]
    filter_horizontal = ('attributes', 'intents')
    form = AnswerForm
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={
                'autocomplete': 'off',
                'style': 'min-width: 50%;'
            })
        },
    }
    intents_count.admin_order_field = 'intents_count'
    intents_count.short_description = _('Number of Intents')
    list_display = ('text', 'language', 'attributes_count', 'intents_count')
    list_filter = ('language', 'attributes', 'intents')
    ordering = ('text',)
    search_fields = ('text',)


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['key', 'value']}),
    ]
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={
                'style': 'min-width: 50%;'
            })
        },
    }
    list_display = ('key', 'value')
    ordering = ('key', 'value')
    search_fields = ('key', 'value')


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    def triggers_count(self, inst):
        return inst.triggers.count()

    fieldsets = [
        (None, {'fields': ['name', 'parent']}),
    ]
    list_display = ('name', 'parent', 'triggers_count')
    list_filter = ('parent',)
    ordering = ('name',)
    search_fields = ('name',)
    triggers_count.admin_order_field = 'triggers_count'
    triggers_count.short_description = _('Number of Triggers')


class TriggerEntityInline(admin.TabularInline):
    extra = 1
    fieldsets = [
        (None, {'fields': ['trigger', 'entity', 'start', 'end', 'value']}),
    ]
    form = TriggerEntityForm
    model = TriggerEntity


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Trigger.objects.annotate(entities_count=Count('entities'))

    def entities_count(self, inst):
        return inst.entities_count

    entities_count.admin_order_field = 'entities_count'
    entities_count.short_description = _('Number of Entities')
    fieldsets = [
        (None, {'fields': ['text', 'language', 'intent']}),
    ]
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={
                'style': 'min-width: 50%;'
            })
        },
    }
    inlines = (TriggerEntityInline,)
    list_display = ('text', 'language', 'intent', 'entities_count')
    list_filter = ('language', 'intent')
    ordering = ('text',)
    search_fields = ('text', 'language__name', 'language__code')
