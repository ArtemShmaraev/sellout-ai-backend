# Backward compatibility shim — логика перенесена в products/services/ai_search.py
from products.services.ai_search import (  # noqa: F401
    CATEGORIES,
    COLLABS,
    COLORS,
    MATERIALS,
    SYSTEM_PROMPT,
    filter_products_from_dict,
    query_to_filters,
)
