import os
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'My custom command'

    def handle(self, *args, **options):
        # Delete all existing migration files
        self.delete_migration_files()

    def delete_migration_files(self):
        # Get the root directory of your Django project
        project_root = os.getcwd()

        # Traverse all apps in the project
        for root, dirs, files in os.walk(project_root):
            for file in files:
                # Check if the file is a migration file
                if file.endswith('.py') and 'migrations' in root and "__init__" not in file:
                    # Delete the migration file
                    os.remove(os.path.join(root, file))

        self.stdout.write(self.style.SUCCESS('Deleted all migration files'))
