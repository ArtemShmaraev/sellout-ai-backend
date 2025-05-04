import json
from django.core.management.base import BaseCommand
from products.models import Color

class Command(BaseCommand):
    help = 'Fill Color model with data from a JSON file'

    def handle(self, *args, **kwargs):

        with open('colors.json', 'r', encoding="utf-8") as file:
            colors_data = json.load(file)
        colors = Color.objects.all()
        k = 0
        for color in colors:
            k += 1
            if k != 1:
                color.delete()


        for color_data in colors_data:
            color, created = Color.objects.get_or_create(
                id=color_data['id'],
                defaults={
                    'name': color_data['name'],
                    'is_main_color': color_data['is_main_color'],
                    'russian_name': color_data['russian_name'],
                    'hex': color_data['hex']
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Color "{color}" created'))
            else:
                self.stdout.write(self.style.WARNING(f'Color "{color}" already exists'))
