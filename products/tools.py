import random
import json
from functools import lru_cache
from datetime import datetime, date

from django.db.models import Q

from products.main_page import get_random
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, Collab, Photo, HeaderText, \
    HeaderPhoto
from products.serializers import LineSerializer



class RandomGenerator:
    def __init__(self):
        self.last_value = None
        self.same_count = 0

    def generate(self):
        while True:
            value = random.randint(0, 1)
            if value != self.last_value:
                self.last_value = value
                self.same_count = 1
                return value
            else:
                self.same_count += 1
                if (value == 0 and self.same_count >= 3) or (value == 1 and self.same_count >= 5):
                    self.last_value = 1 - value
                    self.same_count = 1
                    return self.last_value


def get_product_page_photo(params):
    line = params.getlist('line')
    category = params.getlist("category")
    collab = params.getlist("collab")
    res = {}
    header_photos = HeaderPhoto.objects.all()
    header_photos = header_photos.filter(where="product_page")
    text = False
    if category:
        header_photos = header_photos.filter(categories__eng_name__in=category)

    if line and collab:
        if "all" in collab:
            header_photos = header_photos.filter(
                Q(lines__full_eng_name__in=line) | ~Q(collabs=None)
            )
        else:
            header_photos = header_photos.filter(
                Q(lines__full_eng_name__in=line) | Q(collabs__query_name__in=collab)
            )
    elif line:
        header_photos = header_photos.filter(Q(lines__full_eng_name__in=line))

    elif collab:
        if "all" in collab:
            header_photos = header_photos.filter(~Q(collabs=None))
        else:
            header_photos = header_photos.filter(Q(collabs__query_name__in=collab))
    else:
        text = HeaderText.objects.filter(title="sellout")[random.randint(0, 4)]

    header_photos_desktop = header_photos.filter(type="desktop")
    header_photos_mobile = header_photos.filter(type="mobile")
    if header_photos_desktop.count() > 0:
        count = header_photos_desktop.count()
    else:
        header_photos_desktop = HeaderPhoto.objects.filter(type="desktop")
        count = header_photos_desktop.count()

    photo_desktop = header_photos_desktop[random.randint(0, count - 1)]

    if not text:
        text_desktop = get_text(photo_desktop, category)
    else:
        text_desktop = text
    res["desktop"] = {"title": text_desktop.title, "content": text_desktop.text}
    res['desktop']['photo'] = photo_desktop.photo.url

    if header_photos_mobile.count() > 0:
        count = header_photos_mobile.count()
    else:
        header_photos_mobile = HeaderPhoto.objects.filter(type="mobile")
        count = header_photos_mobile.count()

    photo_mobile = header_photos_mobile[random.randint(0, count - 1)]
    if not text:
        text_mobile = get_text(photo_mobile, category)
    else:
        text_mobile = text

    res["mobile"] = {"title": text_mobile.title, "content": text_mobile.text}
    res['mobile']['photo'] = photo_mobile.photo.url
    return res


def get_product_text(line, collab, category):
    texts = HeaderText.objects.all()
    if line:
        texts = texts.filter(Q(lines__full_eng_name__in=line))
    elif collab:
        texts = texts.filter(Q(collabs__query_name__in=collab))
    elif category:
        texts = texts.filter(categories__eng_name__in=category)
    elif not line and not collab and not category:
        texts = texts.filter(title="sellout")
    text = get_random(texts)

    return text




def get_text(photo, category):
    if photo.lines.exists():
        line = photo.lines.all().order_by("-id").first()
        texts = HeaderText.objects.all()
        while line.parent_line is not None:
            texts = HeaderText.objects.filter(lines=line)
            if texts.exists():
                break
            line = line.parent_line
    elif photo.collabs.exists():
        collab = photo.collabs.all().first()
        texts = HeaderText.objects.filter(collabs=collab)
    elif "shoes_category" in category or "sneakers" in category or "high_top_sneakers" in category or "low_top_sneakers" in category:
        category = ["shoes_category", "sneakers"]
        texts = HeaderText.objects.filter(categories__eng_name__in=category)
    else:
        texts = HeaderText.objects.filter(title="sellout")

    if not texts.exists():
        texts = HeaderText.objects.filter(title="sellout")
    count = texts.count()
    text = texts[random.randint(0, count - 1)]
    return text

def build_category_tree(categories):
    category_dict = {}
    root_categories = []

    # Создаем словарь для быстрого доступа к категориям по их идентификатору
    for category in categories:
        category_dict[category["id"]] = category

    # Строим иерархическую структуру категорий
    for category in categories:
        parent_ids = category["parent_category"]
        if parent_ids:
            parent_category = category_dict[parent_ids]
            parent_category.setdefault("children", []).append(category)
        else:
            root_categories.append(category)
    return root_categories


def category_no_child(cats):
    result = []
    for cat in cats:
        if 'subcategories' not in cat:
            result.append(cat)
        else:
            children = cat['subcategories']
            result.extend(category_no_child(children))
    # result.sort(key=lambda x: x['full_name'])
    return result


@lru_cache(maxsize=2)
def build_line_tree():
    lines = LineSerializer(Line.objects.all(), many=True).data
    line_dict = {}
    root_lines = []
    # Создание словаря линеек с использованием их идентификаторов в качестве ключей
    for line in lines:
        line_dict[line['id']] = line

    # Построение дерева линеек
    for line in lines:
        parent_line = line['parent_line']
        if parent_line is None:
            # Если у линейки нет родительской линейки, она считается корневой линейкой
            del line['parent_line']
            root_lines.append(line)
        else:
            parent_id = parent_line['id']
            parent_line = line_dict.get(parent_id)
            if parent_line:
                del line['parent_line']
                # Если родительская линейка найдена, добавляем текущую линейку в список её дочерних линеек
                parent_line.setdefault('children', []).append(line)

    def sort_children(data):
        for item in data:
            children = item.get('children')
            if children:
                # Сначала сортируем элементы, исключая "Другие"
                sorted_children = sorted([child for child in children if "Другие" not in child['name']],
                                         key=lambda x: x["id"])
                # Добавляем элементы с именем "Другие" в конец
                other_children = [child for child in children if "Другие" in child['name']]
                sorted_children += other_children
                item['children'] = sorted_children
                # Рекурсивно сортируем дочерние элементы
                sort_children(item['children'])
        return data

    root_lines = sort_children(root_lines)
    with_children = [x for x in root_lines if x.get('children')]
    without_children = [x for x in root_lines if not x.get('children')]

    sorted_data_with_children = sorted(with_children, key=lambda x: x["id"])

    # Сортируем оставшиеся элементы
    sorted_data_without_children = sorted(without_children, key=lambda x: x['view_name'].lower())
    # Объединяем отсортированные части
    sorted_data = sorted_data_with_children + sorted_data_without_children
    return sorted_data



def line_no_child(lines):
    line_dict = {}
    root_lines = []

    # Создание словаря линеек с использованием их идентификаторов в качестве ключей
    for line in lines:
        line_dict[line['id']] = line

    # Построение дерева линеек
    for line in lines:
        parent_line = line['parent_line']
        if parent_line is None:
            # Если у линейки нет родительской линейки, она считается корневой линейкой
            root_lines.append(line)
        else:
            parent_id = parent_line['id']
            parent_line = line_dict.get(parent_id)
            if parent_line:
                # Если родительская линейка найдена, добавляем текущую линейку в список её дочерних линеек
                parent_line.setdefault('children', []).append(line)

    def get_lines_without_children(lines):
        result = []
        for line in lines:
            if 'children' not in line:
                result.append(line)
            else:
                children = line['children']
                result.extend(get_lines_without_children(children))
        result.sort(key=lambda x: x['full_name'])
        return result

    return get_lines_without_children(root_lines)


print()
colors_data = json.load(open("colors.json", encoding="utf-8"))
singular_data = json.load(open("categories_singular.json", encoding="utf-8"))


def check_color_in_list(color_name):
    for color in colors_data:
        if color['name'] == color_name:
            return color
    return False


def add_product2(data):
    rel_num = data.get('platform_info').get("poizon").get("detail").get('likesCount', 0)
    product, create = Product.objects.get_or_create(
        model=data.get('model'),
        manufacturer_sku=data.get('manufacturer_sku'),
        russian_name=data.get('model'),
        slug=data.get('manufacturer_sku') + str(random.randint(1, 50)),
        rel_num=int(rel_num if rel_num else 0),
        is_collab=data.get('is_collab'),
        main_color=Color.objects.get_or_create(name="multicolour")[0]
    )
    # if not create:


def add_product(data, SG_PRODUCTS=Product.objects.filter(id__lte=19000)):

    # print(data)
    rel_num = data.get('platform_info').get("poizon").get("detail").get('likesCount', 0)
    manufactorer_sku = data.get('manufacturer_sku').replace(" ", "").replace("-", "")
    if SG_PRODUCTS.filter(manufacturer_sku=manufactorer_sku).exists() and not data.get('is_custom'):
        return 0
        # Product.objects.filter(manufacturer_sku=data.get('manufacturer_sku')).delete()
        product = Product.objects.get(manufacturer_sku=manufactorer_sku, is_custom=False)
        product.manufacturer_sku = data.get('manufacturer_sku')
        product.available_flag = True
        product.rel_num = int(rel_num if rel_num else 0)
        product.is_collab = data.get('is_collab')

    else:
        # Создание нового продукта
        product = Product.objects.create(
            model=data.get('model'),
            manufacturer_sku=data.get('manufacturer_sku'),
            russian_name=data.get('model'),
            slug=data.get('manufacturer_sku') + str(random.randint(1, 50)),
            rel_num=int(rel_num if rel_num else 0),
            is_collab=data.get('is_collab'),
            main_color=Color.objects.get_or_create(name="multicolour")[0]
        )
        # product.save()

        # Обработка брендов
        brands = data.get('brands', [])
        for brand_name in brands:
            brand, _ = Brand.objects.get_or_create(name=brand_name)
            product.brands.add(brand)
        # Обработка цветов

        # colors = data.get('colors', [])
        # for color_name in colors:
        #     color, _ = Color.objects.get_or_create(name=color_name)
        #     product.colors.add(color)
        #
        # # Обработка основного цвета
        # main_color = data.get('main_color')
        # if main_color:
        #     color_in = check_color_in_list(main_color)
        #     if color_in:
        #         main_color, _ = Color.objects.get_or_create(name=main_color)
        #         main_color.hex = color_in['hex']
        #         main_color.russian_name = color_in['russian_name']
        #     else:
        #         main_color, _ = Color.objects.get_or_create(name=main_color)
        #     main_color.is_main_color = True
        #     main_color.save()
        #     product.main_color = main_color

        # print(product.main_line.view_name)

    categories = data.get('categories')
    if not isinstance(categories, list):
        categories = [categories]
    for category_name in categories:
        category = Category.objects.get(name=category_name)
        product.categories.add(category)

    product.platform_info = json.dumps(data.get("platform_info"))

    product.is_custom = data.get('is_custom', False)
    # Обработка пола
    genders = data.get('gender', [])
    product.gender.set(Gender.objects.filter(name__in=genders))

    if data['date']:
        product.exact_date = datetime.strptime(data['date'], "%d.%m.%Y").date()

    if data['approximate_date']:
        product.approximate_date = data['approximate_date']

    lines = data.get('lines', [])
    if len(lines) != 0:
        lines = lines[0]

    f = True
    # проверка что линека уже существует
    for line in lines:
        if not Line.objects.filter(view_name=line).exists():
            f = False
    if f:  # если линейка уже существует
        for line in lines:
            product.lines.add(Line.objects.get(view_name=line))
    else:
        # линейка всегда существует, сюда код не дойдет
        print("ПИЗДАААААААА")
        # parent_line = None
        # for line_name in lines:
        #     if Line.objects.filter(name=line_name, parent_line=parent_line).exists():
        #         line = Line.objects.get(name=line_name, parent_line=parent_line)
        #     else:
        #         line = Line(name=line_name, parent_line=parent_line, full_name=line_name)
        #         line.save()
        #     if parent_line is not None:
        #         if Line.objects.filter(name=f"Все {parent_line.name}",
        #                                parent_line=parent_line).exists():
        #             line_all = Line.objects.get(name=f"Все {parent_line.name}", parent_line=parent_line, )
        #         else:
        #             line_all = Line(name=f"Все {parent_line.name}", parent_line=parent_line,
        #                             full_name=line_name)
        #             line_all.save()
        #         product.lines.add(line_all)
        #     parent_line = line
        #     product.lines.add(line)

    # product.slug = ""
    product.save(custom_param=True)

    if product.main_line is not None:
        brands = data.get('brands', [])
        model = product.main_line.view_name
        for brand in brands:
            model = model.replace(brand, "") if brand != "Jordan" and "Air" not in model else model
        model = " ".join(model.split())
        if not Brand.objects.filter(name=model).exists():
            product.model = model

            product.colorway = data.get('model')

    # # Обработка рекомендованного пола Возможно тут список из одного элемента!!!
    # recommended_gender = data.get('recommended_gender')
    # product.recommended_gender = Gender.objects.get(name=recommended_gender)
    photos = data.get('bucket_link', [])
    for photo in photos:
        photo, _ = Photo.objects.get_or_create(url=photo)
        product.bucket_link.add(photo)

    if product.is_collab:
        collab, _ = Collab.objects.get_or_create(name=data.get('collab_name'))
        product.collab = collab

    if "кроссовки" not in "_".join(categories):
        product.colorway = product.model
        product.model = singular_data[categories[0]]
    product.save()
    print(product)
    return product

    # self.stdout.write(self.style.SUCCESS(product))


