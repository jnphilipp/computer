# -*- coding: utf-8 -*-

import sys

from functools import wraps
from piwikapi.tracking import PiwikTracker
from trader.settings import PIWIK
from urllib.error import HTTPError


def piwik(title):
    def piwik_decorator(func):
        @wraps(func)
        def func_wrapper(request, *args, **kwargs):
            if check_piwik_settings():
                try:
                    piwik = PiwikTracker(PIWIK['SITE_ID'], request)
                    piwik.set_api_url('%s/piwik.php' % PIWIK['URL'])
                    piwik.set_ip(get_client_ip(request))
                    piwik.set_token_auth(PIWIK['AUTH_TOKEN'])
                    piwik.do_track_page_view(title)
                except HTTPError as e:
                    sys.stderr.write(str(e))
                    sys.stderr.write('\n')

            return func(request, *args, **kwargs)
        return func_wrapper
    return piwik_decorator


def check_piwik_settings():
    if 'SITE_ID' in PIWIK and 'URL' in PIWIK and 'AUTH_TOKEN' in PIWIK:
        if PIWIK['SITE_ID'] and PIWIK['URL'] and PIWIK['AUTH_TOKEN']:
            return True
    return False


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    else:
        return request.META.get('REMOTE_ADDR')
