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
"""Intents Django app intents module."""

from .date import holiday as date_holiday
from .date import general as date_general
from .time import general as time_general
from .weather import general as weather_general


def base(text: str, language: str, **kwargs) -> dict:
    """Handle base logic for intent processing."""
    return {}


affirm = base
deny = base
farewell = base
farewell_night = base
greet = base
greet_feelings = base
thankyou = base

__all__ = (
    "date_holiday",
    "date_general",
    "time_general",
    "weather_general",
    "affirm",
    "deny",
    "farewell",
    "farewell_night",
    "greet",
    "greet_feelings",
    "thankyou",
)
