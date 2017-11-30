# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from profiles.forms import UserChangeForm
from profiles.models import Profile
from computer.decorators import piwik


@csrf_protect
@login_required
@piwik('Profile • computer')
def profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = UserChangeForm(instance=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                _('Your profile has been successfully updated.')
            )
    else:
        form = UserChangeForm(instance=request.user)
    return render(request, 'profiles/profile/detail.html', locals())
