# Backward compatibility shim — логика перенесена в products/services/content.py
from products.services.content import (  # noqa: F401
    count_queryset,
    filter_products,
    get_product_page,
    get_product_page_header,
)
