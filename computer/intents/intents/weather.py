# Copyright (C) 2017-2025 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
#
# Computer - personal assistant.
#
# This file is part of computer.
#
# computer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# computer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with computer. If not, see <http://www.gnu.org/licenses/>
"""Intents Django app wather intents."""

import requests

from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone, formats


def _api_call(endpoint: str, params: dict = {}) -> dict:
    url = (
        f'{settings.APIS["WEATHER"]["BASE_URL"]}/'
        + f'{settings.APIS["WEATHER"]["VERSION"]}/{endpoint}'
    )
    params["APPID"] = settings.APIS["WEATHER"]["APPID"]

    r = requests.get(url, header=params)
    return r.json()


def general(text: str, language: str, **kwargs) -> dict:
    """General weather intent."""
    day = timezone.now() + timedelta(days=1)
    params = {
        "lang": language,
        "id": "2879139",
        "units": "metric",
        "user-agent": kwargs["user_agent"],
    }

    temp_max = None
    temp_min = None
    counts: dict[str, int] = {}
    for data in _api_call(settings.APIS["WEATHER"]["GENRAL_ENDPOINT"], params)["list"]:
        if day.date() == datetime.utcfromtimestamp(data["dt"]).date():
            if temp_max:
                temp_max = max(temp_max, data["main"]["temp_max"])
            else:
                temp_max = data["main"]["temp_max"]

            if temp_min:
                temp_min = min(temp_min, data["main"]["temp_min"])
            else:
                temp_min = data["main"]["temp_min"]

            for condition in data["weather"]:
                _id = condition["id"]
                if _id not in counts:
                    counts[_id] = 0
                counts[_id] += 1

    weather = sorted(counts.items(), key=lambda i: (i[1], i[0]), reverse=True)[0][0]
    return {
        "temp_min": formats.number_format(temp_min, decimal_pos=1),
        "temp_max": formats.number_format(temp_max, decimal_pos=1),
        "weather": weather,
    }
