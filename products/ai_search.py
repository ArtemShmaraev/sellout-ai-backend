import json

from django.conf import settings
import httpx

from .models import Product
from .search_tools import search_product

COLORS = [
    "white", "silver", "neutrals", "yellow", "gold", "green", "orange",
    "pink", "red", "blue", "purple", "gray", "black", "brown", "multicolour",
]

CATEGORIES = [
    "shoes_category", "sneakers", "high_top_sneakers", "low_top_sneakers",
    "basketball_sneakers", "football_boots", "other_sport_shoes", "canvas_shoes",
    "loafers", "moccasins_and_topsiders", "slip_ons", "espadrilles", "sandals",
    "beach_sandals", "slippers", "mules_and_clogs", "shoes", "high_heels",
    "medium_heels", "low_heels", "wedge_shoes", "mens_shoes", "derby", "oxford",
    "brogues", "monks", "boots", "thick-soled_shoes", "high_boots_and_jackboots",
    "medium_boots", "short_boots_and_ankle_boots", "chelsea_boots", "martins",
    "timberlands", "deserts", "cossacks", "winter_sneakers_and_shoes", "clothes",
    "tshirts", "longsleeves", "hoodie_sweatshirts", "hoodie", "zip_hoodie",
    "sweatshirts", "knitwear", "sweaters", "cardigans", "turtlenecks", "knit_vests",
    "shorts", "sweatpants", "sport_clothes", "basketball_jerseys", "basketball_shorts",
    "football_shirts", "football_shorts", "sport_vests", "sport_shorts", "sport_tops",
    "tracksuits", "leggings_thermal_underwear", "tops", "vest_shirt", "polo", "jeans",
    "skirts", "dresses", "shirts", "trousers", "jackets", "suits", "denim", "overalls",
    "winter_pants", "outerwear", "coats_jackets", "leather_jackets", "denim_jackets",
    "baseball_jackets", "vests", "windbreakers", "trench", "coats", "down_jackets",
    "fur_coats", "ski_suit", "beach_wear", "mens_swimming_trunks", "womens_swimsuits",
    "one_piece_swimsuits", "underwear_home_wear", "home_clothes", "socks", "bras",
    "underpants", "bags", "crossbody_bags", "shoulder_bags", "handbags", "chest_bags",
    "waist_bags", "tote_bags", "hobo_bags", "bucket_bags", "backpacks", "formal_case",
    "clutches", "wallets", "cardholders", "passport_covers", "makeup_bags", "sport_bags",
    "suitcases", "bags_accessories", "accessories", "belts", "scarfs", "gloves",
    "all_hats", "caps", "hats", "panamas", "sun_hats", "berets_hats", "sport_goods",
    "basketballs", "footballs", "volleyballs", "sports_gloves", "sports_equipment",
    "other_sport_goods", "jewelries", "necklaces", "bracelets", "rings", "earrings",
    "pendants", "brooch", "other_jewelries", "collectibles", "sunglasses",
    "optical_glasses", "glasses_cases", "ties", "watches", "perfumes", "cosmetics",
    "keychains", "phone_cases", "tech_accessories", "other_accessories",
]

MATERIALS = [
    "feather", "cotton", "leather", "cashmere", "wool", "nylon", "polyester",
    "fabric", "denim", "silk", "suede", "fur", "satin", "other_material",
]

COLLABS = [
    "adidas Yeezy", "Nike x Off-White", "Nike x Travis Scott", "Nike x Supreme",
    "Nike x Union", "Nike x Clot", "Nike x Sacai", "Nike x Stüssy", "Nike x Ambush",
    "Nike x A Ma Maniére", "Nike x Jacquemus", "Nike x Fear of God",
    "New Balance x Salehe Bembury", "New Balance x Aimé Leon Dore",
    "New Balance x Casablanca", "Supreme x The North Face", "adidas x Pharrell Williams",
    "adidas x Bad Bunny", "Converse x GOLF le FLEUR*", "YEEZY x Gap",
    "adidas by Stella McCartney", "adidas x Alexander Wang", "adidas x Balenciaga",
    "adidas x Gucci", "adidas x Prada", "Jordan x Dior", "Jordan x J.Balvin",
    "Nike x Louis Vuitton", "Nike x Drake NOCTA", "Supreme x Burberry",
    "Cactus Jack by Travis Scott x Dior", "Nike x Tom Sachs", "Nike x Patta",
    "Nike x Parra", "Nike x Peaceminusone", "Nike x ACRONYM",
]

SYSTEM_PROMPT = f"""Ты помощник для поиска товаров в интернет-магазине кроссовок и одежды (sellout.su).

На основе запроса пользователя верни JSON с фильтрами и коротким пояснением.

Доступные фильтры:
- q: string — текстовый поиск по бренду/модели (например "Nike Air Force 1", "Yeezy 350", "adidas Samba")
- color: list[string] — только из списка: {COLORS}
- category: list[string] — только из списка: {CATEGORIES}
- material: list[string] — только из списка: {MATERIALS}
- collab: list[string] — только из списка: {COLLABS}
- gender: list[string] — только из: ["M", "F" "K"] male female kids
- price_min: int
- price_max: int
- is_sale: bool
- new: bool

Правила:
- Используй ТОЛЬКО значения из предоставленных списков
- Если значение не совпадает ни с одним из списка — не добавляй его
- Для бренда/модели используй поле q (например "Nike", "Air Jordan 4", "New Balance 550")
- Верни ТОЛЬКО валидный JSON без лишнего текста
- Если в истории диалога есть предыдущие фильтры — **бери их за основу** и дополняй или изменяй только то, о чём просит пользователь. Не сбрасывай предыдущие фильтры если пользователь их не отменяет.
- Если пользователь уточняет запрос ("а со скидкой?", "только мужские", "до 10000") — сохраняй все предыдущие фильтры и добавляй новые поверх них.

Формат ответа:
{{
  "filters": {{}},
  "explanation": "короткое пояснение на русском что именно ищем",
  "suggestions": ["уточняющий вопрос 1", "уточняющий вопрос 2"]
}}

Правила для suggestions:
- Ровно 2 коротких подсказки (до 5 слов каждая) для продолжения диалога
- Предлагай логичные уточнения к текущему поиску: по цвету, цене, полу, скидке, новинкам, материалу или коллаборации
- Пиши от первого лица как будто это пишет пользователь, например: "До 10 000 ₽", "Только со скидкой", "Мужские", "Новинки"
- Не повторяй фильтры, которые уже применены"""


def query_to_filters(user_query: str, history: list[dict] | None = None) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *(history or []),
        {"role": "user", "content": user_query},
    ]
    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.OPENROUTER_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "nvidia/nemotron-3-super-120b-a12b:free",
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        },
        timeout=30,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return json.loads(content)


def filter_products_from_dict(filters: dict):
    queryset = Product.objects.filter(available_flag=True, is_custom=False)

    q = filters.get("q")
    color = filters.get("color") or []
    category = filters.get("category") or []
    material = filters.get("material") or []
    collab = filters.get("collab") or []
    gender = filters.get("gender") or []
    price_min = filters.get("price_min")
    price_max = filters.get("price_max")
    is_sale = filters.get("is_sale")
    new = filters.get("new")

    if gender:
        queryset = queryset.filter(gender__name__in=gender)
    if color:
        queryset = queryset.filter(colors__name__in=color)
    if category:
        queryset = queryset.filter(categories__eng_name__in=category)
    if material:
        queryset = queryset.filter(materials__eng_name__in=material)
    if collab:
        queryset = queryset.filter(collab__query_name__in=collab)
    if is_sale:
        queryset = queryset.filter(is_sale=True)
    if new:
        queryset = queryset.filter(is_new=True)
    if price_min:
        queryset = queryset.filter(min_price__gte=price_min)
    if price_max:
        queryset = queryset.filter(min_price__lte=price_max)

    if q:
        q = q.replace("_", " ")
        search = search_product(q, queryset)
        queryset = search["queryset"]
        ids = list(queryset.values_list("id", flat=True).distinct()[:10])
        products = Product.objects.filter(id__in=ids)
    else:
        ids = list(queryset.values_list("id", flat=True).distinct().order_by("-score_product_page")[:10])
        products = Product.objects.filter(id__in=ids).order_by("-score_product_page")

    return products
