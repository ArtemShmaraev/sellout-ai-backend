import json

from django.shortcuts import render
from elasticsearch_dsl.query import Match, MoreLikeThis

from .models import Line, Category, Color, Collab, Product
from .serializers import ProductMainPageSerializer
from elasticsearch_dsl import Search
from django.db.models import Case, When, Value, IntegerField
from elasticsearch_dsl.search import Search, Q

from .documents import LineDocument


def search_line(query):
    index_name = 'line_index'

    # Создайте объект Search и настройте подсказки
    search = Search(index=index_name)
    search = search.suggest(
        'line_suggestions',
        query,  # Здесь замените на ваш поисковый запрос
        completion={'field': 'suggest', "size": 7}
    )

    # search = search.source(includes=['suggest'])
    #
    # # Выполните поиск и получите результаты
    # response = search.execute()
    # print("---------------------------")
    # # Выведите все значения поля 'suggest'
    # for hit in response.hits:
    #     print(hit.suggest.input[0])

    # Выполните поиск и получите результаты подсказок
    response = search.execute()
    suggestions = response.suggest.line_suggestions[0]['options']
    s = []
    # Выведите список подсказок
    for suggestion in suggestions:
        s.append(suggestion['_source']['suggest']['input'][0])
    return s

def similar_product(product):
    search = Search(index='product_index')  # Замените на имя вашего индекса
    search = search.query(MoreLikeThis(like={'_id': product.id},
                                       fields=['brands', 'categories', 'lines', 'model', 'colorway', 'collab', 'gender']))

    # search = search[:1000]

    # Выполните запрос
    response = search.execute()

    output_file = 'similar_results.json'
    with open(output_file, 'w', encoding="utf-8") as f:
        json.dump(response.to_dict(), f, indent=4)
    # max_score = response.hits.max_score
    # threshold = 0.6 * max_score

    product_ids = [hit.meta.id for hit in response.hits]
    queryset = Product.objects.filter(id__in=product_ids)

    # Определение порядка объектов в queryset
    preserved_order = Case(
        *[
            When(id=pk, then=pos) for pos, pk in enumerate(product_ids)
        ],
        default=Value(len(product_ids)),
        output_field=IntegerField()
    )

    # Применение порядка к queryset
    queryset = queryset.annotate(order=preserved_order).order_by('order')
    return queryset


def search_product(query, queryset, page_number=1):
    search = Search(index='product_index')
    # search = search.query(
    #     'bool',
    #     should=[
    #         {'match': {'manufacturer_sku': {'query': query, 'boost': 1, 'fuzziness': 'AUTO'}}},
    #         {'match': {'model': {'query': query, 'boost': 3, 'fuzziness': 'AUTO'}}},
    #         {'match': {'lines': {'query': query, 'boost': 2, 'fuzziness': 'AUTO'}}},
    #         {'match': {'colorway': {'query': query, 'boost': 1, 'fuzziness': 'AUTO'}}},
    #         {'match': {'collab': {'query': query, 'boost': 4, 'fuzziness': 'AUTO'}}},
    #         {'match': {'categories': {'query': query, 'boost': 3, 'fuzziness': 'AUTO'}}},
    #         {'match': {'brands': {'query': query, 'boost': 4, 'fuzziness': 'AUTO'}}}
    #     ]
    # )

    search = search.query('bool',
                          must=[Q(
                              'multi_match',
                              query=query,
                              type="most_fields",
                              fields=['manufacturer_sku^1', 'model^3', 'lines^2', 'colorway^1',
                                      "collab^4", "categories^3", 'brands^4'],
                              # Установите вес для каждого поля
                              fuzziness=0)],
                          # filter=Q('ids', values=list(queryset.values_list('id', flat=True)))
                          )

    # search = search.query(
    #     'multi_match',
    #     query=query,
    #     fields=['manufacturer_sku^1', 'model^5', 'lines^3', 'russian_name^1', 'colorway^2', 'brands^5'],
    #     # Установите вес для каждого поля
    #     fuzziness='AUTO',
    #     filter=queryset.query
    # )

    search = search[:1000]

    response = search.execute()
    # Определите пороговое значение для подходящих результатов (50% от max_score)

    # Запись результатов в JSON файл
    output_file = 'search_results.json'
    with open(output_file, 'w', encoding="utf-8") as f:
        json.dump(response.to_dict(), f, indent=4)
    max_score = response.hits.max_score
    threshold = min(len(query) / 25, 0.8) * max_score
    product_ids = [hit.meta.id for hit in response.hits if hit.meta.score > threshold]
    queryset = Product.objects.filter(id__in=product_ids)

    # Определение порядка объектов в queryset
    preserved_order = Case(
        *[
            When(id=pk, then=pos) for pos, pk in enumerate(product_ids)
        ],
        default=Value(len(product_ids)),
        output_field=IntegerField()
    )

    # Применение порядка к queryset
    queryset = queryset.annotate(order=preserved_order).order_by('order')

    # count = response.hits.total.value
    # start_index = (page_number - 1) * 60
    # queryset = response.hits[start_index:start_index + 60]
    #
    # product_ids = [hit.meta.id for hit in queryset]
    # queryset = Product.objects.filter(id__in=product_ids).order_by('id')

    # search_line = search_best_line(query)
    # search_category = search_best_category(query)
    # search_color = search_best_color(query)
    # search_collab = search_best_collab(query)
    res = {"queryset": queryset}
    url = "?"
    # if search_collab:
    #     url += f"collab={search_collab.name}&"
    #     res['collab'] = search_collab.name
    # if search_category:
    #     url += f"category={search_category.eng_name}&"
    #     res['category'] = search_category.eng_name
    # if search_line:
    #     url += f"line={search_line.full_eng_name}&"
    #     res['line'] = search_line.full_eng_name
    # if search_color:
    #     url += f"color={search_color.name}&"
    #     res['color'] = search_color.name
    res['url'] = url

    print(queryset.count())
    return res


def search_best_line(query_string):
    search = Search(index='line_index')
    search = search.query(
        'multi_match',
        query=query_string,
        fields=['name'],  # Поле для поиска
        fuzziness='AUTO'
    )
    # search = search.sort('_score')  # Сортировка по рейтингу убывающим образом
    response = search.execute()

    if response:
        print("Line", Line.objects.get(id=response.hits[0].meta.id).name, response.hits.max_score)
        return Line.objects.get(id=response.hits[0].meta.id)

    return None


def search_best_category(query_string):
    search = Search(index='category_index')
    search = search.query(
        'multi_match',
        query=query_string,
        fields=['name'],  # Поле для поиска
        fuzziness='AUTO'
    )
    # search = search.sort('_score')  # Сортировка по рейтингу убывающим образом
    response = search.execute()

    if response:
        print("Category", Category.objects.get(id=response.hits[0].meta.id).name, response.hits.max_score)
        return Category.objects.get(id=response.hits[0].meta.id)
    return None


def search_best_color(query_string):
    search = Search(index='color_index')
    search = search.query(
        'multi_match',
        query=query_string,
        fields=['russian_name'],  # Поле для поиска
        fuzziness='AUTO'
    )
    # search = search.sort('_score')  # Сортировка по рейтингу убывающим образом
    response = search.execute()

    if response:
        print("Color", Color.objects.get(id=response.hits[0].meta.id).name, response.hits.max_score)
        return Color.objects.get(id=response.hits[0].meta.id)
    return None


def search_best_collab(query_string):
    search = Search(index='collab_index')
    search = search.query(
        'multi_match',
        query=query_string,
        fields=['name'],  # Поле для поиска
        fuzziness='AUTO'
    )
    # search = search.sort('_score')  # Сортировка по рейтингу убывающим образом
    response = search.execute()

    if response:
        if response.hits[0].meta.score > 5:
            print("Collab", Collab.objects.get(id=response.hits[0].meta.id).name, response.hits.max_score)
            return Collab.objects.get(id=response.hits[0].meta.id)
        return None
    return None
