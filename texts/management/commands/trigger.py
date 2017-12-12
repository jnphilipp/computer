# -*- coding: utf-8 -*-

import csv

from countries.models import Language
from django.core.management.base import BaseCommand
from intents.models import Intent
from texts.models import Trigger


class Command(BaseCommand):
    help = 'Import triggers from a csv file.'

    def add_arguments(self, parser):
        parser.add_argument('path', help='CSV file to import.')

    def handle(self, *args, **options):
        with open(options['path'], 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames

            for row in reader:
                language = self._language(row['language'])
                if language is None:
                    continue

                intents = []
                if 'intents' in fieldnames:
                    intents = self._intents(row['intents'])

                trigger, created = Trigger.objects.get_or_create(
                    text=row['trigger'],
                    language=language
                )
                if created:
                    self.stdout.write('* Trigger created: "%s"' % trigger)
                else:
                    self.stderr.write('* Trigger "%s" already exists.' % trigger)

                self.stdout.write('  * Intents: "%s"' % intents)
                trigger.intents.set(intents, clear=True)

    def _language(self, code):
        try:
            return Language.objects.get(code=code)
        except Language.DoesNotExist:
            self.stderr.write('Language "%s" not found.' %
                              row['language'])
            return None

    def _intents(self, value):
        intents = []
        for name in value.split(';'):
            try:
                intents.append(Intent.objects.get(name=name))
            except Intent.DoesNotExist:
                self.stderr.write('Intent "%s" not found.' % name)
        return intents
