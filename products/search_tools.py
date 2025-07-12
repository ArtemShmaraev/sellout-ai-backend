import json

from django.shortcuts import render
from elasticsearch_dsl.query import Match, MoreLikeThis

from .models import Line, Category, Color, Collab, Product
from .serializers import ProductMainPageSerializer
from elasticsearch_dsl import Search
from django.db.models import Case, When, Value, IntegerField
from elasticsearch_dsl.search import Search, Q

from .documents import LineDocument


def suggest_search(query):
    index_name = 'suggest_index'

    # Создайте объект Search и настройте подсказки
    search = Search(index=index_name)
    s = search.suggest('user-input-suggestions', query, completion={'field': 'suggest', 'size': 100, 'fuzzy': {
        'fuzziness': 'AUTO'
    }})

    # Выполнение запроса
    response = s.execute()

    # Извлечение подсказок из ответа
    suggestions = response.suggest['user-input-suggestions'][0]['options']
    sp = []

    # Вывод подсказок
    for suggestion in suggestions:
        sp.append({"name": suggestion._source.name, "type": suggestion._source.type, "url": suggestion._source.url})
    return sp

    # Извлечение всех подсказок из ответа
    # suggestions = response.suggest['all-suggestions'][0]['options']

    # Вывод всех подсказок
    # for suggestion in suggestions:
    #     print(suggestion.text)


def similar_product(product):
    search = Search(index='product_index')  # Замените на имя вашего индекса
    search = search.query(
        MoreLikeThis(
            like={'_id': product.id},
            fields=['main_category_eng^4', 'categories_eng', 'lines', "main_line^3", 'model^4', 'colorway^2', 'collab'],
            min_term_freq=1,
            min_doc_freq=1,
            max_query_terms=50,
            boost_terms=1.5,
            boost=1.2
        )
    )
    # fields=['brands', 'categories', 'lines', 'model', 'colorway', 'collab']

    search = search[:25]

    # Выполните запрос
    response = search.execute()

    # output_file = 'similar_results.json'
    # with open(output_file, 'w', encoding="utf-8") as f:
    #     json.dump(response.to_dict(), f, indent=4)
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



def add_filter_search(query):
    search_line = search_best_line(query)
    search_category = search_best_category(query)
    search_color = search_best_color(query)
    search_collab = search_best_collab(query)
    res = {"collab": "",
           "category": "",
           "line": "",
           "color": ""}
    if search_collab:
        res['collab'] = search_collab.name
    if search_category:
        res['category'] = search_category.eng_name
    if search_line:
        res['line'] = search_line.full_eng_name
    if search_color:
        res['color'] = search_color.name
    return res



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
                              fields=['manufacturer_sku^2', 'model^3', 'lines^2', 'colorway^1',
                                      "collab^4", "categories^3", 'brands^4'],
                              # Установите вес для каждого поля
                              fuzziness="AUTO")],
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
    print(search)
    print(100)

    response = search.execute()
    # Определите пороговое значение для подходящих результатов (50% от max_score)

    # Запись результатов в JSON файл
    # output_file = 'search_results.json'
    # with open(output_file, 'w', encoding="utf-8") as f:
    #     json.dump(response.to_dict(), f, indent=4)
    # max_score = response.hits.max_score
    # threshold = min(len(query) / 25, 0.8) * max_score
    product_ids = [hit.meta.id for hit in response.hits if hit.meta.score > 0.6]
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

    res = {"queryset": queryset}

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
        print(response.hits[0].meta)
        print(response.hits[0].name)

        # print("Line", Line.objects.get(id=response.hits[0].meta.id).name, response.hits.max_score)
        return Line.objects.get(name=response.hits[0].name)

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
        # print("Category", Category.objects.get(id=response.hits[0].meta.id).name, response.hits.max_score)
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
