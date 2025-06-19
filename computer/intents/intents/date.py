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
"""Intents Django app date intens."""

from datetime import datetime
from django.utils import timezone
from django.utils.dates import WEEKDAYS, MONTHS
from texts.models import TriggerEntity


def holiday(text: str, language: str, **kwargs) -> dict:
    """Holiday intent."""
    date = timezone.localtime().date()

    is_christmas = False
    is_new_years_eve = False
    holiday = None
    for entity in TriggerEntity.objects.filter(entity__name="holiday").filter(
        trigger__language=language
    ):
        if entity.value.lower() in text.lower():
            holiday = entity.value
            christmas = (
                entity.value == "Weihnachten"
                or entity.value == "Heiligabend"
                or entity.value == "christmas"
            )
            new_years_eve = (
                entity.value == "Silvester" or entity.value == "New Year's Eve"
            )

    if is_christmas:
        christmas = datetime(date.year, 12, 24).date()
        days = (christmas - date).days
        if days == 0 or days == -1 or days == -2:
            return {"days": 0, "holiday": holiday}
        elif days == -3:
            return {"days": -1, "holiday": holiday}
        elif days <= 0:
            return {"days": -2, "holiday": holiday}
        else:
            return {"days": days, "holiday": holiday}
    elif is_new_years_eve:
        new_years_eve = datetime(date.year, 12, 31).date()
        days = (new_years_eve - date).days
        if days == 0:
            return {"days": 0, "holiday": holiday}
        else:
            return {"days": days, "holiday": holiday}
    else:
        return {"holiday": holiday}


def general(text: str, language: str, **kwargs) -> dict:
    """General date intent."""
    date = timezone.localtime()
    return {
        "weekday": WEEKDAYS[date.weekday()],
        "day": date.day,
        "month": MONTHS[date.month],
    }
