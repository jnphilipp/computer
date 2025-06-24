# Copyright (C) 2017-2025 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
#
# Computer - personal assistant.
#
# This file is part of computer.
#
# computer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# computer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with computer. If not, see <http://www.gnu.org/licenses/>
"""Computer Django app views."""

import json
import numpy as np

from django.db.models import Count
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django_markdowns.templatetags.markdowns import md
from intents import intents
from profiles.models import NLURequest
from texts.models import Answer, Attribute

from .nlu_models import NLUModel


@csrf_exempt
def markdown(request):
    """Handels GET/POST request for markdown.

    GET/POST parameters:
        text: the text to process
    """
    if request.method not in ["GET", "POST"]:
        return HttpResponseNotAllowed(["GET", "POST"])

    params = request.POST.copy() if request.method == "POST" else request.GET.copy()
    if "application/json" == request.META.get("CONTENT_TYPE"):
        params.update(json.loads(request.body.decode("utf-8")))

    if "text" in params:
        text = params.pop("text")[0].lower()
    else:
        return HttpResponseBadRequest('The parameter "text" was not given.')

    return JsonResponse({"text": md(text)})


@csrf_exempt
def nlu(request):
    """Handels POST request for nlu.

    POST parameters:
        text: the text to do the nlu for
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    params = request.POST.copy()
    if "application/json" == request.META.get("CONTENT_TYPE"):
        params.update(json.loads(request.body.decode("utf-8")))

    nlu_request = NLURequest.objects.create(
        user=request.user if request.user.is_authenticated else None,
        params=params.dict(),
    )

    if "text" in params:
        text = params.pop("text")[0].lower()
    else:
        return HttpResponseBadRequest('The parameter "text" was not given.')

    try:
        model = NLUModel()
        outs = model.predict(text)

        translation.activate(outs["language"]["name"])
        request.LANGUAGE_CODE = translation.get_language()

        nlu_request.nlu_model_output = outs
        nlu_request.save()

        fn = getattr(intents, outs["intent"]["name"])
        properties = fn(
            text=text,
            language=outs["language"]["name"],
            user_agent=request.headers.get("User-Agent"),
            **outs["entities"]
        )
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

        answer = Answer.objects.annotate(num_attrs=Count("attributes")).filter(
            intents__name=outs["intent"]["name"],
            num_attrs=len(attributes),
            language=outs["language"]["name"],
        )
        for attribute in attributes:
            answer = answer.filter(attributes__id=attribute)

        if answer.count() >= 1:
            answer = np.random.choice(answer)
        else:
            answer = Answer.objects.filter(
                intents__name="fallback", language=request.LANGUAGE_CODE
            ).order_by("?")[:1][0]

        nlu_request.answer = answer.text % properties
        nlu_request.save()
        return JsonResponse(
            {
                "response_date": timezone.now().strftime("%Y-%m-%dT%H:%M:%S:%f%z"),
                "intent": outs["intent"]["name"],
                "certainty": outs["intent"]["p"],
                "replies": [md(answer.text % properties)],
            }
        )
    except Exception as e:
        text = _("An error occured while processing your request.")
        nlu_request.answer = text + " " + str(e)
        nlu_request.save()
        return JsonResponse(
            {
                "response_date": timezone.now().strftime("%Y-%m-%dT%H:%M:%S:%f%z"),
                "intent": "error",
                "certainty": 1.0,
                "replies": [text, str(e)],
            }
        )
