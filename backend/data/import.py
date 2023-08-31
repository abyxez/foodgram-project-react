import csv
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
import django
from pathlib import Path
from typing import Any, Optional
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient

CSV_INGREDIENTS = Path(settings.BASE_DIR).parent / 'data' / 'ingredients.csv'


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> str | None:
        try:
            with open(CSV_INGREDIENTS, 'r', encoding='utf-8') as csv_file:
                rows = csv.reader(csv_file)
                for row in rows:
                    name, measurement_unit = row
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit,
                    )
        except FileNotFoundError:
            raise CommandError('CSV File not found.')
        self.stdout.write('Imported successfully.')
