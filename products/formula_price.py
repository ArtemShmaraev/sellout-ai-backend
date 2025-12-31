import copy
import math


def round_by_step(value, step=50):
    return math.ceil(value / step) * step


CURRENCY_RATE_CNY = 13.8
COMMISSION_FEE_ABSOLUTE = 500
COMMISSION_FEE_RELATIVE_DECIMAL = 1
REGULAR_SHIPPING_KG_COST = 900
EXPRESS_SHIPPING_KG_COST = 2700
CASHING_OUT_COMMISSION_FEE_DECIMAL = 1.025
PAYMENT_AND_TAX_COMMISSION_FEE_DECIMAL = 0.915
FIXED_COSTS_ABSOLUTE = 100
PRELIMINARY_MARKUP = {
    "steps_of_order_amount": {
        "1": {
            "min_price_including": 0,
            "max_price_not_including": 2500,
            "preliminary_markup": 500
        },
        "2": {
            "min_price_including": 2500,
            "max_price_not_including": 5000,
            "preliminary_markup": 1000
        },
        "3": {
            "min_price_including": 5000,
            "max_price_not_including": 10000,
            "preliminary_markup": 1500
        },
        "4": {
            "min_price_including": 10000,
            "max_price_not_including": 15000,
            "preliminary_markup": 1700
        },
        "5": {
            "min_price_including": 15000,
            "max_price_not_including": 24000,
            "preliminary_markup": 2000
        },
        "6": {
            "min_price_including": 24000,
            "max_price_not_including": 35000,
            "preliminary_markup": 2500
        },
        "7": {
            "min_price_including": 35000,
            "max_price_not_including": 70000,
            "preliminary_markup": 3500
        },
        "8": {
            "min_price_including": 70000,
            "max_price_not_including": 90000,
            "preliminary_markup": 4000
        },
        "9": {
            "min_price_including": 90000,
            "max_price_not_including": 130000,
            "preliminary_markup": 5000
        },
        "10": {
            "min_price_including": 130000,
            "max_price_not_including": 150000,
            "preliminary_markup": 6000
        },
        "11": {
            "min_price_including": 150000,
            "max_price_not_including": 200000,
            "preliminary_markup": 7000
        },
        "12": {
            "min_price_including": 200000,
            "max_price_not_including": 1000000000000000,
            "preliminary_markup": 9000
        }
    }
}

PRIVILEGED_CURRENCY_DIFFERENCE_DECIMAL = 0.05
PRIVILEGED_MARKUP = 1500

FRIENDS_AND_FAMILY_CURRENCY_DIFFERENCE_DECIMAL = 1
FRIENDS_AND_FAMILY_MARKUP = 500


def correlate_markup_with_price(extra_markup, delivery_extra_charge):
    for step in PRELIMINARY_MARKUP["steps_of_order_amount"]:
        min_total_cost_including = (PRELIMINARY_MARKUP["steps_of_order_amount"][step]["min_price_including"]
                                    * PAYMENT_AND_TAX_COMMISSION_FEE_DECIMAL
                                    - PRELIMINARY_MARKUP["steps_of_order_amount"][step]["preliminary_markup"]
                                    - extra_markup - delivery_extra_charge)
        max_total_cost_including = (PRELIMINARY_MARKUP["steps_of_order_amount"][step]["max_price_not_including"]
                                    * PAYMENT_AND_TAX_COMMISSION_FEE_DECIMAL
                                    - PRELIMINARY_MARKUP["steps_of_order_amount"][step]["preliminary_markup"]
                                    - extra_markup - delivery_extra_charge)
        PRELIMINARY_MARKUP["steps_of_order_amount"][step]["min_total_cost_including"] = min_total_cost_including
        PRELIMINARY_MARKUP["steps_of_order_amount"][step]["max_total_cost_not_including"] = max_total_cost_including


def get_bonus(total_profit, max_total_profit_for_product, status_name):
    if status_name == "Amethyst":
        bonus_max = 250
        bonus_from_profit = round(0.1 * total_profit)
        bonus = min(bonus_max, bonus_from_profit)
        max_bonus_for_product = min(round(0.1 * max_total_profit_for_product), bonus_max)
    elif status_name == "Sapphire":
        bonus_max = 500
        bonus_from_profit = round(0.15 * total_profit)
        bonus = min(bonus_max, bonus_from_profit)
        max_bonus_for_product = min(round(0.15 * max_total_profit_for_product), bonus_max)
    elif status_name == "Emerald":
        bonus_max = 750
        bonus_from_profit = round(0.2 * total_profit)
        bonus = min(bonus_max, bonus_from_profit)
        max_bonus_for_product = min(round(0.2 * max_total_profit_for_product), bonus_max)
    elif status_name == "Ruby":
        bonus_max = 1000
        bonus_from_profit = round(0.25 * total_profit)
        bonus = min(bonus_max, bonus_from_profit)
        max_bonus_for_product = min(round(0.25 * max_total_profit_for_product), bonus_max)
    elif status_name == "Diamond":
        bonus_max = 1500
        bonus_from_profit = round(0.3 * total_profit)
        bonus = min(bonus_max, bonus_from_profit)
        max_bonus_for_product = min(round(0.3 * max_total_profit_for_product), bonus_max)
    else:
        bonus = 0
        max_bonus_for_product = 0

    return bonus, max_bonus_for_product


def formula_price(product, unit, user_status):
    original_price = unit.original_price
    weight = unit.weight if unit.weight != 0 else 1
    delivery = unit.delivery_type
    delivery_price_per_kg_in_rub = delivery.delivery_price_per_kg_in_rub
    delivery_decimal_insurance = delivery.decimal_insurance
    delivery_absolute_insurance = delivery.absolute_insurance
    delivery_extra_charge = delivery.extra_charge
    genders = list(product.gender.all().values_list("name", flat=True))  # ["M", "F", "K"]
    categories = list(product.categories.all().values_list("name", flat=True))  # на русском ["Обувь", "Вся обувь"]
    poizon_abroad = unit.delivery_type.poizon_abroad
    status_name = user_status.name  # Amethyst

    if status_name == "Privileged":
        converted_into_rub_price = original_price * CURRENCY_RATE_CNY
        shipping_cost = (
                delivery_price_per_kg_in_rub * weight + converted_into_rub_price * max(0,
                                                                                       delivery_decimal_insurance - 1)
                + delivery_absolute_insurance)
        cost_without_shipping = (converted_into_rub_price * COMMISSION_FEE_RELATIVE_DECIMAL + converted_into_rub_price
                                 * PRIVILEGED_CURRENCY_DIFFERENCE_DECIMAL + COMMISSION_FEE_ABSOLUTE)
        total_cost = cost_without_shipping + shipping_cost + FIXED_COSTS_ABSOLUTE
        total_profit = PRIVILEGED_MARKUP + converted_into_rub_price * PRIVILEGED_CURRENCY_DIFFERENCE_DECIMAL
        total_price = total_cost + PRIVILEGED_MARKUP
    elif status_name == "Friends & Family":

        converted_into_rub_price = original_price * CURRENCY_RATE_CNY
        # print(converted_into_rub_price)
        # print()
        shipping_cost = (
                delivery_price_per_kg_in_rub * weight + converted_into_rub_price * max(0,
                                                                                       delivery_decimal_insurance - 1)
                + delivery_absolute_insurance)

        cost_without_shipping = converted_into_rub_price * COMMISSION_FEE_RELATIVE_DECIMAL + COMMISSION_FEE_ABSOLUTE
        total_cost = cost_without_shipping + shipping_cost + FIXED_COSTS_ABSOLUTE
        total_profit = FRIENDS_AND_FAMILY_MARKUP
        total_price = total_cost + FRIENDS_AND_FAMILY_MARKUP

    else:
        if product.actual_price:
            bonus, max_bonus_for_product = get_bonus(unit.total_profit, product.max_profit, status_name)

            return {"final_price": unit.final_price,
                    "start_price": unit.start_price,
                    "total_profit": unit.total_profit,
                    "bonus": bonus,
                    "max_bonus": max_bonus_for_product}
        converted_into_rub_price = original_price * CURRENCY_RATE_CNY

        shipping_cost = (
                delivery_price_per_kg_in_rub * weight + converted_into_rub_price * max(0,
                                                                                       delivery_decimal_insurance - 1)
                + delivery_absolute_insurance)

        cost_without_shipping = converted_into_rub_price * COMMISSION_FEE_RELATIVE_DECIMAL + COMMISSION_FEE_ABSOLUTE

        total_cost_before_cashing_out = cost_without_shipping + shipping_cost

        total_cost = total_cost_before_cashing_out * CASHING_OUT_COMMISSION_FEE_DECIMAL + FIXED_COSTS_ABSOLUTE

        preliminary_markup = 0
        extra_markup = 0

        if 60000 >= total_cost >= 30000 and poizon_abroad:
            extra_markup += 1000
        elif total_cost > 60000 and poizon_abroad:
            extra_markup += 1500

        if genders == ["F"] and total_cost >= 15000 and "Кроссовки" not in categories:
            extra_markup += 500

        if genders == ["F"] and total_cost >= 30000 and "Обувь" not in categories and "Сумки" in categories:
            extra_markup += 1000

        if genders == ["F"] and total_cost >= 80000 and "Обувь" not in categories and "Сумки" in categories:
            extra_markup += 1000

        if genders == ["M"] and total_cost >= 60000 and "Обувь" not in categories and "Сумки" in categories:
            extra_markup += 1000

        correlate_markup_with_price(extra_markup, delivery_extra_charge)
        for step in PRELIMINARY_MARKUP["steps_of_order_amount"]:
            # print(PRELIMINARY_MARKUP["steps_of_order_amount"][step])
            if (PRELIMINARY_MARKUP["steps_of_order_amount"][step]["min_total_cost_including"] <= total_cost <
                    PRELIMINARY_MARKUP["steps_of_order_amount"][step]["max_total_cost_not_including"]):
                preliminary_markup = PRELIMINARY_MARKUP["steps_of_order_amount"][step]["preliminary_markup"]

        total_markup = preliminary_markup + extra_markup + delivery_extra_charge
        total_price_before_payment_and_tax_commission = total_cost + total_markup
        total_profit = total_markup
        total_price = total_price_before_payment_and_tax_commission / PAYMENT_AND_TAX_COMMISSION_FEE_DECIMAL

    round_total_price = round_by_step(total_price + 10, step=100) - 10
    total_round_markup = round_total_price - total_price
    total_profit += total_round_markup

    bonus, max_bonus_for_product = get_bonus(total_profit, product.max_profit, status_name)
    price_without_sale = round_total_price
    if product.sale_percentage != 0:
        percentage = round(((100 - product.sale_percentage) / 100), 2)
        price_without_sale = round_by_step((unit.final_price / percentage) + 10, step=100) - 10
    elif product.sale_absolute:
        price_without_sale = unit.final_price + product.sale_absolute

    # if unit.is_sale:
    #     price_without_sale = round_by_step(round_total_price * 1.33, step=100) - 10
    if unit.final_price > round_total_price:
        # print("Цена дешевле")
        price_without_sale = unit.final_price
        unit.is_sale = True
        unit.save()
        product.is_sale = True
    return {"final_price": round_total_price, "start_price": price_without_sale, "total_profit": round(total_profit),
            "bonus": bonus, "max_bonus": max_bonus_for_product}
