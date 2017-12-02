# -*- coding: utf-8 -*-

import json

from django.core.management.base import BaseCommand
from texts.models import Text


class Command(BaseCommand):
    help = 'Export texts for training.'

    def add_arguments(self, parser):
        parser.add_argument('--file', help='Output file')

    def handle(self, *args, **options):
        common_examples = []
        for text in Text.objects.all():
            common_examples.append(text.to_dict())

        regex_features = []
        entity_synonyms = []

        data = json.dumps({
            'common_examples': common_examples,
            'regex_features': regex_features,
            'entity_synonyms': entity_synonyms,
        })

        if options['file']:
            with open(options['file'], 'w', encoding='utf-8') as f:
                f.write(data)
                f.write('\n')
        else:
            print(data)
