from orders.tools import round_to_nearest


def formula_price(product, original_price):
    price = original_price * 13.96
    if "accessories" in product.categories.all().values_list("name", flat=True):
        price += 1000
    price += 1500
    price *= 1.025
    price += 1500
    price /= 0.918
    return round_to_nearest(price, step=500) - 10
