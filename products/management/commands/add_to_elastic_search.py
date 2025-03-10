from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from django.core.management.base import BaseCommand
from products.models import Product  # Замените "your_app" на название вашего Django-приложения
import requests


class Command(BaseCommand):
    help = 'Indexes products in Elasticsearch'

    def handle(self, *args, **options):
        # Установите подключение к Elasticsearch
        es = Elasticsearch(['http://51.250.2.233:9200'])  # Замените 'localhost' на адрес вашего Elasticsearch-узла

        # Получите все продукты из базы данных Django
        products = Product.objects.all()
        k = 0
        kk = 0
        for product in products:
            kk += 1
            search = f"{' x '.join([x.name for x in product.brands.all()])} {product.model} {product.colorway}"
            data = {
                "query": {
                    "multi_match": {
                        "query": search,
                        "fields": ["brand", "model", "colorway"],
                        "fuzziness": 0
                    }
                }
            }

            actions = [
                {
                    '_index': 'products',  # Замените 'products' на имя вашего индекса Elasticsearch
                    '_id': product.id,
                    '_source': {
                        'brand': ' x '.join([x.name for x in product.brands.all()]),
                        'model': product.model,
                        'colorway': product.colorway
                        # Добавьте другие поля продукта, которые вы хотите индексировать
                    }
                }
            ]

            # Индексируйте продукты в Elasticsearch
            bulk(es, actions)


            # Отправьте запрос поиска
            response = es.search(index='products',
                                 body=data)  # Замените 'products' на имя вашего индекса Elasticsearch

            f = False
            for hit in response['hits']['hits'][:7]:
                if search != f"{hit['_source']['brand']} {hit['_source']['model']} {hit['_source']['colorway']}":
                    f = True
                    break
            if not f:
                print(search)
                k += 1
            print(k, kk, round(k/kk * 100, 3))



        # # Соберите данные продуктов для индексации в Elasticsearch
        # actions = [
        #     {
        #         '_index': 'products',  # Замените 'products' на имя вашего индекса Elasticsearch
        #         '_id': product.id,
        #         '_source': {
        #             'brand': ' x '.join([x.name for x in product.brands.all()]),
        #             'model': product.model,
        #             'colorway': product.colorway
        #             # Добавьте другие поля продукта, которые вы хотите индексировать
        #         }
        #     }
        #     for product in products
        # ]
        # print(len(actions))
        #
        # # Индексируйте продукты в Elasticsearch
        # bulk(es, actions)

        self.stdout.write(self.style.SUCCESS('Products indexed successfully!'))
