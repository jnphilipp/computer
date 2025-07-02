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
import numpy.typing as npt
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
            self.mappings["rvocab"] = {}
            for k, v in self.mappings["vocab"].items():
                self.mappings["rvocab"][v] = k

        try:
            print(
                _('Loading model "%(path)s".')
                % {"path": settings.MODELS["nlu"]["path"]}
            )
            self.nlu_model = load_model(
                settings.BASE_DIR / settings.MODELS["nlu"]["path"]
            )
        except Exception as e:
            print(_("Could not load model."), e, file=sys.stderr)
            self.nlu_model = None

        self.chat_model = None
        if "chat" in settings.MODELS:
            try:
                print(
                    _('Loading model "%(path)s".')
                    % {"path": settings.MODELS["chat"]["path"]}
                )
                self.chat_model = load_model(
                    settings.BASE_DIR / settings.MODELS["chat"]["path"]
                )
            except Exception as e:
                print(_("Could not load model."), e, file=sys.stderr)

    def _clean_text(self, text):
        return re.sub(
            r"[^%s]" % re.escape("".join(self.mappings["vocab"].keys())),
            self.fallback_symbol,
            re.sub(r"\s\s+", " ", text),
        )

    def _text_to_np(
        self, text: str, include_end_of_sequence: bool = True
    ) -> npt.NDArray:
        x_text = np.zeros((1, self.mappings["context_size"]))
        x_text[0, 0] = self.mappings["vocab"]["<begin of sequence>"]
        i = 0
        for i, s in enumerate(text):
            x_text[0, i + 1] = (
                self.mappings["vocab"][s]
                if s in self.mappings["vocab"]
                else self.mappings["vocab"]["<fallback character>"]
            )
        if include_end_of_sequence:
            x_text[0, i + 2] = self.mappings["vocab"]["<end of sequence>"]
        return x_text

    def predict(self, text):
        """Predict intent."""
        text = self._clean_text(text)
        x_text = self._text_to_np(text)
        outs = self.nlu_model.predict({"text": x_text}, batch_size=1)
        p = {"entities": {}}
        for k, v in outs.items():
            p[k] = {
                "name": self.mappings["r" + k + "s"][v.argmax()],
                "p": float(v.max()),
            }
        return p

    def chat(self, text: str, context: str | None = None) -> str:
        """Generate text."""
        text = self._clean_text(text)
        x_text = self._text_to_np(text + ("" if context is None else context), False)
        outs = self.chat_model.predict({"text": x_text}, batch_size=1)
        answer_text = [] if context is None else list()
        done = False
        for i in range(len(text) + 1, len(outs["next"][0])):
            if (
                outs["next"][0][i].argmax()
                == self.mappings["vocab"]["<end of sequence>"]
            ):
                done = True
                break
            answer_text.append(self.mappings["rvocab"][outs["next"][0][i].argmax()])

        if done or len(answer_text) >= 98:
            return "".join(answer_text)
        else:
            return self.chat(text, "".join(answer_text))
