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
"""Texts Django app trigger command."""

import csv

from django.core.management.base import BaseCommand
from intents.models import Intent
from texts.models import Trigger


class Command(BaseCommand):
    """Trigger command."""

    help = "Import triggers from a csv file."

    def add_arguments(self, parser):
        """Add arguments."""
        parser.add_argument("path", help="CSV file to import.")

    def handle(self, *args, **options):
        """Handle."""
        with open(options["path"], "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames

            for row in reader:
                intents = []
                if "intents" in fieldnames:
                    intents = self._intents(row["intents"])

                trigger, created = Trigger.objects.get_or_create(
                    text=row["trigger"], language=row["language"]
                )
                if created:
                    self.stdout.write('* Trigger created: "%s"' % trigger)
                else:
                    self.stderr.write('* Trigger "%s" already exists.' % trigger)

                self.stdout.write('  * Intents: "%s"' % intents)
                trigger.intents.set(intents, clear=True)

    def _intents(self, value):
        intents = []
        for name in value.split(";"):
            try:
                intents.append(Intent.objects.get(name=name))
            except Intent.DoesNotExist:
                self.stderr.write('Intent "%s" not found.' % name)
        return intents
