# -*- coding: utf-8 -*-

import json

from computer.decorators import piwik
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseNotFound)
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from intents.models import Answer, Attribute
from profiles.models import NLURequest


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
    nlu_request = NLURequest.objects.create(
        user=request.user if request.user.is_authenticated else None,
        params=params.dict()
    )

    if 'text' in params:
        text = params.pop('text')[0].lower()
    else:
        return HttpResponseBadRequest('The parameter "text" was not given.')

    from computer.keras_models import NLUModel
    model = NLUModel()
    intent, language = model.predict(text)
    nlu_request.nlu_model_output = {
        'intent': [intent[0], float(intent[1])],
        'language': [language[0], float(language[1])],
    }
    nlu_request.save()

    from intents import intents
    fn = getattr(intents, intent[0])
    properties = fn(language=language[0])

    required_attributes = []
    for k, v in properties.items():
        attributes = Attribute.objects.filter(key=k)
        if attributes.count() > 1:
            required_attributes.append(attributes.filter(value=v)[0].pk)
        elif attributes.count() == 1:
            required_attributes.append(attributes[0].pk)

    answer = Answer.objects.filter(
        intent__name=intent[0],
        language__code=language[0]
    )
    for required_attribute in required_attributes:
        answer = answer.filter(required_attributes__id=required_attribute)
    answer = answer.order_by('?')[:1]
    if answer.count() == 1:
        answer = answer[0]
    else:
        answer = Answer.objects.filter(
            intent__name='fallback',
            language__code=language[0]
        ).order_by('?')[:1][0]

    nlu_request.answer = answer.text % properties
    nlu_request.save()
    data = {
        'certainty': float(intent[1]),
        'response_date': timezone.now().strftime('%Y-%m-%dT%H:%M:%S:%f%z'),
        'reply': answer.text % properties
    }
    return HttpResponse(json.dumps(data), 'application/json')
