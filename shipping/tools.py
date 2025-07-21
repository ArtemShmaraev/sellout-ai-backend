import requests

def get_delivery_costs(weight, target, ordersum, deliverysum, targetstart, token, zip):
    url = "http://api.boxberry.ru/json.php"
    params = {
        "method": "DeliveryCosts",
        "weight": weight,
        "target": target,
        "ordersum": ordersum,
        "targetstart": targetstart,
        "token": token,
        "zip": zip
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Ошибка {response.status_code}: {response.text}")
        return None

