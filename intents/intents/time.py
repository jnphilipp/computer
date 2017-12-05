# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils import timezone


def general(language):
    time = timezone.localtime()
    return {'time': time.strftime('%H:%M')}
