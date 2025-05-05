# from haystack import indexes
# from .models import Product
#
#
# class ProductIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True, use_template=True)
#     brands = indexes.MultiValueField()
#     model = indexes.CharField(model_attr='model')
#     colorway = indexes.CharField(model_attr='colorway')
#     russian_name = indexes.CharField(model_attr='russian_name')
#     manufacturer_sku = indexes.CharField(model_attr='manufacturer_sku')
#     description = indexes.CharField(model_attr='description')
#     designer_color = indexes.CharField(model_attr='designer_color')
#     categories = indexes.MultiValueField()
#     lines = indexes.MultiValueField()
#     main_color = indexes.CharField(model_attr='main_color__name')
#     collab = indexes.CharField(model_attr='collab__name')  # Имя для поля collab
#
#     def get_model(self):
#         return Product
#
#     def prepare_categories(self, obj):
#         return [category.name for category in obj.categories.all()]
#
#
#     def prepare_brands(self, obj):
#         return [brand.name for brand in obj.brands.all()]
#
#
#     def prepare_lines(self, obj):
#         return [line.name for line in obj.lines.all()]
#
