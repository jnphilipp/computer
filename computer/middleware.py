# -*- coding: utf-8 -*-

import pytz

from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        timezone.deactivate()
        if request.user.is_authenticated:
            if 'timezone' in request.user.profile.preferences:
                timezone.activate(
                    pytz.timezone(request.user.profile.preferences['timezone'])
                )
