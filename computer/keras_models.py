# -*- coding: utf-8 -*-

import json
import numpy as np
import os
import re
import string
import sys

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from utils import Singleton


class NLUModel(metaclass=Singleton):
    def __init__(self, fallback_symbol='?'):
        self.fallback_symbol = fallback_symbol

        if 'nlu' not in settings.MODELS:
            raise ImproperlyConfigured(
                _('No nlu model defiend.')
            )

        with open(os.path.join(settings.BASE_DIR,
                               settings.MODELS['nlu']['mappings']),
                  'r', encoding='utf-8') as f:
            self.mappings = json.loads(f.read())
            v = dict((s, str(i)) for i, s in enumerate(self.mappings['vocab']))
            self.trans = str.maketrans(v)

        try:
            from keras.models import load_model
            print(_('Loading model "%(path)s".') % {
                'path': settings.MODELS['nlu']['path']
            })
            self.model = load_model(
                os.path.join(settings.BASE_DIR, settings.MODELS['nlu']['path'])
            )
        except Exception as e:
            print(_('Could not load model.'), e, file=sys.stderr)
            self.model = None

    def _clean_text(self, text):
        return re.sub('[^%s]' % re.escape(self.mappings['vocab']),
                      self.fallback_symbol, re.sub(r'\s\s+', ' ',
                                                   text.lower()))

    def predict(self, text):
        text = self._clean_text(text)
        X = np.asarray([int(s.translate(self.trans)) for s in '%s^' % text]). \
            reshape((1, len(text) + 1))
        outs = self.model.predict(X, batch_size=1)
        p = {'entities': {}}
        for i in range(len(outs)):
            out = outs[i][0].argmax()

            name = self.mappings['outputs']['outputs'][i]
            if name in self.mappings['outputs']:
                p[name] = {
                    'name': self.mappings['outputs'][name][out],
                    'p': float(outs[i][0][out])
                }
            elif name in self.mappings['outputs']['entities']:
                p['entities']['name'] = float(outs[i][0][out])
            else:
                p[name] = float(outs[i][0][out])
        return p
