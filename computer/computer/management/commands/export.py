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
import sys

from argparse import FileType
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from texts.models import Trigger


class Command(BaseCommand):
    """Export data."""

    help = _("Export data.")

    def add_arguments(self, parser):
        """Command arguments."""
        parser.add_argument(
            "output",
            nargs="?",
            type=FileType("w", encoding="utf8"),
            default=sys.stdout,
        )

    def handle(self, *args, **options):
        """Handle command."""
        data = {"triggers": []}
        for trigger in Trigger.objects.all():
            data["triggers"].append(trigger.to_dict())
        options["output"].write(json.dumps(data, ensure_ascii=False, indent=4))
        options["output"].write("\n")
