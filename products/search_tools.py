from django.shortcuts import render
from .models import Line
from elasticsearch_dsl import Search
from .documents import LineDocument

def search_best_line(query_string):
    search = Search(index='line_index')
    print(query_string)
    search = search.query(
        'multi_match',
        query=query_string,
        fields=['name'],  # Поле для поиска
        fuzziness='AUTO'
    )
    search = search.sort('_score')  # Сортировка по рейтингу убывающим образом
    response = search.execute()

    if response:
        return Line.objects.get(id=response.hits[0].meta.id)

    return None


def search_best_line(query_string):
    search = Search(index='line_index')
    print(query_string)
    search = search.query(
        'multi_match',
        query=query_string,
        fields=['name'],  # Поле для поиска
        fuzziness='AUTO'
    )
    search = search.sort('_score')  # Сортировка по рейтингу убывающим образом
    response = search.execute()

    if response:
        return Line.objects.get(id=response.hits[0].meta.id)

    return None