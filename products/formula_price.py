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
PAYMENT_AND_TAX_COMMISSION_FEE_DECIMAL = 1.089324618736383
FIXED_COSTS_ABSOLUTE = 100
PRELIMINARY_MARKUP = {
    "steps_of_order_amount": {
        "1": {
            "min_price_including": 0,
            "max_price_not_including": 2500,
            "preliminary_markup": 500,
            "min_total_cost_including": -487.80487804878055,
            "max_total_cost_not_including": 1751.219512195123
        },
        "2": {
            "min_price_including": 2500,
            "max_price_not_including": 5000,
            "preliminary_markup": 1000,
            "min_total_cost_including": 1263.4146341463425,
            "max_total_cost_not_including": 3502.439024390246
        },
        "3": {
            "min_price_including": 5000,
            "max_price_not_including": 10000,
            "preliminary_markup": 1500,
            "min_total_cost_including": 3014.6341463414656,
            "max_total_cost_not_including": 7492.682926829272
        },
        "4": {
            "min_price_including": 10000,
            "max_price_not_including": 15000,
            "preliminary_markup": 1700,
            "min_total_cost_including": 7297.56097560976,
            "max_total_cost_not_including": 11775.609756097567
        },
        "5": {
            "min_price_including": 15000,
            "max_price_not_including": 24000,
            "preliminary_markup": 2000,
            "min_total_cost_including": 11482.9268292683,
            "max_total_cost_not_including": 19543.414634146353
        },
        "6": {
            "min_price_including": 24000,
            "max_price_not_including": 35000,
            "preliminary_markup": 2200,
            "min_total_cost_including": 19348.29268292684,
            "max_total_cost_not_including": 29200.00000000002
        },
        "7": {
            "min_price_including": 35000,
            "max_price_not_including": 70000,
            "preliminary_markup": 2500,
            "min_total_cost_including": 28907.317073170747,
            "max_total_cost_not_including": 60253.6585365854
        },
        "8": {
            "min_price_including": 70000,
            "max_price_not_including": 90000,
            "preliminary_markup": 4000,
            "min_total_cost_including": 58790.243902439055,
            "max_total_cost_not_including": 76702.43902439027
        },
        "9": {
            "min_price_including": 90000,
            "max_price_not_including": 130000,
            "preliminary_markup": 4500,
            "min_total_cost_including": 76214.6341463415,
            "max_total_cost_not_including": 112039.02439024397
        },
        "10": {
            "min_price_including": 130000,
            "max_price_not_including": 150000,
            "preliminary_markup": 5500,
            "min_total_cost_including": 111063.41463414641,
            "max_total_cost_not_including": 128975.60975609763
        },
        "11": {
            "min_price_including": 150000,
            "max_price_not_including": 200000,
            "preliminary_markup": 6000,
            "min_total_cost_including": 128487.80487804885,
            "max_total_cost_not_including": 173268.29268292693
        },
        "12": {
            "min_price_including": 200000,
            "max_price_not_including": 1000000000000000,
            "preliminary_markup": 7000,
            "min_total_cost_including": 172292.68292682938,
            "max_total_cost_not_including": 895609756090732.1
        }
    }
}

PRIVILEGED_CURRENCY_DIFFERENCE_DECIMAL = 0.05
PRIVILEGED_MARKUP = 1500

FRIENDS_AND_FAMILY_CURRENCY_DIFFERENCE_DECIMAL = 1
FRIENDS_AND_FAMILY_MARKUP = 500


# def check_preliminary_markup():
#     for step in PRELIMINARY_MARKUP["steps_of_order_amount"]:
#         PRELIMINARY_MARKUP["steps_of_order_amount"][step]["min_total_cost_including"] = ((
#                                                                                                  PRELIMINARY_MARKUP[
#                                                                                                      "steps_of_order_amount"][
#                                                                                                      step][
#                                                                                                      "min_price_including"]
#                                                                                                  / PAYMENT_AND_TAX_COMMISSION_FEE_DECIMAL
#                                                                                                  - PRELIMINARY_MARKUP[
#                                                                                                      "steps_of_order_amount"][
#                                                                                                      step][
#                                                                                                      "preliminary_markup"]) / CASHING_OUT_COMMISSION_FEE_DECIMAL)
#         PRELIMINARY_MARKUP["steps_of_order_amount"][step]["max_total_cost_not_including"] = ((
#                                                                                                      PRELIMINARY_MARKUP[
#                                                                                                          "steps_of_order_amount"][
#                                                                                                          step][
#                                                                                                          "max_price_not_including"]
#                                                                                                      / PAYMENT_AND_TAX_COMMISSION_FEE_DECIMAL
#                                                                                                      -
#                                                                                                      PRELIMINARY_MARKUP[
#                                                                                                          "steps_of_order_amount"][
#                                                                                                          step][
#                                                                                                          "preliminary_markup"]) / CASHING_OUT_COMMISSION_FEE_DECIMAL)


def formula_price(product, unit, user_status):
    original_price = unit.original_price
    weight = unit.weight
    delivery = unit.delivery_type
    delivery_price_per_kg_in_rub = delivery.delivery_price_per_kg_in_rub
    delivery_decimal_insurance = delivery.decimal_insurance
    delivery_absolute_insurance = delivery.absolute_insurance
    delivery_extra_charge = delivery.extra_charge
    genders = list(product.gender.all().values_list("name", flat=True))  # ["M", "F", "K"]
    categories = list(product.categories.all().values_list("name", flat=True))  # на русском ["Обувь", "Вся обувь"]
    poizon_abroad = unit.platform_info.poizon.poizon_abroad
    status_name = user_status.name  # Amethyst

    if status_name == "Privileged":
        converted_into_rub_price = original_price * CURRENCY_RATE_CNY
        shipping_cost = (delivery_price_per_kg_in_rub * weight + converted_into_rub_price * delivery_decimal_insurance
                         + delivery_absolute_insurance)
        cost_without_shipping = (converted_into_rub_price * COMMISSION_FEE_RELATIVE_DECIMAL + converted_into_rub_price
                                 * PRIVILEGED_CURRENCY_DIFFERENCE_DECIMAL + COMMISSION_FEE_ABSOLUTE)
        total_cost = cost_without_shipping + shipping_cost + FIXED_COSTS_ABSOLUTE
        total_profit = PRIVILEGED_MARKUP + converted_into_rub_price * PRIVILEGED_CURRENCY_DIFFERENCE_DECIMAL
        total_price = total_cost + PRIVILEGED_MARKUP
    elif status_name == "Friends & Family":
        converted_into_rub_price = original_price * CURRENCY_RATE_CNY
        shipping_cost = (delivery_price_per_kg_in_rub * weight + converted_into_rub_price * delivery_decimal_insurance
                         + delivery_absolute_insurance)
        cost_without_shipping = converted_into_rub_price * COMMISSION_FEE_RELATIVE_DECIMAL + COMMISSION_FEE_ABSOLUTE
        total_cost = cost_without_shipping + shipping_cost + FIXED_COSTS_ABSOLUTE
        total_profit = FRIENDS_AND_FAMILY_MARKUP
        total_price = total_cost + FRIENDS_AND_FAMILY_MARKUP
    else:
        if product.actual_price:
            total_profit = unit.total_profit
            bonus = unit.bonus
            if status_name == "Amethyst":
                bonus_max = 250
                bonus_from_profit = round(0.1 * total_profit)
                bonus = min(bonus_max, bonus_from_profit)
            elif status_name == "Sapphire":
                bonus_max = 500
                bonus_from_profit = round(0.15 * total_profit)
                bonus = min(bonus_max, bonus_from_profit)
            elif status_name == "Emerald":
                bonus_max = 750
                bonus_from_profit = round(0.2 * total_profit)
                bonus = min(bonus_max, bonus_from_profit)
            elif status_name == "Ruby":
                bonus_max = 1000
                bonus_from_profit = round(0.25 * total_profit)
                bonus = min(bonus_max, bonus_from_profit)
            elif status_name == "Diamond":
                bonus_max = 1500
                bonus_from_profit = round(0.3 * total_profit)
                bonus = min(bonus_max, bonus_from_profit)
            return {"final_price": unit.final_price,
                    "start_price": unit.start_price,
                    "total_profit": unit.total_profit,
                    "bonus": bonus}
        converted_into_rub_price = original_price * CURRENCY_RATE_CNY
        shipping_cost = (delivery_price_per_kg_in_rub * weight + converted_into_rub_price * delivery_decimal_insurance
                         + delivery_absolute_insurance)
        cost_without_shipping = converted_into_rub_price * COMMISSION_FEE_RELATIVE_DECIMAL + COMMISSION_FEE_ABSOLUTE

        total_cost = cost_without_shipping + shipping_cost
        total_cost_after_cashing_out = total_cost * CASHING_OUT_COMMISSION_FEE_DECIMAL

        # check_preliminary_markup()

        step_of_order_amount = "12"
        preliminary_markup = 0
        extra_markup = 0
        for step in PRELIMINARY_MARKUP["steps_of_order_amount"]:
            if (PRELIMINARY_MARKUP["steps_of_order_amount"][step]["min_total_cost_including"] <= total_cost <
                    PRELIMINARY_MARKUP["steps_of_order_amount"][step]["max_total_cost_not_including"]):
                step_of_order_amount = step
                preliminary_markup = PRELIMINARY_MARKUP["steps_of_order_amount"][step]["preliminary_markup"]

        if int(step_of_order_amount) == 7 and poizon_abroad:
            extra_markup += 1000
        elif int(step_of_order_amount) > 7 and poizon_abroad:
            extra_markup += 1500

        if genders == ["F"] and int(step_of_order_amount) >= 5 and "Обувь" not in categories:
            extra_markup += 500

        if genders == ["F"] and int(
                step_of_order_amount) >= 7 and "Обувь" not in categories and "Аксессуары" in categories:
            extra_markup += 1000

        if genders == ["F"] and int(
                step_of_order_amount) >= 9 and "Обувь" not in categories and "Аксессуары" in categories:
            extra_markup += 1000

        if genders == ["M"] and int(
                step_of_order_amount) >= 8 and "Обувь" not in categories and "Аксессуары" in categories:
            extra_markup += 1000

        total_markup = preliminary_markup + extra_markup + delivery_extra_charge
        total_price_before_payment_and_tax_commission = (total_cost_after_cashing_out + total_markup
                                                         + FIXED_COSTS_ABSOLUTE)
        total_profit = total_markup
        total_price = total_price_before_payment_and_tax_commission * PAYMENT_AND_TAX_COMMISSION_FEE_DECIMAL

    round_total_price = round_by_step(total_price + 10, step=100) - 10
    total_round_markup = round_total_price - total_price
    total_profit += total_round_markup

    if status_name == "Amethyst":
        bonus_max = 250
        bonus_from_profit = round(0.1 * total_profit)
        bonus = min(bonus_max, bonus_from_profit)
    elif status_name == "Sapphire":
        bonus_max = 500
        bonus_from_profit = round(0.15 * total_profit)
        bonus = min(bonus_max, bonus_from_profit)
    elif status_name == "Emerald":
        bonus_max = 750
        bonus_from_profit = round(0.2 * total_profit)
        bonus = min(bonus_max, bonus_from_profit)
    elif status_name == "Ruby":
        bonus_max = 1000
        bonus_from_profit = round(0.25 * total_profit)
        bonus = min(bonus_max, bonus_from_profit)
    elif status_name == "Diamond":
        bonus_max = 1500
        bonus_from_profit = round(0.3 * total_profit)
        bonus = min(bonus_max, bonus_from_profit)
    else:
        bonus = 0
    print(total_profit, round_total_price)
    return {"final_price": round_total_price, "start_price": round_total_price, "total_profit": round(total_profit),
            "bonus": bonus}
