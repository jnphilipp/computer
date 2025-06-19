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
            self.mappings["rintents"] = {}
            for k, v in self.mappings["intents"].items():
                self.mappings["rintents"][v] = k
            self.mappings["rlanguages"] = {}
            for k, v in self.mappings["languages"].items():
                self.mappings["rlanguages"][v] = k

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
        x_text = np.asarray(
            [self.mappings["vocab"]["<begin of sequence>"]]
            + [
                (
                    self.mappings["vocab"][s]
                    if s in self.mappings["vocab"]
                    else self.mappings["vocab"]["<fallback character>"]
                )
                for s in text
            ]
            + [self.mappings["vocab"]["<end of sequence>"]]
        ).reshape((1, len(text) + 2))
        outs = self.model.predict({"text": x_text}, batch_size=1)
        p = {"entities": {}}
        for k, v in outs.items():
            p[k] = {
                "name": self.mappings["r" + k + "s"][v.argmax()],
                "p": float(v.max()),
            }
        return p
