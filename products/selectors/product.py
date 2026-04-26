from django.db import models

from products.models import Product

_PRODUCT_SELECT_RELATED = ["main_line", "main_color", "collab", "recommended_gender", "size_table"]
_PRODUCT_PREFETCH_RELATED = [
    "brands",
    "categories",
    "lines",
    "colors",
    "gender",
    "materials",
    "collections",
    "tags",
    "bucket_link",
]


def _base_qs():
    return (
        Product.objects
        .select_related(*_PRODUCT_SELECT_RELATED)
        .prefetch_related(*_PRODUCT_PREFETCH_RELATED)
    )


def get_product_by_slug(slug: str) -> Product:
    return _base_qs().get(slug=slug)


def get_product_by_id(product_id: int) -> Product:
    return _base_qs().get(id=product_id)


def get_products_by_ids(ids: list[int]):
    return (
        _base_qs()
        .filter(id__in=ids)
        .order_by(
            models.Case(*[models.When(id=pk, then=idx) for idx, pk in enumerate(ids)])
        )
    )


def get_products_by_spu_id(spu_id: int):
    return _base_qs().filter(spu_id=spu_id)


def get_available_products(filters: dict | None = None):
    qs = _base_qs().filter(available_flag=True, is_custom=False)
    if not filters:
        return qs
    if brand := filters.get("brand"):
        qs = qs.filter(brands__query_name=brand)
    if category := filters.get("category"):
        qs = qs.filter(categories__eng_name=category)
    if line := filters.get("line"):
        qs = qs.filter(lines__full_eng_name=line)
    if color := filters.get("color"):
        qs = qs.filter(colors__name=color)
    return qs
