# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone, formats
from utils.parser import BaseParser


def _api_call(endpoint, params={}):
    url = '%s/%s/%s' % (settings.APIS['WEATHER']['BASE_URL'],
                        settings.APIS['WEATHER']['VERSION'],
                        endpoint)
    params['APPID'] = settings.APIS['WEATHER']['APPID']
    url = '%s?%s' % (url,
                     '&'.join(['%s=%s' % (k, v) for k, v in params.items()]))

    parser = BaseParser()
    return parser.fetch(url)


def general(language):
    day = timezone.now() + timedelta(days=1)
    params = {
        'lang': language,
        'id': '2879139',
        'units': 'metric'
    }

    temp_max = None
    temp_min = None
    counts = {}
    for data in _api_call(settings.APIS['WEATHER']['GENRAL_ENDPOINT'],
                          params)['list']:
        if day.date() == datetime.utcfromtimestamp(data['dt']).date():
            if temp_max:
                temp_max = max(temp_max, data['main']['temp_max'])
            else:
                temp_max = data['main']['temp_max']

            if temp_min:
                temp_min = min(temp_min, data['main']['temp_min'])
            else:
                temp_min = data['main']['temp_min']

            for condition in data['weather']:
                _id = condition['id']
                if _id not in counts:
                    counts[_id] = 0
                counts[_id] += 1

    weather = sorted(counts.items(), key=lambda i: (i[1], i[0]))[0][0]
    return {
        'temp_min': formats.number_format(temp_min, decimal_pos=1),
        'temp_max': formats.number_format(temp_max, decimal_pos=1),
        'weather': weather
    }
