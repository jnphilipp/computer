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


class Attribute(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    key = SingleLineTextField(
        verbose_name=_('Key')
    )
    value = SingleLineTextField(
        blank=True,
        null=True,
        verbose_name=_('Value')
    )

    def __str__(self):
        return '%s: %s' % (self.key, self.value)

    class Meta:
        ordering = ('key', 'value')
        unique_together = ('key', 'value')
        verbose_name = _('Attribute')
        verbose_name_plural = _('Attributes')


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
    required_attributes = models.ManyToManyField(
        Attribute,
        blank=True,
        related_name='answers',
        verbose_name=_('Required attributes')
    )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('text',)
        unique_together = ('text', 'language', 'intent')
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')
