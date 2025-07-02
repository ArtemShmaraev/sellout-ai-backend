from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'My custom command'

    def handle(self, *args, **options):
        # Выполнение команды python manage.py makemigrations


        # Выполнение команды python manage.py add_cat

        call_command('delete_db')
        call_command('add_cat')
        call_command('add_line')
        # Выполнение команды python manage.py add_size_table

        call_command('add_color')
        call_command('add_material')
        call_command('add_size_table')
        call_command('add_text_for_header')

        # Выполнение команды python manage.py add_sg
        # call_command('add_sg')

        print('All commands executed successfully.')
