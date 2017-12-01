# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CountriesConfig(AppConfig):
    name = 'countries'
    verbose_name = _('Country')
    verbose_name_plural = _('Countries')
