import json
from time import time

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

    search = Search(index=index_name)
    search = search.suggest(
        'autocomplete',
        query,  # Часть слова, по которой будет выполняться поиск
        completion={
            'field': 'suggest',
            'size': 25,
            # 'analyzer': analyzer_name,
            'fuzzy': {  # Добавляем фильтр fuzzy для допуска опечаток
                'fuzziness': 'AUTO'  # Автоматический режим допуска опечаток
            }
            # Указываем соответствующий анализатор для поиска
        }
    )

    #
    # search = Search(index='suggest_index')
    # search = search.suggest(
    #     'autocomplete',
    #     query,  # Часть слова, по которой будет выполняться поиск
    #     completion={
    #         'field': 'suggest',
    #         'size': 10
    #     }
    # )

    response = search.execute()
    suggestions = response.suggest.autocomplete[0].options

    # Обработка полученных подсказок
    sp = []
    for suggestion in suggestions:
        sp.append({"name": suggestion._source.name, "type": suggestion._source.type, "url": suggestion._source.url})
        #
    return sp

    # # Создайте объект Search и настройте подсказки
    # search = Search(index=index_name)
    # s = search.suggest('user-input-suggestions', query, completion={'field': 'suggest', 'size': 100, 'fuzzy': {
    #     'fuzziness': 'AUTO'
    # }})
    #
    # # Выполнение запроса
    # response = s.execute()
    #
    # # Извлечение подсказок из ответа
    # suggestions = response.suggest['user-input-suggestions'][0]['options']
    # sp = []
    #
    # # Вывод подсказок
    # for suggestion in suggestions:
    #
    #     sp.append({"name": suggestion._source.name, "type": suggestion._source.type, "url": suggestion._source.url, "sug": suggestion._source.suggest})
    #     # sp.append(dict(suggestion._source))
    # return sp

    # Извлечение всех подсказок из ответа
    # suggestions = response.suggest['all-suggestions'][0]['options']

    # Вывод всех подсказок
    # for suggestion in suggestions:
    #     print(suggestion.text)


def similar_product(product):
    try:
        t = time()
        search = Search(index='product_index_3')  # Замените на имя вашего индекса
        # print(search.count())

        search = search.query(
            MoreLikeThis(
                like={'_id': product.id},
                fields=['main_category_eng^4', 'categories_eng', 'lines', "main_line^3", 'model^4', 'colorway^2',
                        'collab'],
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
        # print(response)
        # output_file = 'similar_results.json'
        # with open(output_file, 'w', encoding="utf-8") as f:
        #     json.dump(response.to_dict(), f, indent=4)
        # max_score = response.hits.max_score
        # threshold = 0.6 * max_score

        product_ids = [hit.meta.id for hit in response.hits]
        queryset = Product.objects.filter(id__in=product_ids).filter(
            available_flag=True).filter(is_custom=False)

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
        return queryset, True
    except:
        print(",kznm", time() - t)
        return [], False


def add_filter_search(query):
    res = {"collab": "",
           "category": "",
           "line": "",
           "color": ""}
    return res
    search_line = search_best_line(query)
    search_category = search_best_category(query)
    search_color = search_best_color(query)
    search_collab = search_best_collab(query)

    if search_collab:
        res['collab'] = search_collab.name
    if search_category:
        res['category'] = search_category.eng_name
    if search_line:
        res['line'] = search_line.full_eng_name
    if search_color:
        res['color'] = search_color.name
    return res


def search_product(query, pod_queryset, page_number=1):
    search = Search(index='product_index_3')


    # fields = ['manufacturer_sku^6', 'model^3', 'lines^2', 'colorway^1', "collab^4", "categories^3", 'brands^4']
    # search = search.query(Q("multi_match", query=query, fields=fields))
    # search = search.query('bool',
    #                       must=[
    #                           Q('multi_match',
    #                             query=query,
    #                             type="most_fields",
    #                             fields=['model^3', 'lines^2', 'colorway^1', 'categories^3', 'brands^4'],
    #                             fuzziness="AUTO")
    #                       ],
    #                       should=[
    #                           # Q('match', main_line={'query': query, 'boost': 2, 'fuzziness': 'AUTO'}),
    #                           Q('match', colorway={'query': query, 'fuzziness': 'AUTO'}),
    #                           Q('match', manufacturer_sku={"query": query, 'boost': 8, 'fuzziness': 2})
    #                       ]
    #                       )





    # search = search.query(
    #     'multi_match',
    #     query=query,
    #     fields=['manufacturer_sku', "full_name"],
    #     # Установите вес для каждого поля
    #     fuzziness='AUTO'
    # )
    search = search.query('bool', must=[
        {'match': {'full_name': {'query': query, 'fuzziness': 'AUTO'}}}])
    # , should=[
    #     {'match': {'manufacturer_sku': {'query': query, 'fuzziness': 'AUTO', 'boost': 1}}}
    # ])


    search = search.sort(
        {'_score': {'order': 'desc'}},
        {'rel_num': {'order': 'desc'}}
    )

    search = search[:192]

    response = search.execute()
    with open('results.json', 'w', encoding='utf-8') as json_file:
        # Преобразовать результаты в JSON и записать их в файл
        json.dump(response.to_dict(), json_file, ensure_ascii=False, indent=4)

    # for hit in response['hits']['hits'][:10]:
    #     print(hit['_score'], hit['_source']['rel_num'])
    #
    #     result = json.dumps(hit['_source'].to_dict(), indent=4, ensure_ascii=False)
    #     # print(result)

    # Определите пороговое значение для подходящих результатов (50% от max_score)

    # Запись результатов в JSON файл
    # output_file = 'search_results.json'
    # with open(output_file, 'w', encoding="utf-8") as f:
    #     json.dump(response.to_dict(), f, indent=4)
    # max_score = response.hits.max_score
    # threshold = min(len(query) / 25, 0.8) * max_score
    product_ids = [hit.meta.id for hit in response.hits if hit.meta.score > 0.6]
    queryset = Product.objects.filter(id__in=product_ids).filter(id__in=pod_queryset).values_list("id", flat=True)

    count = queryset.count()
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
        if response.hits[0].meta.score > 4:
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
        if response.hits[0].meta.score > 4:
            # print("Category", Category.objects.get(id=response.hits[0].meta.id).name, response.hits.max_score)
            return Category.objects.get(id=response.hits[0].meta.id)
    return None


def search_best_color(query_string):
    search = Search(index='color_index')
    search = search.query(
        'multi_match',
        query=query_string,
        fields=['russian_name', 'eng_name'],  # Поле для поиска
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
