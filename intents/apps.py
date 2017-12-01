# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class IntentsConfig(AppConfig):
    name = 'intents'
    verbose_name = _('Intent')
    verbose_name_plural = _('Intents')
