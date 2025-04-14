from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'My custom command'

    def handle(self, *args, **options):
        # Выполнение команды python manage.py makemigrations
        call_command('flush')

        call_command('delete_migrations')

        call_command('makemigrations')

        # Выполнение команды python manage.py migrate
        call_command('migrate')

        # Выполнение команды python manage.py add_cat
        call_command('add_cat')

        # Выполнение команды python manage.py add_size_table
        call_command('add_size_table')

        # Выполнение команды python manage.py add_sg
        call_command('add_sg')

        print('All commands executed successfully.')
