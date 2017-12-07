# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils import formats, timezone


def general(language):
    time = timezone.localtime()
    return {'time': formats.time_format(time, 'TIME_FORMAT')}
