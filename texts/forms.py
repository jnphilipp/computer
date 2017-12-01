# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import TextEntity


class TextEntityForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(TextEntityForm, self).clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        content = cleaned_data.get('text').content
        value = cleaned_data.get('value')

        if start > end:
            raise forms.ValidationError(
                _('End needs to be larger than start.')
            )
        if start > len(content) or end > len(content):
            raise forms.ValidationError(
                _('Start and ends need to be smaller than content length.')
            )

        extracted = content[start:end]
        if extracted != value:
            raise forms.ValidationError(
                _('The extracted text "%(extracted)s" does not match the ' +
                  'given text "%(value)s".'
                ) % {'extracted': extracted, 'value': value}
            )

    class Meta:
        model = TextEntity
        fields = ('start', 'end', 'value')
