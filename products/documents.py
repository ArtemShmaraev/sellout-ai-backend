from elasticsearch_dsl import Document, Text, Keyword, Float, Integer, Completion
from elasticsearch_dsl.connections import connections
from .models import Product, Line, Category, Color
from elasticsearch_dsl import analyzer, token_filter
from sellout.settings import HOST

# connections.create_connection(hosts=['51.250.74.115'])  # Укажите адрес вашего Elasticsearch-сервера
connections.create_connection(hosts=[f"{HOST}:9200"])

russian_stop = token_filter('russian_stop', type='stop', stopwords='_russian_')
russian_stemmer = token_filter('russian_stemmer', type='stemmer', language='russian')

russian_analyzer = analyzer(
    'russian_analyzer',
    tokenizer='standard',
    filter=['lowercase', russian_stop, russian_stemmer]
)


class ProductDocument(Document):
    brands = Text(multi=True, analyzer='keyword')
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
    manufacturer_sku = Text(analyzer='standard')
    suggest = Completion()

    # colors = Keyword(multi=True)
    # designer_color = Text()
    # description = Text()
    # russian_name = Text()

    class Index:
        name = 'product_index'


# Определение анализаторов для n-грамм с разной длиной
ngram_analyzer_2 = analyzer('ngram_analyzer_2',
    type='custom',
    tokenizer='standard',
    filter=['lowercase', 'ngram_filter_2']
)

ngram_analyzer_3 = analyzer('ngram_analyzer_3',
    type='custom',
    tokenizer='standard',
    filter=['lowercase', 'ngram_filter_3']
)

ngram_analyzer_4 = analyzer('ngram_analyzer_4',
    type='custom',
    tokenizer='standard',
    filter=['lowercase', 'ngram_filter_4']
)

ngram_analyzer_5 = analyzer('ngram_analyzer_5',
    type='custom',
    tokenizer='standard',
    filter=['lowercase', 'ngram_filter_5']
)

ngram_analyzer_6 = analyzer('ngram_analyzer_6',
    type='custom',
    tokenizer='standard',
    filter=['lowercase', 'ngram_filter_6']
)

ngram_analyzer_7 = analyzer('ngram_analyzer_7',
    type='custom',
    tokenizer='standard',
    filter=['lowercase', 'ngram_filter_7']
)

ngram_analyzer_8 = analyzer('ngram_analyzer_8',
    type='custom',
    tokenizer='standard',
    filter=['lowercase', 'ngram_filter_8']
)

ngram_analyzer_9 = analyzer('ngram_analyzer_9',
    type='custom',
    tokenizer='standard',
    filter=['lowercase', 'ngram_filter_9']
)

ngram_analyzer_10 = analyzer('ngram_analyzer_10',
    type='custom',
    tokenizer='standard',
    filter=['lowercase', 'ngram_filter_10']
)


custom_analyzer = analyzer(
    'autocomplete',
    tokenizer='standard',
    filter=['lowercase', 'edge_ngram']
)
class SuggestDocument(Document):
    name = Text()
    type = Text()
    url = Text()
    suggest = Completion(analyzer='keyword')  # Использование анализатора n-грамм (по умолчанию)

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

    class Index:
        name = 'color_index'


class CollabDocument(Document):
    name = Text()

    class Index:
        name = 'collab_index'
