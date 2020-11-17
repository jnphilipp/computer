# -*- coding: utf-8 -*-

import json
import numpy as np

from computer.decorators import piwik
from django.db.models import Count
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseNotAllowed, HttpResponseNotFound)
from django.shortcuts import redirect, render
from django.utils import timezone, translation
from django.views.decorators.csrf import csrf_exempt
from texts.models import Answer, Attribute
from profiles.models import NLURequest


@piwik('Chat • computer')
def chat(request):
    return render(request, 'computer/chat.html', locals())


@piwik('Dashboard • computer')
def dashboard(request):
    return redirect('chat')


@csrf_exempt
@piwik('NLU • API • computer')
def nlu(request):
    """Handels GET/POST request for nlu.

    POST parameters:
        text: the text to do the nlu for
    """
    if request.method == 'GET':
        return HttpResponseNotAllowed(['POST'])

    params = request.POST.copy()
    if 'application/json' == request.META.get('CONTENT_TYPE'):
        params.update(json.loads(request.body.decode('utf-8')))
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
    outs = model.predict(text)

    translation.activate(outs['language']['name'])
    request.LANGUAGE_CODE = translation.get_language()

    nlu_request.nlu_model_output = outs
    nlu_request.save()

    from intents import intents
    fn = getattr(intents, outs['intent']['name'])
    properties = fn(text=text, language=outs['language']['name'], **outs['entities'])
    nlu_request.intent_output = properties
    nlu_request.save()

    attributes = []
    for k, v in properties.items():
        attrs = Attribute.objects.filter(key=k)
        if attrs.count() > 1:
            if attrs.filter(value=v).exists():
                attributes.append(attrs.filter(value=v)[0].pk)
            else:
                attributes.append(attrs.filter(value=None)[0].pk)
        elif attrs.count() == 1:
            attributes.append(attrs[0].pk)

    answer = Answer.objects.annotate(num_attrs=Count('attributes')).filter(
        intents__name=outs['intent']['name'],
        language__code=outs['language']['name'],
        num_attrs=len(attributes)
    )
    for attribute in attributes:
        answer = answer.filter(attributes__id=attribute)

    if answer.count() >= 1:
        answer = np.random.choice(answer)
    else:
        answer = Answer.objects.filter(
            intents__name='fallback',
            language__code=language[0]
        ).order_by('?')[:1][0]

    nlu_request.answer = answer.text % properties
    nlu_request.save()
    data = {
        'response_date': timezone.now().strftime('%Y-%m-%dT%H:%M:%S:%f%z'),
        'intent': outs['intent']['name'],
        'certainty': outs['intent']['p'],
        'replies': [answer.text % properties]
    }
    return HttpResponse(json.dumps(data), 'application/json')
