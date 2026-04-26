"""Тесты промокодов, бонусов и реферальной программы."""
import time
from datetime import date, timedelta

import pytest


@pytest.mark.django_db
def test_promo_percentage_discount(user):
    """Процентный промокод 10% применяется, promo_sale = final_amount × 0.1."""
    from promotions.models import PromoCode
    from orders.models import ShoppingCart

    promo = PromoCode.objects.create(
        string_representation='SAVE10',
        discount_percentage=10,
        active_status=True,
        active_until_date=date.today() + timedelta(days=30),
        max_activation_count=100,
        owner=None,
    )

    cart = ShoppingCart.objects.get(user=user)
    cart.final_amount = 10000
    cart.save()

    result = promo.check_promo_in_cart(cart)

    assert result['flag'] == 1
    assert result['promo_sale'] == 1000


@pytest.mark.django_db
def test_promo_absolute_discount(user):
    """Абсолютный промокод (1000₽) даёт скидку = 1000."""
    from promotions.models import PromoCode
    from orders.models import ShoppingCart

    promo = PromoCode.objects.create(
        string_representation='ABS1000',
        discount_absolute=1000,
        active_status=True,
        active_until_date=date.today() + timedelta(days=30),
        max_activation_count=100,
        owner=None,
    )

    cart = ShoppingCart.objects.get(user=user)
    cart.final_amount = 5000
    cart.save()

    result = promo.check_promo_in_cart(cart)

    assert result['flag'] == 1
    assert result['promo_sale'] == 1000


@pytest.mark.django_db
def test_promo_bonus_type(user):
    """Промокод с promo_bonus>0 начисляет бонусы вместо скидки."""
    from promotions.models import PromoCode
    from orders.models import ShoppingCart

    promo = PromoCode.objects.create(
        string_representation='BONUS500',
        promo_bonus=500,
        active_status=True,
        active_until_date=date.today() + timedelta(days=30),
        max_activation_count=100,
        owner=None,
    )

    cart = ShoppingCart.objects.get(user=user)
    cart.final_amount = 5000
    cart.save()

    result = promo.check_promo_in_cart(cart)

    assert result['flag'] == 1
    assert result['promo_bonus'] == 500
    assert result['promo_sale'] == 0


@pytest.mark.django_db
def test_promo_referral_first_order(user):
    """Реферальный промокод применяется к корзине пользователя БЕЗ заказов;
    bonus берётся из owner.referral_data['client_bonus_amounts']."""
    from users.models import User
    from users.tools import register_user
    from orders.models import ShoppingCart

    register_user({
        'username': 'owner@example.com',
        'password': 'OwnerPass1',
        'first_name': 'Owner',
        'last_name': 'Owner',
        'is_mailing_list': False,
    })
    owner = User.objects.get(username='owner@example.com')
    ref_promo = owner.referral_promo
    assert ref_promo is not None and ref_promo.ref_promo

    cart = ShoppingCart.objects.get(user=user)
    cart.final_amount = 20000  # > 15000 → второй порог
    cart.save()

    result = ref_promo.check_promo_in_cart(cart)

    assert result['flag'] == 1
    # client_bonus_amounts по умолчанию = [1000, 1000, 1000, 1000, 1000, 1000]
    assert result['promo_bonus'] == 1000


@pytest.mark.django_db
def test_promo_referral_user_already_has_orders(user):
    """Реферальный промокод НЕ применяется, если у пользователя уже есть оплаченный заказ."""
    from users.models import User
    from users.tools import register_user
    from orders.models import ShoppingCart, Order, Status as OrderStatus

    register_user({
        'username': 'owner@example.com',
        'password': 'OwnerPass1',
        'first_name': 'Owner',
        'last_name': 'Owner',
        'is_mailing_list': False,
    })
    owner = User.objects.get(username='owner@example.com')
    ref_promo = owner.referral_promo

    Order.objects.create(
        user=user,
        fact_of_payment=True,
        final_amount=10000,
        email='test@example.com',
        phone='+71234567890',
        surname='Test',
        status=OrderStatus.objects.get(name='Заказ принят'),
    )

    cart = ShoppingCart.objects.get(user=user)
    cart.final_amount = 20000
    cart.save()

    result = ref_promo.check_promo_in_cart(cart)

    # ref-ветка пропускается (есть заказ); discount_percentage=discount_absolute=promo_bonus=0
    # → promo_sale=0, promo_bonus=0 → flag=0.
    assert result['flag'] == 0


@pytest.mark.django_db
def test_promo_expired_rejected(user, expired_promo):
    """Промокод с истёкшим active_until_date возвращает flag=0."""
    from orders.models import ShoppingCart

    cart = ShoppingCart.objects.get(user=user)
    cart.final_amount = 5000
    cart.save()

    result = expired_promo.check_promo_in_cart(cart)

    assert result['flag'] == 0
    assert 'не активен' in result['message']


@pytest.mark.django_db
def test_promo_activation_limit_exceeded(user):
    """activation_count >= max_activation_count, unlimited=False → flag=0."""
    from promotions.models import PromoCode
    from orders.models import ShoppingCart

    promo = PromoCode.objects.create(
        string_representation='LIMIT',
        discount_percentage=10,
        active_status=True,
        active_until_date=date.today() + timedelta(days=30),
        max_activation_count=5,
        activation_count=5,
        unlimited=False,
        owner=None,
    )

    cart = ShoppingCart.objects.get(user=user)
    cart.final_amount = 5000
    cart.save()

    result = promo.check_promo_in_cart(cart)

    assert result['flag'] == 0
    assert 'закончился' in result['message']


@pytest.mark.django_db
def test_promo_unlimited_ignores_limit(user):
    """unlimited=True игнорирует превышение лимита активаций."""
    from promotions.models import PromoCode
    from orders.models import ShoppingCart

    promo = PromoCode.objects.create(
        string_representation='UNLIMITED',
        discount_percentage=10,
        active_status=True,
        active_until_date=date.today() + timedelta(days=30),
        max_activation_count=1,
        activation_count=999,
        unlimited=True,
        owner=None,
    )

    cart = ShoppingCart.objects.get(user=user)
    cart.final_amount = 5000
    cart.save()

    result = promo.check_promo_in_cart(cart)

    assert result['flag'] == 1


@pytest.mark.django_db
def test_promo_check_endpoint_returns_status(authenticated_client, user, promo_code):
    """POST /api/v1/promo/check/<user_id> с валидным промокодом возвращает status=True."""
    from orders.models import ShoppingCart

    cart = ShoppingCart.objects.get(user=user)
    cart.final_amount = 5000
    cart.save()

    url = f'/api/v1/promo/check/{user.id}'
    response = authenticated_client.post(url, data={'promo': 'SAVE10'}, format='json')

    assert response.status_code == 200
    assert response.data['status'] is True
    assert 'message' in response.data


@pytest.mark.django_db
def test_promo_check_invalid_promo_404(authenticated_client, user):
    """POST /api/v1/promo/check/<user_id> с несуществующим промокодом — message «Промокод не найден»."""
    url = f'/api/v1/promo/check/{user.id}'
    response = authenticated_client.post(url, data={'promo': 'NONEXISTENT'}, format='json')

    assert response.status_code == 200
    assert response.data['status'] is False
    assert 'не найден' in response.data['message']


@pytest.mark.django_db
def test_bonuses_deduct_lifo(user):
    """deduct_bonus(amount) списывает бонусы из последних начислений (LIFO по дате)."""
    from promotions.models import AccrualBonus

    bonuses = user.bonuses

    a1 = AccrualBonus.objects.create(amount=100)
    bonuses.accrual.add(a1)
    time.sleep(0.01)
    a2 = AccrualBonus.objects.create(amount=200)
    bonuses.accrual.add(a2)
    time.sleep(0.01)
    a3 = AccrualBonus.objects.create(amount=300)
    bonuses.accrual.add(a3)

    bonuses.update_total_amount()
    bonuses.refresh_from_db()
    assert bonuses.total_amount == 600

    # Списываем 150 — должно уйти из самого нового (a3=300)
    bonuses.deduct_bonus(150)

    a1.refresh_from_db()
    a2.refresh_from_db()
    a3.refresh_from_db()

    assert a3.amount == 150
    assert a2.amount == 200
    assert a1.amount == 100


@pytest.mark.django_db
def test_bonuses_total_amount_signal(user):
    """После bonuses.accrual.add(new) сигнал m2m_changed пересчитывает total_amount."""
    from promotions.models import AccrualBonus

    bonuses = user.bonuses
    initial_total = bonuses.total_amount

    new_accrual = AccrualBonus.objects.create(amount=500)
    bonuses.accrual.add(new_accrual)

    bonuses.refresh_from_db()
    assert bonuses.total_amount == initial_total + 500
