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
    Bidirectional,
    Dense,
    Embedding,
    GRU,
    SpatialDropout1D,
)
from keras.optimizers import AdamW
from keras.utils import PyDataset, to_categorical
from logging import Logger
from pathlib import Path
from sacred import Experiment
from sacred.observers import FileStorageObserver
from sacred.run import Run
from sacred.utils import apply_backspaces_and_linefeeds
from tensorflow.keras.callbacks import History
from texts.models import Trigger


name = "computer-nn"
ex = Experiment(name)
ex.captured_out_filter = apply_backspaces_and_linefeeds


@ex.capture
def build(
    vocab_size: int,
    embedding_size: int,
    dropout_rate: float,
    units: int,
    num_intents: int,
    num_languages: int,
    adamw: dict,
    _log: Logger,
) -> Model:
    """Build model."""
    _log.info("Build nn-model.")

    texts = Input((None,), name="text")

    x = Embedding(input_dim=vocab_size, output_dim=embedding_size, mask_zero=True)(
        texts
    )
    x = SpatialDropout1D(rate=dropout_rate)(x)
    x = Bidirectional(
        GRU(
            units,
            dropout=dropout_rate,
            recurrent_dropout=dropout_rate,
        )
    )(x)
    intents = Dense(num_intents, activation="softmax", name="intent")(x)
    languages = Dense(num_languages, activation="softmax", name="language")(x)

    model = Model(
        {"text": texts}, {"intent": intents, "language": languages}, name="computer"
    )
    model.compile(
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
    model.summary()
    return model


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
def run(batch_size, _log: Logger, _run: Run):
    """Run sacred experiment."""
    _log.info("Build dataset.")
    train_gen = IntentPyDataset(batch_size)

    vocab_size = len(train_gen.vocab) + 1
    _log.info(f"Loaded {len(train_gen.texts)} texts in {len(train_gen)} batches.")
    _log.info(f"Vocab size: {vocab_size}.")
    _log.info(f"Min input length: {train_gen.min_len}.")
    _log.info(f"Max input length: {train_gen.max_len}.")
    _log.info(f"Number of intents: {len(train_gen.mappings['intents'])}.")
    _log.info(f"Number of languages: {len(train_gen.mappings['languages'])}.")

    model = build(
        vocab_size=vocab_size,
        num_intents=len(train_gen.mappings["intents"]),
        num_languages=len(train_gen.mappings["languages"]),
    )

    history = train(model, train_gen)

    _log.info("Save experiment")
    _run.observers[0].save_json(history, "history.json")
    model.save(f"{_run.observers[0].dir}/computer-nn.keras")
    _run.observers[0].save_json(
        {
            "vocab": train_gen.vocab,
            "max_len": train_gen.max_len,
            "min_len": train_gen.min_len,
        }
        | train_gen.mappings,
        "mappings.json",
    )

    results = {k: history.history[k][-1] for k in history.history.keys()}
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
        **kwargs,
    ):
        """Init."""
        super().__init__(**kwargs)
        self.batch_size = batch_size

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

        entities: dict[str, dict[str, int] | None] = {}
        self.mappings = {
            "intents": {"null": 0},
            "languages": {"null": 0},
        }
        triggers = []
        for trigger in Trigger.objects.all():
            for i in set(list(trigger.text)):
                if i not in self.vocab.keys():
                    self.vocab[i] = len(self.vocab) + 1
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
            data = trigger.to_dict()
            data["intent"] = data["intent"]["name"]
            triggers.append(data)

        self.max_len = self.min_len = len(triggers[0]["text"]) + 2
        self.intents = []
        self.languages = []
        self.texts = []
        for trigger in triggers:
            self.min_len = min(self.min_len, len(trigger["text"]) + 2)
            self.max_len = max(self.max_len, len(trigger["text"]) + 2)

            self.texts.append([self.vocab["<begin of sequence>"]])
            self.texts[-1] += [
                (
                    self.vocab[j]
                    if j in self.vocab.keys()
                    else self.vocab["<fallback character>"]
                )
                for j in trigger["text"]
            ]
            self.texts[-1].append(self.vocab["<end of sequence>"])
            self.languages.append(self.mappings["languages"][trigger["language"]])
            self.intents.append(self.mappings["intents"][trigger["intent"]])
        self.indices = np.asarray(list(range(len(self.texts))), dtype=np.int32)

    def __len__(self) -> int:
        """Get the number of batches in the PyDataset."""
        return math.ceil(len(self.texts) / self.batch_size)

    def __getitem__(
        self, idx: int
    ) -> tuple[dict[str, npt.NDArray], dict[str, npt.NDArray]]:
        """Get the batch at position `index`."""
        low = idx * self.batch_size
        high = min(low + self.batch_size, len(self.texts))
        batch_texts = np.zeros((self.batch_size, self.max_len), dtype=np.int32)
        batch_languages = np.zeros(
            (self.batch_size, len(self.mappings["languages"])),
            dtype=np.int32,
        )
        batch_intents = np.zeros(
            (self.batch_size, len(self.mappings["intents"])),
            dtype=np.int32,
        )

        i = 0
        for j in self.indices[low:high]:
            for k in range(len(self.texts[j])):
                batch_texts[i][k] = self.texts[j][k]
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
        self.indices = np.asarray(list(range(len(self.texts))), dtype=np.int32)
        np.random.shuffle(self.indices)

    def on_epoch_end(self):
        """At the end of every epoch called."""
        pass


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
            embedding_size=options["embedding_size"],
            dropout_rate=options["dropout_rate"],
            units=options["units"],
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
        )
        ex.run()
