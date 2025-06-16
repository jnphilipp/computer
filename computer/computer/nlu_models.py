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
"""Computer Django app nlu model module."""


import json
import numpy as np
import re
import sys

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _
from tensorflow.keras.models import load_model

from .utils import Singleton


class NLUModel(metaclass=Singleton):
    """NLU model."""

    def __init__(self, fallback_symbol="?"):
        """Init."""
        self.fallback_symbol = fallback_symbol

        if "nlu" not in settings.MODELS:
            raise ImproperlyConfigured(_("No nlu model defiend."))

        with open(
            settings.BASE_DIR / settings.MODELS["nlu"]["mappings"],
            "r",
            encoding="utf-8",
        ) as f:
            self.mappings = json.loads(f.read())
            v = dict((s, str(i)) for i, s in enumerate(self.mappings["vocab"]))
            self.trans = str.maketrans(v)

        try:
            print(
                _('Loading model "%(path)s".')
                % {"path": settings.MODELS["nlu"]["path"]}
            )
            self.model = load_model(settings.BASE_DIR / settings.MODELS["nlu"]["path"])
        except Exception as e:
            print(_("Could not load model."), e, file=sys.stderr)
            self.model = None

    def _clean_text(self, text):
        return re.sub(
            r"[^%s]" % re.escape("".join(self.mappings["vocab"].keys())),
            self.fallback_symbol,
            re.sub(r"\s\s+", " ", text),
        )

    def predict(self, text):
        """Predict intent."""
        text = self._clean_text(text)
        X = np.asarray([int(s.translate(self.trans)) for s in "%s^" % text]).reshape(
            (1, len(text) + 1)
        )
        outs = self.model.predict(X, batch_size=1)
        p = {"entities": {}}
        for i in range(len(outs)):
            out = outs[i][0].argmax()

            name = self.mappings["outputs"]["outputs"][i]
            if name in self.mappings["outputs"]:
                p[name] = {
                    "name": self.mappings["outputs"][name][out],
                    "p": float(outs[i][0][out]),
                }
            elif name in self.mappings["outputs"]["entities"]:
                p["entities"]["name"] = float(outs[i][0][out])
            else:
                p[name] = float(outs[i][0][out])
        return p
