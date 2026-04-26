"""Тесты модуля заказов: корзина, расчёт доставки, оформление заказа."""
import pytest


MOCK_PRICE = {
    'start_price': 15000,
    'final_price': 12000,
    'bonus': 500,
    'total_profit': 0,
}


@pytest.fixture
def mock_pricing(mocker):
    """Мокаем formula_price во всех модулях, где он импортируется напрямую,
    + сопутствующие методы обновления цен (чтобы не дёргали внешние API)."""
    for path in [
        'orders.models.formula_price',
        'products.models.formula_price',
        'shipping.serializers.formula_price',
        'promotions.views.formula_price',
    ]:
        mocker.patch(path, return_value=MOCK_PRICE)
    mocker.patch('products.models.Product.update_price')
    mocker.patch('products.tools.platform_update_price')
    return MOCK_PRICE


def _put_in_cart(user, product_unit):
    from orders.models import ShoppingCart
    cart = ShoppingCart.objects.get(user=user)
    cart.product_units.add(product_unit)
    cart.unit_order = [product_unit.id]
    cart.save()
    return cart


@pytest.mark.django_db
def test_add_to_cart(authenticated_client, user, product_unit, mock_pricing):
    """POST /order/cart/<user_id>/<product_unit_id> добавляет товар в корзину."""
    url = f'/api/v1/order/cart/{user.id}/{product_unit.id}'
    response = authenticated_client.post(url)

    assert response.status_code == 200

    from orders.models import ShoppingCart
    cart = ShoppingCart.objects.get(user=user)
    assert product_unit in cart.product_units.all()
    assert product_unit.id in cart.unit_order


@pytest.mark.django_db
def test_remove_from_cart(authenticated_client, user, product_unit, mock_pricing):
    """DELETE /order/cart/<user_id>/<product_unit_id> убирает товар, корзина пересчитывается."""
    _put_in_cart(user, product_unit)

    url = f'/api/v1/order/cart/{user.id}/{product_unit.id}'
    response = authenticated_client.delete(url)

    assert response.status_code == 200

    from orders.models import ShoppingCart
    cart = ShoppingCart.objects.get(user=user)
    assert product_unit not in cart.product_units.all()


@pytest.mark.django_db
def test_get_cart(authenticated_client, user, product_unit, mock_pricing):
    """GET /order/cart/<user_id> возвращает корзину с агрегированными суммами."""
    _put_in_cart(user, product_unit)

    url = f'/api/v1/order/cart/{user.id}'
    response = authenticated_client.get(url)

    assert response.status_code == 200
    # ShoppingCartSerializer возвращает поля корзины (final_amount/total_amount/sale/bonus и т.п.)
    assert 'final_amount' in response.data or 'total_amount' in response.data


@pytest.mark.django_db
def test_use_bonus(authenticated_client, user, product_unit, mock_pricing):
    """POST /order/cart/use_bonus списывает указанные бонусы, final_amount уменьшается."""
    from promotions.models import AccrualBonus

    accrual = AccrualBonus.objects.create(amount=1000)
    user.bonuses.accrual.add(accrual)
    user.bonuses.update_total_amount()

    _put_in_cart(user, product_unit)

    response = authenticated_client.post(
        '/api/v1/order/cart/use_bonus',
        data={'bonus': 100},
        format='json',
    )

    assert response.status_code == 200
    from orders.models import ShoppingCart
    cart = ShoppingCart.objects.get(user=user)
    assert cart.bonus_sale == 100


@pytest.mark.django_db
def test_delivery_info_calculates_boxberry(
    authenticated_client, user, product_unit, mock_pricing, mocker
):
    """POST /order/delivery_info с delivery_type=1 (ПВЗ Boxberry).
    Запросы к api.boxberry.ru замоканы; ответ должен содержать sum_part/days_to_client."""
    mocker.patch(
        'orders.tools.requests.get',
        return_value=mocker.Mock(
            status_code=200,
            json=lambda: {'price_base': 200, 'price_service': 50, 'delivery_period': 5},
        ),
    )

    _put_in_cart(user, product_unit)

    response = authenticated_client.post(
        '/api/v1/order/delivery_info',
        data={'delivery_type': 1, 'target': '02743'},
        format='json',
    )

    assert response.status_code == 200
    assert 'sum_part' in response.data
    assert 'days_to_client' in response.data
    # Округление до 50 (round_to_nearest)
    assert response.data['sum_part'] % 50 == 0


@pytest.mark.django_db
def test_checkout_creates_order(
    authenticated_client, user, product_unit, mock_pricing, mocker
):
    """POST /order/checkout/<user_id> создаёт Order со статусом «Заказ принят»."""
    mocker.patch(
        'orders.tools.requests.get',
        return_value=mocker.Mock(
            status_code=200,
            json=lambda: {'price_base': 200, 'price_service': 50, 'delivery_period': 5},
        ),
    )
    mocker.patch('orders.tools.requests.post')  # send_email_*

    cart = _put_in_cart(user, product_unit)
    cart.total()  # пересчитать total_amount/final_amount через замоканный formula_price,
                  # иначе evenly_distribute_discount упадёт с ZeroDivisionError на total_cost=0
    cart.delivery_info = {'days_to_client': 5}
    cart.save()

    payload = {
        'email': 'test@example.com',
        'phone': '+71234567890',
        'name': 'Тест',
        'surname': 'Пользователь',
        'patronymic': '',
        'delivery_type': 0,
        'consolidation': True,
        'comment': '',
    }

    url = f'/api/v1/order/checkout/{user.id}'
    response = authenticated_client.post(url, data=payload, format='json')

    assert response.status_code == 200
    assert response.data['fact_of_payment'] is False
    assert response.data['number']
    assert response.data['status']['name'] == 'Заказ принят'

    from orders.models import Order
    order = Order.objects.get(user=user)
    assert order.email == 'test@example.com'
    assert order.surname == 'Пользователь'
