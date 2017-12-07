# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils import timezone
from django.utils.formats import get_format


def general(language):
    time = timezone.localtime()
    return {'time': time.strftime(get_format('DATE_FORMAT'))}
