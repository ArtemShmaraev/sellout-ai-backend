import os
from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch

from products.models import Product


class Command(BaseCommand):
    help = 'My custom command'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.brands = None

    def handle(self, *args, **options):
        # Delete all existing migration files
        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

        # Название индекса
        index_name = 'my_index'

        # Создание индекса
        index_body = {
            'mappings': {
                'properties': {
                    'suggest': {
                        'type': 'completion',
                        'contexts': [
                            {
                                'name': 'weight',
                                'type': 'integer'
                            }
                        ]
                    }
                }
            }
        }

        # Создание индекса
        es.indices.create(index=index_name, body=index_body)
        suggest = set()
        products = Product.objects.all()
        # Данные для заполнения индекса
        for product in products:
            s1 = ' '.join([x.name for x in product.brands.all()])
            if s1 not in suggest:
                data = {'suggest': {'input': s1, 'weight': 1000 - len(s1) - len(product.brands.all()) * 30}}
                suggest.add(s1)
                es.index(index=index_name, body=data)


            s2 = product.model
            if s2 not in suggest:
                data = {'suggest': {'input': s2, 'weight': 800 - len(s2)}}
                suggest.add(s2)
                es.index(index=index_name, body=data)

            s3 = product.colorway
            if s3 not in suggest:
                data = {'suggest': {'input': s3, 'weight': 500 - len(s3)}}
                suggest.add(s3)
                es.index(index=index_name, body=data)


            if product.main_line:
                s4 = product.main_line.view_name
                if s4 not in suggest:
                    data = {'suggest': {'input': s4, 'weight': 800 - len(s4)}}
                    suggest.add(s4)
                    es.index(index=index_name, body=data)

            s5 = f"{s1} {s2}"
            if s5 not in suggest:
                data = {'suggest': {'input': s5, 'weight': 400 - len(s5)}}
                suggest.add(s5)
                es.index(index=index_name, body=data)

            s6 = f"{s1} {s2} {s3}"
            if s6 not in suggest:
                data = {'suggest': {'input': s6, 'weight': 300 - len(s6)}}
                suggest.add(s6)
                es.index(index=index_name, body=data)

            s7 = f"{s2} {s3}"
            if s7 not in suggest:
                data = {'suggest': {'input': s7, 'weight': 300 - len(s7)}}
                suggest.add(s7)
                es.index(index=index_name, body=data)




            data = {'suggest': {'input': 'подсказка 1', 'weight': 5}}
            es.index(index=index_name, body=data)
        data = [
            {'suggest': 'подсказка 1'},
            {'suggest': 'подсказка 2'},
            {'suggest': 'подсказка 3'},
            {'suggest': 'подсказка 4'},
            {'suggest': 'подсказка 5'}
        ]

        # Заполнение данных в индексе
        for item in data:
            es.index(index=index_name, body=item)

        # Подтверждение создания и заполнения индекса
        print("Индекс успешно создан и заполнен данными.")
