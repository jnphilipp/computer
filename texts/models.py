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
    language = models.ForeignKey(
        'countries.Language',
        models.CASCADE,
        related_name='texts',
        verbose_name=_('Language')
    )

    def __str__(self):
        return self.content

    class Meta:
        ordering = ('language',)
        unique_together = ('content', 'language')
        verbose_name = _('Text')
        verbose_name_plural = _('Texts')
