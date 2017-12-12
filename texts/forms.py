# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin as admin_module
from django.utils.translation import ugettext_lazy as _
from intents.models import Intent
from .models import Answer, TriggerEntity


class AnswerForm(forms.ModelForm):
    intents = forms.ModelMultipleChoiceField(
        queryset=Intent.objects.all(),
        required=False,
        widget=admin_module.widgets.FilteredSelectMultiple('intents', False)
    )

    class Meta:
        model = Answer
        fields = '__all__'


class TriggerEntityForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(TriggerEntityForm, self).clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        text = cleaned_data.get('trigger').text
        value = cleaned_data.get('value')

        if start > end:
            raise forms.ValidationError(
                _('End needs to be larger than start.')
            )
        if start > len(text) or end > len(text):
            raise forms.ValidationError(
                _('Start and ends need to be smaller than text length.')
            )

        extracted = text[start:end]
        if extracted != value:
            raise forms.ValidationError(
                _('The extracted text "%(extracted)s" does not match the ' +
                  'given text "%(value)s".'
                ) % {'extracted': extracted, 'value': value}
            )

    class Meta:
        model = TriggerEntity
        fields = ('start', 'end', 'value')
