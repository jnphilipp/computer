# -*- coding: utf-8 -*-

from django.utils import timezone
from computer.templatetags.computer import register


@register.filter
def startswith(value, start):
    return value.startswith(start)


@register.filter
def endswith(value, end):
    return value.endswith(end)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def timestamp(format_str):
    return timezone.now().strftime(format_str)
