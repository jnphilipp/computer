# -*- coding: utf-8 -*-

from computer.fields import SingleLineTextField
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Entity(models.Model):
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
    parent = models.ForeignKey(
        'Entity',
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='children',
        verbose_name=_('Parent')
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = _('Entity')
        verbose_name_plural = _('Entities')


class Trigger(models.Model):
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
    intent = models.ForeignKey(
        'intents.Intent',
        models.CASCADE,
        related_name='triggers',
        verbose_name=_('Intent')
    )
    language = models.ForeignKey(
        'countries.Language',
        models.CASCADE,
        related_name='triggers',
        verbose_name=_('Language')
    )

    def to_dict(self):
        return {
            'text': self.text,
            'language': self.language.code,
            'intent': self.intent.name,
            'entities': [e.to_dict() for e in self.entities.all()]
        }

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('language',)
        unique_together = ('text', 'language')
        verbose_name = _('Trigger')
        verbose_name_plural = _('Triggers')


class TriggerEntity(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    trigger = models.ForeignKey(
        Trigger,
        models.CASCADE,
        related_name='entities',
        verbose_name=_('Trigger')
    )
    entity = models.ForeignKey(
        Entity,
        models.CASCADE,
        related_name='triggers',
        verbose_name=_('Entity')
    )
    start = models.PositiveIntegerField(
        verbose_name=_('Start')
    )
    end = models.PositiveIntegerField(
        verbose_name=_('End')
    )
    value = SingleLineTextField(
        verbose_name=_('Value')
    )

    def to_dict(self):
        return {
            'start': self.start,
            'end': self.end,
            'value': self.value,
            'entity': {
                'name': self.entity.name,
                'parent': self.entity.parent.name if self.entity.parent else None
            }
        }

    def __str__(self):
        return self.value

    class Meta:
        ordering = ('trigger', 'start', 'end')
        verbose_name = _('Trigger entity')
        verbose_name_plural = _('Trigger entities')


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
        return ('%s: %s' % (self.key, self.value)) if self.value else self.key

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
    attributes = models.ManyToManyField(
        Attribute,
        blank=True,
        related_name='answers',
        verbose_name=_('Attributes')
    )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('language',)
        unique_together = ('text', 'language')
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')
