# -*- coding: utf-8 -*-

from computer.fields import SingleLineTextField
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Intent(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    name = SingleLineTextField(
        unique=True,
        verbose_name=_('Name')
    )
    answers = models.ManyToManyField(
        'texts.Answer',
        blank=True,
        related_name='intents',
        verbose_name=_('Answers')
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = _('Intent')
        verbose_name_plural = _('Intents')
