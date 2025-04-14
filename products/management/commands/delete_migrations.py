import os
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'My custom command'

    def handle(self, *args, **options):
        # Delete all existing migration files
        self.delete_migration_files()

        # Execute the makemigrations command
        call_command('makemigrations')

        # Execute the migrate command
        call_command('migrate')

    def delete_migration_files(self):
        # Run the shell command to delete migration files
        os.system('find . -path "*/migrations/*.py" -not -name "__init__.py" -delete')
        self.stdout.write(self.style.SUCCESS('Deleted all migration files'))