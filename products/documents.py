from elasticsearch_dsl import Document, Text, Keyword, Float, Integer, Completion
from elasticsearch_dsl.connections import connections
from .models import Product, Line, Category, Color
from elasticsearch_dsl import analyzer, token_filter
from sellout.settings import ELASTIC_HOST

# connections.create_connection(hosts=['51.250.74.115'])  # Укажите адрес вашего Elasticsearch-сервера
connections.create_connection(
            hosts=[ELASTIC_HOST],
            http_auth=("elastic", "espass2024word"),
            scheme="http",  # Используйте "https", если ваш сервер настроен для безопасного соединения
            port=9200,
            )

russian_stop = token_filter('russian_stop', type='stop', stopwords='_russian_')
russian_stemmer = token_filter('russian_stemmer', type='stemmer', language='russian')
# russian_morphology = token_filter('russian_morphology', type='morphology', language='russian')

russian_analyzer = analyzer(
    'russian_analyzer',
    tokenizer='standard',
    filter=['lowercase', russian_stop, russian_stemmer])


class ProductDocument(Document):
    brands = Text(multi=True, analyzer='standard')
    categories = Text(multi=True, analyzer=russian_analyzer)
    categories_eng = Text(multi=True, analyzer='standard')
    main_category = Text(analyzer=russian_analyzer)
    main_category_eng = Text(analyzer='standard')
    lines = Text(multi=True, analyzer='standard')
    main_line = Text(analyzer='standard')
    model = Text(analyzer='standard')
    colorway = Text(analyzer='standard')
    collab = Text(analyzer='standard')
    gender = Keyword(multi=True)
    colors = Keyword(multi=True)
    manufacturer_sku = Text(analyzer="standard")
    rel_num = Integer()
    min_price = Integer()
    materials = Keyword()
    full_name = Text(analyzer='standard')
    suggest = Completion()

    # colors = Keyword(multi=True)
    # designer_color = Text()
    # description = Text()
    # russian_name = Text()

    class Index:
        name = 'product_index'


# Определение анализаторов для n-грамм с разной длиной

custom_analyzer = analyzer(
    'custom_keyword_analyzer',
    tokenizer='keyword',
    filter=['lowercase']
)


class SuggestDocument(Document):
    name = Text()
    type = Text()
    url = Text()
    suggest = Completion(analyzer=custom_analyzer)  # Использование анализатора n-грамм (по умолчанию)

    class Index:
        name = 'suggest_index'


class LineDocument(Document):
    name = Text()
    suggest = Completion()

    class Index:
        name = 'line_index'


class CategoryDocument(Document):
    name = Text()
    suggest = Completion()

    class Index:
        name = 'category_index'


class ColorDocument(Document):
    russian_name = Text(analyzer=russian_analyzer)
    eng_name = Text()

    class Index:
        name = 'color_index'


class CollabDocument(Document):
    name = Text()

    class Index:
        name = 'collab_index'
