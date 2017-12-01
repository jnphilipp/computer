# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class SingleLineTextField(models.TextField):
    pass


class Text(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    content = SingleLineTextField(
        verbose_name=_('Content')
    )
    intent = models.ForeignKey(
        'intents.Intent',
        models.CASCADE,
        related_name='texts',
        verbose_name=_('Intent')
    )
    language = models.ForeignKey(
        'countries.Language',
        models.CASCADE,
        related_name='texts',
        verbose_name=_('Language')
    )

    def to_dict(self):
        return {
            'text': self.content,
            'language': self.language.code,
            'entities': [e.to_dict() for e in self.entities.all()]
        }

    def __str__(self):
        return self.content

    class Meta:
        ordering = ('language',)
        unique_together = ('content', 'language')
        verbose_name = _('Text')
        verbose_name_plural = _('Texts')


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

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = _('Entity')
        verbose_name_plural = _('Entities')


class TextEntity(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    text = models.ForeignKey(
        Text,
        models.CASCADE,
        related_name='entities',
        verbose_name=_('Text')
    )
    entity = models.ForeignKey(
        Entity,
        models.CASCADE,
        related_name='texts',
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
            'entity': self.entity.name
        }

    def __str__(self):
        return self.value

    class Meta:
        ordering = ('text', 'start', 'end')
        verbose_name = _('Text entity')
        verbose_name_plural = _('Text entities')
