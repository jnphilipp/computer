# -*- coding: utf-8 -*-

import hashlib
import urllib

from computer.templatetags.computer import register
from django.utils.safestring import mark_safe


@register.simple_tag(takes_context=True)
def gravatar(context, size=40, default='identicon'):
    if context['user'].is_authenticated:
        email = context['user'].email.lower().encode('utf-8')
    else:
        email = ''.encode('utf-8')

    return 'https://www.gravatar.com/avatar/%s?%s' % (
        hashlib.md5(email).hexdigest(),
        urllib.parse.urlencode({'s': str(size), 'd': default})
    )


@register.simple_tag(takes_context=True)
def gravatar_img(context, size=40, default='identicon', classes=''):
    img_str = '<img class="%s" src="%s" height="%d" width="%d">'
    return mark_safe(img_str % (classes, gravatar(context, size, default),
                                size, size))
