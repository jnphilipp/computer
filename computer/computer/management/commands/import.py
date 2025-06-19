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
"""Computer Django app import command."""

import json
import sys

from argparse import FileType
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from intents.models import Intent
from texts.models import Answer, Attribute, Entity, Trigger, TriggerEntity


class Command(BaseCommand):
    """Export data."""

    help = _("Export data.")

    def add_arguments(self, parser):
        """Command arguments."""
        parser.add_argument(
            "input",
            nargs="?",
            type=FileType("r", encoding="utf8"),
            default=sys.stdout,
        )

    def handle(self, *args, **options):
        """Handle command."""
        data = json.loads(options["input"].read())
        for i in data["triggers"]:
            intent, _ = Intent.objects.get_or_create(name=i["intent"]["name"])
            for j in i["intent"]["answers"]:
                answer, _ = Answer.objects.get_or_create(
                    text=j["text"], language=j["language"]
                )
                intent.answers.add(answer)
                for k in j["attributes"]:
                    attribute, _ = Attribute.objects.get_or_create(
                        key=k["key"], value=k["value"]
                    )
                    answer.attributes.add(attribute)
            trigger, _ = Trigger.objects.get_or_create(
                text=i["text"], language=i["language"], intent=intent
            )
            for j in i["entities"]:
                entity = self._create_entity(j["entity"])
                triggerentity, _ = TriggerEntity.objects.get_or_create(
                    start=j["start"],
                    end=j["end"],
                    value=j["value"],
                    entity=entity,
                    trigger=trigger,
                )

    def _create_entity(self, data) -> Entity:
        parent = None
        if data["parent"] is not None:
            parent = self._create_entity(data["parent"])
        entity, _ = Entity.objects.get_or_create(name=data["name"], parent=parent)
        return entity
