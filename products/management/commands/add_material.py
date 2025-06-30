import json
from django.core.management.base import BaseCommand
from products.models import Material

class Command(BaseCommand):
    help = 'Fill Color model with data from a JSON file'

    def handle(self, *args, **kwargs):

        with open('material.json', 'r', encoding="utf-8") as file:
            data = json.load(file)

        for k, v in data.items():
            material, created = Material.objects.get_or_create(
                name=v, eng_name=k
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Material "{material}" created'))
            else:
                self.stdout.write(self.style.WARNING(f'Materiak "{material}" already exists'))
