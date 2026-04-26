
from django.core.management.base import BaseCommand

from products.models import (
    Brand,
    Category,
    Collab,
    Color,
    HeaderPhoto,
    HeaderText,
    Line,
    Material,
    Photo,
    Product,
    SizeRow,
    SizeTable,
    SizeTranslationRows,
)
from promotions.models import AccrualBonus, Bonuses, PromoCode
from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        users = User.objects.all()
        num_users = users.count()
        users.delete()
        print(f"Удалено {num_users} пользователей")

        products = Product.objects.all()
        num_products = products.count()
        products.delete()
        print(f"Удалено {num_products} продуктов")

        lines = Line.objects.all()
        num_lines = lines.count()
        lines.delete()
        print(f"Удалено {num_lines} линий")

        collabs = Collab.objects.all()
        num_collabs = collabs.count()
        collabs.delete()
        print(f"Удалено {num_collabs} коллабораций")

        cats = Category.objects.all()
        num_cats = cats.count()
        cats.delete()
        print(f"Удалено {num_cats} категорий")

        colors = Color.objects.all()
        num_colors = colors.count()
        colors.delete()
        print(f"Удалено {num_colors} цветов")

        material = Material.objects.all()
        num_materials = material.count()
        material.delete()
        print(f"Удалено {num_materials} материалов")

        brand = Brand.objects.all()
        num_brands = brand.count()
        brand.delete()
        print(f"Удалено {num_brands} брендов")

        photo = Photo.objects.all()
        num_photos = photo.count()
        photo.delete()
        print(f"Удалено {num_photos} фотографий")

        header = HeaderPhoto.objects.all()
        num_headers = header.count()
        header.delete()
        print(f"Удалено {num_headers} заголовочных фотографий")

        header = HeaderText.objects.all()
        num_headers = header.count()
        header.delete()
        print(f"Удалено {num_headers} заголовочных текстов")

        size = SizeTable.objects.all()
        num_sizes = size.count()
        size.delete()
        print(f"Удалено {num_sizes} таблиц размеров")

        size = SizeRow.objects.all()
        num_sizes = size.count()
        size.delete()
        print(f"Удалено {num_sizes} строк размеров")

        size = SizeTranslationRows.objects.all()
        num_sizes = size.count()
        size.delete()
        print(f"Удалено {num_sizes} переводов строк размеров")

        bonus = Bonuses.objects.all()
        bonus.delete()

        accrualbonus = AccrualBonus.objects.all()
        accrualbonus.delete()

        promo = PromoCode.objects.all()
        promo.delete()













