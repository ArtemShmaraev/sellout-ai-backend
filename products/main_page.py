# Backward compatibility shim — логика перенесена в products/services/content.py
from products.services.content import (  # noqa: F401
    get_brand_and_category_selection,
    get_brand_selection,
    get_category_selection,
    get_collab_selection,
    get_color_and_brand_selection,
    get_color_and_category_selection,
    get_color_and_line_selection,
    get_header_photo,
    get_line_selection,
    get_photo,
    get_photo_text,
    get_product_for_selecet,
    get_random,
    get_random_model,
    get_selection,
    get_sellout_photo_text,
)
