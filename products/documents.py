from elasticsearch_dsl import Document, Text, Keyword, Float, Integer, Completion
from elasticsearch_dsl.connections import connections
from .models import Product, Line, Category, Color
from elasticsearch_dsl import analyzer, token_filter

connections.create_connection(hosts=['localhost'])  # Укажите адрес вашего Elasticsearch-сервера

russian_stop = token_filter('russian_stop', type='stop', stopwords='_russian_')
russian_stemmer = token_filter('russian_stemmer', type='stemmer', language='russian')

russian_analyzer = analyzer(
    'russian_analyzer',
    tokenizer='standard',
    filter=['lowercase', russian_stop, russian_stemmer]
)


class ProductDocument(Document):
    brands = Text(multi=True)
    categories = Text(multi=True, analyzer=russian_analyzer)
    lines = Text(multi=True)
    model = Text()
    colorway = Text()
    collab = Text()
    # main_color = Keyword()
    gender = Keyword(multi=True)
    manufacturer_sku = Text()
    suggest = Completion()

    # colors = Keyword(multi=True)
    # designer_color = Text()
    # description = Text()
    # russian_name = Text()

    class Index:
        name = 'product_index'


custom_edge_ngram = token_filter(
    'custom_edge_ngram',
    type='edgeNGram',
    min_gram=2,
    max_gram=20,
    token_chars=['letter', 'digit']
)


custom_analyzer = analyzer(
    'custom_analyzer',
    tokenizer='standard',
    filter=['lowercase', custom_edge_ngram]
)

class BrandDocument(Document):
    name = Text(analyzer=custom_analyzer)

    class Index:
        name = 'brand_index'


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

    class Index:
        name = 'color_index'


class CollabDocument(Document):
    name = Text()

    class Index:
        name = 'collab_index'
