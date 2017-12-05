# -*- coding: utf-8 -*-

import json

from computer.decorators import piwik
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseNotFound)
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from intents.models import Answer


@piwik('Dashboard • computer')
def dashboard(request):
    return render(request, 'computer/dashboard.html', locals())


@csrf_exempt
@piwik('NLU • API • computer')
def nlu(request):
    """Handels GET/POST request for nlu.

    GET/POST parameters:
        text: the text to do the nlu for
    """
    params = request.POST.copy() if request.method == 'POST' \
        else request.GET.copy()
    if 'application/json' == request.META.get('CONTENT_TYPE'):
        params.update(json.loads(request.body.decode('utf-8')))
    found_params = params.dict()

    if 'text' in params:
        text = params.pop('text')[0].lower()
    else:
        return HttpResponseBadRequest('The parameter "text" was not given.')

    from computer.keras_models import NLUModel
    model = NLUModel()
    intent, language = model.predict(text)

    from intents import intents
    fn = getattr(intents, intent[0])
    answer_dict = fn(language=language[0])

    answer = Answer.objects.filter(
        intent__name=intent[0],
        language__code=language[0]
    ).order_by('?')[:1]
    if answer.count() == 1:
        answer = answer[0]
    else:
        answer = Answer.objects.filter(
            intent__name='fallback',
            language__code=language[0]
        ).order_by('?')[:1][0]

    data = {
        'certainty': float(intent[1]),
        'response_date': timezone.now().strftime('%Y-%m-%dT%H:%M:%S:%f%z'),
        'reply': answer.text % answer_dict
    }

    return HttpResponse(json.dumps(data), 'application/json')
