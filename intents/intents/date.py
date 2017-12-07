# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils import timezone
from django.utils.dates import WEEKDAYS, MONTHS


def general(language):
    date = timezone.localtime()
    return {
        'weekday': WEEKDAYS[date.weekday()],
        'day': date.day,
        'month': MONTHS[date.month]
    }
