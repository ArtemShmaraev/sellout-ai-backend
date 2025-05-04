from django.shortcuts import render
from .models import Line, Category, Color, Collab
from elasticsearch_dsl import Search
from .documents import LineDocument


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
            return Collab.objects.get(id=response.hits[0].meta.id)
        return None
    return None
