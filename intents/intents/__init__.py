# -*- coding: utf-8 -*-


from .date import holiday as date_holiday
from .date import general as date_general
from .time import general as time_general
from .weather import general as weather_general


def base(text, language, **kwargs):
    return {}


affirm = base
deny = base
farewell = base
farewell_night = base
greet = base
greet_feelings = base
thankyou = base
