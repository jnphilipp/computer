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
"""Computer Django app train command."""

import gzip
import json
import math
import numpy as np
import numpy.typing as npt
import string

from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from keras import Model
from keras.callbacks import Callback, EarlyStopping, ReduceLROnPlateau
from keras.layers import (
    Input,
    Concatenate,
    Conv1D,
    Dense,
    Embedding,
    Flatten,
    SpatialDropout1D,
)
from keras.optimizers import AdamW
from keras.utils import Progbar, PyDataset, to_categorical
from logging import Logger
from pathlib import Path
from sacred import Experiment
from sacred.observers import FileStorageObserver
from sacred.run import Run
from sacred.utils import apply_backspaces_and_linefeeds
from tensorflow.keras.callbacks import History
from texts.models import Trigger
from typing import Callable


name = "computer-nn"
ex = Experiment(name)
ex.captured_out_filter = apply_backspaces_and_linefeeds


@ex.capture
def build(
    context_size: int,
    vocab_size: int,
    embedding_size: int,
    dropout_rate: float,
    units: int,
    num_filters: int,
    kernel_size: int,
    activation: str,
    num_intents: int,
    num_languages: int,
    adamw: dict,
    _log: Logger,
) -> Model:
    """Build model."""
    _log.info("Build nn-model.")

    texts = Input((context_size,), name="text")

    x = Embedding(input_dim=vocab_size, output_dim=embedding_size, mask_zero=True)(
        texts
    )
    x = SpatialDropout1D(rate=dropout_rate)(x)

    tensors = [x]
    for i in range(math.ceil(context_size / 10)):
        x = Concatenate()(tensors)
        x = Conv1D(num_filters, kernel_size, padding="same", activation=activation)(x)
        x = SpatialDropout1D(rate=dropout_rate)(x)
        tensors.append(x)

    inner_model = Model({"text": texts}, {"vec": x}, name="inner_model")
    inner_model.compile(
        loss={
            "vec": "mse",
        },
        optimizer=AdamW(**adamw),
    )
    inner_model.summary()

    # Language Model
    texts = Input((context_size,), name="text")
    x = inner_model(texts)
    x = Conv1D(vocab_size, 1, padding="same", activation="sigmoid", name="next")(
        x["vec"]
    )

    language_model = Model({"text": texts}, {"next": x}, name="language_model")
    language_model.compile(
        loss={
            "next": "mse",
        },
        metrics={
            "next": ["accuracy", "precision", "recall"],
        },
        optimizer=AdamW(**adamw),
    )
    language_model.summary()

    # NLU model
    texts = Input((context_size,), name="text")
    inner_model.trainable = False
    x = inner_model(texts)
    x = Flatten()(x["vec"])

    intents = Dense(num_intents, activation="softmax", name="intent")(x)
    languages = Dense(num_languages, activation="softmax", name="language")(x)

    nlu_model = Model(
        {"text": texts}, {"intent": intents, "language": languages}, name="computer"
    )
    nlu_model.compile(
        loss={
            "intent": "categorical_crossentropy",
            "language": "categorical_crossentropy",
        },
        metrics={
            "intent": ["categorical_accuracy", "precision", "recall"],
            "language": ["categorical_accuracy", "precision", "recall"],
        },
        optimizer=AdamW(**adamw),
    )
    nlu_model.summary(show_trainable=True)
    return inner_model, language_model, nlu_model


@ex.capture
def train(
    model: Model,
    train_gen: PyDataset,
    batch_size: int,
    epochs: int,
    earlystopping: dict,
    reducelronplateau: dict,
    _log: Logger,
    _run: Run,
) -> History:
    """Train model."""
    _log.info("Train model.")
    callbacks = [
        SacredMetricsLogging(_run),
    ]
    callbacks.append(EarlyStopping(**earlystopping))
    callbacks.append(ReduceLROnPlateau(**reducelronplateau))
    return model.fit(
        train_gen,
        batch_size=batch_size,
        epochs=epochs,
        callbacks=callbacks,
    )


@ex.main
def run(texts, batch_size: int, context_size: int, _log: Logger, _run: Run):
    """Run sacred experiment."""
    _log.info("Build datasets.")
    text_train_gen = TextPyDataset(texts, batch_size, context_size, _log)
    vocab_size = len(text_train_gen.vocab) + 1
    _log.info(
        f"Loaded {len(text_train_gen.data)} examples in {len(text_train_gen)} batches."
    )
    _log.info(f"Vocab size: {vocab_size}.")

    intent_train_gen = IntentPyDataset(
        batch_size, context_size, text_train_gen.vocab, _log
    )
    _log.info(
        f"Loaded {len(intent_train_gen.triggers)} triggers in "
        + f"{len(intent_train_gen)} batches."
    )
    _log.info(f"Number of intents: {len(intent_train_gen.mappings['intents'])}.")
    _log.info(f"Number of languages: {len(intent_train_gen.mappings['languages'])}.")

    inner_model, language_model, nlu_model = build(
        vocab_size=vocab_size,
        num_intents=len(intent_train_gen.mappings["intents"]),
        num_languages=len(intent_train_gen.mappings["languages"]),
    )

    language_model_history = train(language_model, text_train_gen)
    nlu_model_history = train(nlu_model, intent_train_gen)

    _log.info("Save experiment")
    _run.observers[0].save_json(language_model_history, "language_model_history.json")
    _run.observers[0].save_json(nlu_model_history, "nlu_model_history.json")
    inner_model.save(f"{_run.observers[0].dir}/inner-model.keras")
    language_model.save(f"{_run.observers[0].dir}/langauge-model.keras")
    nlu_model.save(f"{_run.observers[0].dir}/computer-nn.keras")
    _run.observers[0].save_json(
        {
            "vocab": text_train_gen.vocab,
            "context_size": context_size,
        }
        | intent_train_gen.mappings,
        "mappings.json",
    )

    results = {
        k: nlu_model_history.history[k][-1] for k in nlu_model_history.history.keys()
    }
    return results


class SacredMetricsLogging(Callback):
    """Sacred metrics logging callback."""

    def __init__(self, run: Run):
        """Init."""
        super().__init__()
        self.run = run

    def on_epoch_end(self, epoch: int, logs: dict | None = None):
        """On epoch end."""
        if logs is not None:
            for k, v in logs.items():
                self.run.log_scalar(k, v, epoch)


class IntentPyDataset(PyDataset):
    """Text pydataset."""

    def __init__(
        self,
        batch_size: int,
        context_size: int,
        vocab: dict[str, int],
        _log: Logger,
        **kwargs,
    ):
        """Init."""
        super().__init__(**kwargs)
        self.batch_size = batch_size
        self.context_size = context_size
        self.vocab = vocab

        _log.info(_("Generating data from triggers."))
        entities: dict[str, dict[str, int] | None] = {}
        self.intents = []
        self.languages = []
        progbar = Progbar(Trigger.objects.count(), width=30)
        self.mappings = {
            "intents": {"null": 0},
            "languages": {"null": 0},
        }
        self.triggers = []
        for trigger in Trigger.objects.all():
            if trigger.intent.name not in self.mappings["intents"]:
                self.mappings["intents"][trigger.intent.name] = len(
                    self.mappings["intents"].keys()
                )
            if trigger.language not in self.mappings["languages"]:
                self.mappings["languages"][trigger.language] = len(
                    self.mappings["languages"].keys()
                )
            for triggerentity in trigger.entities.all():
                entity = triggerentity.entity
                parent = triggerentity.entity.parent
                if parent is None:
                    if entity.name not in entities:
                        entities[entity.name] = None
                else:
                    if parent.name not in entities:
                        entities[parent.name] = {entity.name: 0}
                    elif entity.name not in entities[parent.name]:
                        entities[parent.name][entity.name] = len(
                            entities[parent.name].keys()
                        )
            self.triggers.append([self.vocab["<begin of sequence>"]])
            self.triggers[-1] += [
                (
                    self.vocab[j]
                    if j in self.vocab.keys()
                    else self.vocab["<fallback character>"]
                )
                for j in trigger.text
            ]
            self.triggers[-1].append(self.vocab["<end of sequence>"])
            self.languages.append(self.mappings["languages"][trigger.language])
            self.intents.append(self.mappings["intents"][trigger.intent.name])
            progbar.add(1)
        self.indices = np.asarray(list(range(len(self.triggers))), dtype=np.int32)

    def __len__(self) -> int:
        """Get the number of batches in the PyDataset."""
        return math.ceil(len(self.triggers) / self.batch_size)

    def __getitem__(
        self, idx: int
    ) -> tuple[dict[str, npt.NDArray], dict[str, npt.NDArray]]:
        """Get the batch at position `index`."""
        if idx < 0 or len(self) <= idx:
            raise IndexError(
                _("Index %(idx)d out of range for %(class)s with size %(size)d.")
                % {"idx": idx, "class": self.__class__.__name__, "size": len(self)}
            )
        low = idx * self.batch_size
        high = min(low + self.batch_size, len(self.triggers))
        batch_texts = np.zeros(
            (min(self.batch_size, high - low), self.context_size), dtype=np.int32
        )
        batch_languages = np.zeros(
            (min(self.batch_size, high - low), len(self.mappings["languages"])),
            dtype=np.int32,
        )
        batch_intents = np.zeros(
            (min(self.batch_size, high - low), len(self.mappings["intents"])),
            dtype=np.int32,
        )

        i = 0
        for j in self.indices[low:high]:
            for k in range(len(self.triggers[j])):
                batch_texts[i][k] = self.triggers[j][k]
            batch_languages[i] = to_categorical(
                [self.languages[j]], len(self.mappings["languages"])
            )
            batch_intents[i] = to_categorical(
                [self.intents[j]], len(self.mappings["intents"])
            )
            i += 1

        return {"text": batch_texts}, {
            "intent": batch_intents,
            "language": batch_languages,
        }

    def on_epoch_begin(self):
        """At the beginning of every epoch called."""
        self.indices = np.asarray(list(range(len(self.triggers))), dtype=np.int32)
        np.random.shuffle(self.indices)

    def on_epoch_end(self):
        """At the end of every epoch called."""
        pass


class TextPyDataset(PyDataset):
    """Text pydataset."""

    def __init__(
        self,
        paths: list[Path | str],
        batch_size: int,
        context_size: int,
        _log: Logger,
        **kwargs,
    ):
        """Init."""
        super().__init__(**kwargs)
        self.batch_size = batch_size
        self.context_size = context_size

        self.vocab = {
            "<begin of sequence>": 1,
            "<end of sequence>": 2,
            "<fallback character>": 3,
        } | {
            k: i + 4
            for i, k in enumerate(
                [" "]
                + sorted(list(string.ascii_letters), key=lambda x: x.lower())
                + list(string.digits + string.punctuation)
            )
        }

        _log.info(_("Loading texts from files."))
        self.data: list[tuple[list[int], list[int]]] = []
        progbar = Progbar(len(paths), width=30)
        for p in paths:
            if isinstance(p, str):
                p = Path(p)

            fopen: Callable = open
            if p.suffix == ".gz":
                fopen = gzip.open

            texts = []
            with fopen(p, "rt", encoding="utf8") as f:
                if p.suffix == ".json":
                    data = json.loads(f.read())
                    if "title" in data.keys():
                        texts.append(data["title"])
                    if "lead" in data.keys():
                        texts.append(data["lead"])
                    if "text" in data.keys():
                        texts.append(data["text"])
                else:
                    texts.append(f.read().strip())
            for text in texts:
                for i in range(1, len(text) + 2):
                    start = (
                        0 if i <= (self.context_size - 1) else i - (self.context_size)
                    )
                    self.data.append(
                        (
                            ([1] if i <= (self.context_size - 1) else [])
                            + [
                                self.vocab.setdefault(j, len(self.vocab) + 1)
                                for j in text[start:i]
                            ]
                            + ([2] if i > len(text) else []),
                            [
                                self.vocab.setdefault(j, len(self.vocab) + 1)
                                for j in text[
                                    start
                                    + (0 if i <= (self.context_size - 1) else 1) : i
                                    + (1 if i <= len(text) else 0)
                                ]
                            ]
                            + ([2] if i + 1 > len(text) else []),
                        )
                    )
            progbar.add(1)
        self.indices = np.asarray(list(range(len(self.data))), dtype=np.int32)

    def __len__(self) -> int:
        """Get the number of batches in the PyDataset."""
        return math.ceil(len(self.data) / self.batch_size)

    def __getitem__(
        self, idx: int
    ) -> tuple[dict[str, npt.NDArray], dict[str, npt.NDArray]]:
        """Get the batch at position `index`."""
        if idx < 0 or len(self) <= idx:
            raise IndexError(
                _("Index %(idx)d out of range for %(class)s with size %(size)d.")
                % {"idx": idx, "class": self.__class__.__name__, "size": len(self)}
            )
        low = idx * self.batch_size
        high = min(low + self.batch_size, len(self.data))
        batch_text = np.zeros(
            (min(self.batch_size, high - low), self.context_size), dtype=np.int32
        )
        batch_next = np.zeros(
            (min(self.batch_size, high - low), self.context_size, len(self.vocab) + 1),
            dtype=np.int32,
        )

        i = 0
        for j in self.indices[low:high]:
            for k in range(len(self.data[j][0])):
                batch_text[i][k] = self.data[j][0][k]
            for k in range(len(self.data[j][1])):
                batch_next[i][k][self.data[j][1][k]] = 1
            i += 1

        return {"text": batch_text}, {"next": batch_next}

    def on_epoch_begin(self):
        """Method called at the beginning of every epoch."""
        self.indices = np.asarray(list(range(len(self.data))), dtype=np.int32)
        np.random.shuffle(self.indices)


class Command(BaseCommand):
    """Django command to train a new nn model."""

    help = _("Train a new nn-model.")

    def add_arguments(self, parser):
        """Add arguments."""
        parser.add_argument(
            "SACRED_BASEDIR",
            type=lambda p: Path(p).absolute(),
        )
        parser.add_argument(
            "--text-data",
            nargs="+",
            type=lambda p: Path(p).absolute(),
        )
        parser.add_argument(
            "--batch-size",
            default=128,
            type=int,
        )
        parser.add_argument(
            "--epochs",
            default=1000,
            type=int,
        )
        parser.add_argument(
            "--embedding-size",
            default=8,
            type=int,
        )
        parser.add_argument(
            "--dropout-rate",
            default=0.25,
            type=float,
        )
        parser.add_argument(
            "--units",
            default=256,
            type=int,
        )

    def handle(self, *args, **options):
        """Handle command."""
        ex.observers.append(FileStorageObserver(options["SACRED_BASEDIR"]))
        ex.add_config(
            batch_size=options["batch_size"],
            epochs=options["epochs"],
            context_size=100,
            embedding_size=options["embedding_size"],
            dropout_rate=options["dropout_rate"],
            units=options["units"],
            num_filters=5,
            kernel_size=3,
            activation="tanh",
            earlystopping={
                "monitor": "loss",
                "patience": 10,
                "mode": "auto",
                "restore_best_weights": False,
            },
            reducelronplateau={
                "monitor": "loss",
                "factor": 0.5,
                "patience": 5,
                "min_lr": 0.00001,
            },
            adamw={"amsgrad": True},
            texts=options["text_data"],
        )
        ex.run()
