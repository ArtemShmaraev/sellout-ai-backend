import requests

import math

from django.db.models import Sum



def get_delivery_price(units, target_start, target, zip):
    sum = 0
    sum_weight = 0
    delivery_price = 0
    for unit in units:
        sum += unit.final_price
        sum_weight += unit.weight
    delivery_info = get_delivery_costs(sum_weight, sum, target_start, target, zip)
    if "price_base" in delivery_info:
        delivery_price += (delivery_info['price_base'] * 1.25) + delivery_info['price_service']
    return delivery_price


def get_delivery_costs(weight, ordersum, targetstart, target, zip):
    url = "http://api.boxberry.ru/json.php"
    params = {
        "method": "DeliveryCosts",
        "weight": weight * 1000,
        "target": target,
        "ordersum": ordersum,
        "targetstart": targetstart,
        "token": "f985be8eebb3a5ba0c954d598f176cda",
        "zip": zip
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Ошибка {response.status_code}: {response.text}")
        return None


def round_to_nearest(value, step=50):
    return math.ceil(value / step) * step


def send_email_confirmation_order(order, email):
    url = "https://sellout.su/mail/send_customer_service_mail/"
    params = {
        "recipient_email": email,
        "body": order
    }
    requests.get(url, params=params)
    return requests.status_codes
