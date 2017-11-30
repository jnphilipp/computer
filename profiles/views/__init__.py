# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from computer.decorators import piwik

from .base import *
from .profile import *


@login_required
@piwik('Index • Profile • computer')
def index(request):
    return redirect('profiles:profile')
