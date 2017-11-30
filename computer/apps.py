# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ComputerConfig(AppConfig):
    name = 'computer'
    verbose_name = _('Computer')
    verbose_name_plural = _('Computers')
