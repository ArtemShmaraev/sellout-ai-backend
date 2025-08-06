from orders.tools import round_to_nearest

def formula_price(product, unit, user_status):


    genders = product.gender.all().values_list("name", flat=True)  # ["M", "F", "K"]
    categories = product.categories.all().values_list("name", flat=True)  # на русском ["Обувь", "Вся обувь"]
    poizon_abroad = unit.delivery_type.poizon_abroad
    weight = unit.weight
    status_name = user_status.name  # Amethyst
    delivery = unit.delivery_type
    delivery_price_per_kg_in_rub = delivery.delivery_price_per_kg_in_rub
    extra_charge = delivery.extra_charge
    original_price = unit.original_price  # цена в юанях


    final_price = unit.final_price * 14
    final_price += 3000
    start_price = final_price
    if product.is_sale:
        start_price *= 1.2

    # print(categories)
    # print(genders)

    return {"final_price": round_to_nearest(final_price, step=500) - 10, "start_price": round_to_nearest(start_price, step=500) - 10}
