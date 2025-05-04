from django.shortcuts import render
from .models import Line, Category, Color, Collab, Product
from .serializers import ProductMainPageSerializer
from elasticsearch_dsl import Search
from django.db.models import Case, When, Value, IntegerField
from .documents import LineDocument



def search_product(query, page_number=1):
    search = Search(index='product_index')
    search = search.query(
        'multi_match',
        query=query,
        fields=['manufacturer_sku^1', 'model^3', 'lines^3', 'russian_name^1', 'colorway^1'],
        # Установите вес для каждого поля
        fuzziness='AUTO'
    )

    response = search.execute()
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

    # count = response.hits.total.value
    # start_index = (page_number - 1) * 60
    # queryset = response.hits[start_index:start_index + 60]
    #
    # product_ids = [hit.meta.id for hit in queryset]
    # queryset = Product.objects.filter(id__in=product_ids).order_by('id')

    search_line = search_best_line(query)
    search_category = search_best_category(query)
    search_color = search_best_color(query)
    search_collab = search_best_collab(query)
    res = {"queryset": queryset}
    url = "?"
    if search_collab:
        url += f"collab={search_collab.name}&"
        res['collab'] = search_collab.name
    if search_category:
        url += f"category={search_category.eng_name}&"
        res['category'] = search_category.eng_name
    if search_line:
        url += f"line={search_line.full_eng_name}&"
        res['line'] = search_line.full_eng_name
    if search_color:
        url += f"color={search_color.name}&"
        res['color'] = search_color.name
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
