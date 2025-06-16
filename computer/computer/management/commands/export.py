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
"""Computer Django app export command."""

import json
import string
import sys

from argparse import FileType
from csv import DictWriter
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from texts.models import Trigger


class Command(BaseCommand):
    help = _("Export texts for training.")

    def add_arguments(self, parser):
        parser.add_argument("--meta", type=FileType("w", encoding="utf8"))
        parser.add_argument(
            "dataset",
            nargs="?",
            type=FileType("w", encoding="utf8"),
            default=sys.stdout,
        )

    def handle(self, *args, **options):
        def to_categorial(idx, num_classes):
            x = ["0"] * num_classes
            x[idx] = "1"
            return x

        vocab = {
            k: i + 2
            for i, k in enumerate(
                [" "]
                + sorted(list(string.ascii_letters), key=lambda x: x.lower())
                + list(string.digits + string.punctuation)
            )
        }

        entities = {}
        intent = {"null": 0}
        language = {"null": 0}
        triggers = []
        for trigger in Trigger.objects.all():
            for i in set(list(trigger.text)):
                if i not in vocab.keys():
                    vocab[i] = len(vocab) + 2
            if trigger.intent.name not in intent:
                intent[trigger.intent.name] = len(intent.keys())
            if trigger.language.code not in language:
                language[trigger.language.code] = len(language.keys())
            for entity in trigger.entities.all():
                if entity.entity.parent is None:
                    if entity.entity.name not in entities:
                        entities[entity.entity.name] = None
                elif entity.entity.parent.name not in entities:
                    entities[entity.entity.parent.name] = {entity.entity.name: 0}
                elif entity.entity.name not in entities[entity.entity.parent.name]:
                    entities[entity.entity.parent.name][entity.entity.name] = len(
                        entities[entity.entity.parent.name].keys()
                    )
            triggers.append(trigger.to_dict())

        max_id = max(vocab.values()) + 1
        min_len = None
        max_len = None
        writer = DictWriter(
            options["dataset"], ["text", "language", "intent"], dialect="unix"
        )
        writer.writeheader()
        for trigger in triggers:
            if min_len is None:
                min_len = len(trigger["text"])
            else:
                min_len = min(min_len, len(trigger["text"]))
            if max_len is None:
                max_len = len(trigger["text"])
            else:
                max_len = max(max_len, len(trigger["text"]))

            row = {
                "text": ",".join(
                    [
                        str(vocab[j] if j in vocab.keys() else max_id)
                        for j in trigger["text"]
                    ]
                ),
                "language": ",".join(
                    to_categorial(language[trigger["language"]], len(language))
                ),
                "intent": ",".join(
                    to_categorial(intent[trigger["intent"]], len(intent))
                ),
            }
            writer.writerow(row)
        with open("./data/de.txt", "r", encoding="utf8") as f:
            for line in f:
                row = {
                    "text": ",".join(
                        [
                            str(vocab[j] if j in vocab.keys() else max_id)
                            for j in line.strip()
                        ]
                    ),
                    "language": ",".join(to_categorial(language["de"], len(language))),
                    "intent": ",".join(to_categorial(0, len(intent))),
                }
                writer.writerow(row)
        with open("./data/en.txt", "r", encoding="utf8") as f:
            for line in f:
                row = {
                    "text": ",".join(
                        [
                            str(vocab[j] if j in vocab.keys() else max_id)
                            for j in line.strip()
                        ]
                    ),
                    "language": ",".join(to_categorial(language["en"], len(language))),
                    "intent": ",".join(to_categorial(0, len(intent))),
                }
                writer.writerow(row)
        with open("./data/fr.txt", "r", encoding="utf8") as f:
            for line in f:
                row = {
                    "text": ",".join(
                        [
                            str(vocab[j] if j in vocab.keys() else max_id)
                            for j in line.strip()
                        ]
                    ),
                    "language": ",".join(to_categorial(0, len(language))),
                    "intent": ",".join(to_categorial(0, len(intent))),
                }
                writer.writerow(row)
        with open("./data/es.txt", "r", encoding="utf8") as f:
            for line in f:
                row = {
                    "text": ",".join(
                        [
                            str(vocab[j] if j in vocab.keys() else max_id)
                            for j in line.strip()
                        ]
                    ),
                    "language": ",".join(to_categorial(0, len(language))),
                    "intent": ",".join(to_categorial(0, len(intent))),
                }
                writer.writerow(row)

        if options["meta"]:
            options["meta"].write(
                json.dumps(
                    {
                        "vocab": vocab,
                        "entities": entities,
                        "intent": intent,
                        "language": language,
                    },
                    ensure_ascii=False,
                    indent=4,
                )
            )
