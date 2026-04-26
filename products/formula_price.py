# Backward compatibility shim — логика перенесена в products/services/pricing.py
from products.services.pricing import (  # noqa: F401
    CASHING_OUT_COMMISSION_FEE_DECIMAL,
    FIXED_COSTS_ABSOLUTE,
    FRIENDS_AND_FAMILY_MARKUP,
    PAYMENT_AND_TAX_COMMISSION_FEE_DECIMAL,
    PRELIMINARY_MARKUP,
    PRIVILEGED_CURRENCY_DIFFERENCE_DECIMAL,
    PRIVILEGED_MARKUP,
    correlate_markup_with_price,
    formula_price,
    get_bonus,
    round_by_step,
)
