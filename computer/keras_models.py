# -*- coding: utf-8 -*-

import json
import numpy as np
import os
import string
import sys

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from utils import Singleton


class NLUModel(metaclass=Singleton):
    def __init__(self, vocab='/^ %s' % (string.ascii_lowercase + 'äöüß')):
        vocab = dict((s, str(i)) for i, s in enumerate(vocab))
        self.trans = str.maketrans(vocab)

        if 'nlu' not in settings.MODELS:
            raise ImproperlyConfigured(
                _('No nlu model defiend.')
            )

        print(_('Loading model "%(path)s".') % {
            'path': settings.MODELS['nlu']['path']
        })

        with open(os.path.join(settings.BASE_DIR,
                               settings.MODELS['nlu']['mappings']),
                  'r', encoding='utf-8') as f:
            self.mappings = json.loads(f.read())

        try:
            from keras.models import load_model
            self.model = load_model(
                os.path.join(settings.BASE_DIR, settings.MODELS['nlu']['path'])
            )
        except Exception as e:
            print(_('Could not load model.'), e, file=sys.stderr)
            self.model = None

    def predict(self, text):
        X = np.asarray([int(s.translate(self.trans)) for s in '%s^' % text]). \
            reshape((1, len(text) + 1))
        outs = self.model.predict(X, batch_size=1)
        p = []
        for i in range(len(outs)):
            out = outs[i][0].argmax()
            p.append((self.mappings[i][out], outs[i][0][out]))
        return p
