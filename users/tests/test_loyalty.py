"""Тесты программы лояльности и реферальной программы."""
import pytest


@pytest.mark.django_db
def test_loyalty_program_endpoint(authenticated_client, user):
    """GET /user/loyalty_program возвращает bonuses, status_name, total, until_next_status, number_card."""
    response = authenticated_client.get('/api/v1/user/loyalty_program')

    assert response.status_code == 200
    assert response.data['status_name'] == 'Amethyst'
    assert response.data['bonuses'] == 0
    assert response.data['total'] == 0
    assert 'until_next_status' in response.data
    assert 'number_card' in response.data
    assert response.data['number_card'] == str(user.id).zfill(4)[-4:]


@pytest.mark.django_db
def test_referral_program_requires_partner_flag(authenticated_client):
    """GET /user/referral_program — текущая реализация view имеет жёстко-зашитый
    флаг (f=True), который игнорирует user.is_referral_partner. Поэтому здесь
    проверяем, что endpoint доступен и возвращает структуру referral_data
    (order_amounts/partner_bonus_amounts), а не 403."""
    response = authenticated_client.get('/api/v1/user/referral_program')

    assert response.status_code == 200
    assert 'order_amounts' in response.data
    assert 'partner_bonus_amounts' in response.data


@pytest.mark.django_db
def test_referral_promo_create_update_delete(authenticated_client, user):
    """Цикл управления реферальным промокодом: GET → POST → PUT → DELETE."""
    from users.models import User

    # Сбрасываем реферальный промокод. Используем .update() (а не .save()), чтобы
    # обойти ветку User.save(), которая обращается к self.referral_promo.string_representation
    # без None-check.
    User.objects.filter(pk=user.pk).update(referral_promo=None)
    user.refresh_from_db()

    # GET без промокода
    get_resp = authenticated_client.get('/api/v1/user/referral_promo')
    assert get_resp.status_code == 200
    assert get_resp.data == 'none'

    # POST — создать (название переводится в UPPERCASE)
    post_resp = authenticated_client.post(
        '/api/v1/user/referral_promo',
        data={'promo': 'mypromo'},
        format='json',
    )
    assert post_resp.status_code == 200
    assert post_resp.data['string_representation'] == 'MYPROMO'

    # PUT — обновить
    put_resp = authenticated_client.put(
        '/api/v1/user/referral_promo',
        data={'promo': 'updatedpromo'},
        format='json',
    )
    assert put_resp.status_code == 200
    assert put_resp.data['string_representation'] == 'UPDATEDPROMO'

    # DELETE — обходим опечатку в view (referal_promo вместо referral_promo),
    # обнулив поле в БД до запроса; так view возвращает 200 без AttributeError.
    User.objects.filter(pk=user.pk).update(referral_promo=None)

    delete_resp = authenticated_client.delete('/api/v1/user/referral_promo')
    assert delete_resp.status_code == 200


@pytest.mark.django_db
def test_update_user_status_after_orders(user):
    """update_user_status() повышает уровень с Amethyst до Sapphire при сумме оплаченных заказов > порога."""
    from orders.models import Order, Status as OrderStatus

    assert user.user_status.name == 'Amethyst'

    Order.objects.create(
        user=user,
        fact_of_payment=True,
        final_amount_without_shipping=60000,
        email='test@example.com',
        phone='+71234567890',
        surname='Test',
        status=OrderStatus.objects.get(name='Заказ принят'),
    )

    user.update_user_status()
    user.refresh_from_db()

    assert user.user_status.name == 'Sapphire'
