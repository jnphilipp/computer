# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class SingleLineTextField(models.TextField):
    pass


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

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = _('Intent')
        verbose_name_plural = _('Intents')


class Answer(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    text = SingleLineTextField(
        verbose_name=_('Text')
    )
    language = models.ForeignKey(
        'countries.Language',
        models.CASCADE,
        related_name='answers',
        verbose_name=_('Language')
    )
    intent = models.ForeignKey(
        Intent,
        models.CASCADE,
        related_name='answers',
        verbose_name=_('Intent')
    )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('text',)
        unique_together = ('text', 'language', 'intent')
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')
