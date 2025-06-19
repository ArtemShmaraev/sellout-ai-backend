from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Execute custom SQL query'

    def handle(self, *args, **kwargs):
        query = "DELETE FROM django_migrations;"

        with connection.cursor() as cursor:
            cursor.execute(query)

        self.stdout.write(self.style.SUCCESS('Successfully executed custom SQL query.'))
