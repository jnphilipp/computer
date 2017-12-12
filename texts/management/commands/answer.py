# -*- coding: utf-8 -*-

import csv

from countries.models import Language
from django.core.management.base import BaseCommand
from intents.models import Intent
from texts.models import Answer, Attribute


class Command(BaseCommand):
    help = 'Import answers from a csv file.'

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

                attributes = []
                if 'attributes' in fieldnames:
                    attributes = self._attributes(row['attributes'])

                intents = []
                if 'intents' in fieldnames:
                    intents = self._intents(row['intents'])

                answer, created = Answer.objects.get_or_create(
                    text=row['answer'],
                    language=language
                )
                if created:
                    self.stdout.write('* Answer created: "%s"' % answer)
                else:
                    self.stderr.write('* Answer "%s" already exists.' % answer)

                self.stdout.write('  * Attributes: "%s"' % attributes)
                answer.attributes.set(attributes, clear=True)
                self.stdout.write('  * Intents: "%s"' % intents)
                answer.intents.set(intents, clear=True)

    def _language(self, code):
        try:
            return Language.objects.get(code=code)
        except Language.DoesNotExist:
            self.stderr.write('Language "%s" not found.' %
                              row['language'])
            return None

    def _attributes(self, value):
        attrs = []
        for attr in value.split(';'):
            if '=' in attr:
                try:
                    k, v = attr.split('=')
                    attrs.append(Attribute.objects.get(key=k, value=v))
                except Attribute.DoesNotExist:
                    self.stderr.write('Attribute "%s=%s" not found.' % k, v)
            else:
                try:
                    attrs.append(Attribute.objects.get(key=attr))
                except Attribute.DoesNotExist:
                    self.stderr.write('Attribute "%s" not found.' % attr)
        return attrs

    def _intents(self, value):
        intents = []
        for name in value.split(';'):
            try:
                intents.append(Intent.objects.get(name=name))
            except Intent.DoesNotExist:
                self.stderr.write('Intent "%s" not found.' % name)
        return intents
