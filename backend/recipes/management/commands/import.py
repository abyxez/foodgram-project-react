import csv
import os
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


def read(file_name):
    csv_path = os.path.join(settings.BASE_DIR, file_name)
    csv_file = open(csv_path, encoding='utf-8')
    csv_reader = csv.reader(csv_file, delimiter=',')
    return csv_reader


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> str | None:
        reader = read('copy.csv')
        i = 1
        for row in reader:
            obj, created = Ingredient.objects.get_or_create(
                id=i,
                name=row[0],
                measurement_unit=row[1],
            )
            i += 1
        print(' Success !')
