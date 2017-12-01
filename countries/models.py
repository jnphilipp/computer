# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class SingleLineTextField(models.TextField):
    pass


class Country(models.Model):
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
    locale_name = SingleLineTextField(
        unique=True,
        verbose_name=_('Locale name')
    )
    code = models.CharField(
        max_length=2,
        unique=True,
        verbose_name=_('ISO code')
    )
    phone_prefix = models.CharField(
        max_length=5,
        unique=True,
        verbose_name=_('Phone prefix')
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('code',)
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')


class Language(models.Model):
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
    code = models.CharField(
        max_length=3,
        unique=True,
        verbose_name=_('ISO code')
    )
    countries = models.ManyToManyField(
        Country,
        blank=True,
        related_name='languages',
        verbose_name=_('Countries')
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')
