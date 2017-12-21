# -*- coding: utf-8 -*-

from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.utils.dates import WEEKDAYS, MONTHS
from texts.models import TriggerEntity


def holiday(text, language, **kwargs):
    date = timezone.localtime().date()

    christmas = False
    new_years_eve = False
    holiday = None
    for entity in TriggerEntity.objects.filter(entity__name='holiday').filter(trigger__language__code=language):
        if entity.value.lower() in text.lower():
            holiday = entity.value
            christmas = entity.value == 'Weihnachten' or entity.value == 'Heiligabend' or entity.value == 'christmas'
            new_years_eve = entity.value == 'Silvester' or entity.value == 'New Year\'s Eve'

    if christmas:
        christmas = datetime(date.year, 12, 24).date()
        days = (christmas - date).days
        if days == 0 or days == -1 or days == -2:
            return {'days': 0, 'holiday': holiday}
        elif days == -3:
            return {'days': -1, 'holiday': holiday}
        elif days <= 0:
            return {'days': -2, 'holiday': holiday}
        else:
            return {'days': days, 'holiday': holiday}
    elif new_years_eve:
        new_years_eve = datetime(date.year, 12, 31).date()
        days = (new_years_eve - date).days
        if days == 0:
            return {'days': 0, 'holiday': holiday}
        else:
            return {'days': days, 'holiday': holiday}
    else:
        return {'holiday': holiday}


def general(text, language, **kwargs):
    date = timezone.localtime()
    return {
        'weekday': WEEKDAYS[date.weekday()],
        'day': date.day,
        'month': MONTHS[date.month]
    }
