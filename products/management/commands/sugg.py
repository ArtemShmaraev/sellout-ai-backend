from django.core.management.base import BaseCommand
from elasticsearch_dsl import Search

class Command(BaseCommand):
    help = 'Get all suggestions from Line, Category, and Product indexes'

    def handle(self, *args, **options):
        def get_all_suggestions(index_name):
            search = Search(index=index_name)
            search = search.suggest('all_suggestions', '', completion={
                'field': 'suggest',
                'size': 1000
            })

            response = search.execute()

            all_suggestions = []

            if response.suggest.all_suggestions[0].options:
                all_suggestions = [option.text for option in response.suggest.all_suggestions[0].options]

            return all_suggestions

        # Получение всех подсказок из индексов
        all_line_suggestions = get_all_suggestions('line_index')
        self.stdout.write(self.style.SUCCESS("All Line Suggestions:"))
        for suggestion in all_line_suggestions:
            self.stdout.write(self.style.SUCCESS(suggestion))

