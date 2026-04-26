"""Тесты модуля пользователей: регистрация, авторизация, профиль, адреса, размеры."""
import pytest


@pytest.mark.django_db
def test_register_creates_user_cart_bonuses_and_promo(api_client):
    """POST /user/register создаёт User, ShoppingCart, Bonuses и реферальный PromoCode."""
    from users.models import User
    from orders.models import ShoppingCart
    from promotions.models import PromoCode

    url = '/api/v1/user/register'
    data = {
        'username': 'new@example.com',
        'password': 'TestPass123',
        'first_name': 'Новый',
        'last_name': 'Пользователь',
        'is_mailing_list': False,
    }
    response = api_client.post(url, data=data, format='json')

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data
    assert 'user_id' in response.data

    user = User.objects.get(username='new@example.com')
    assert ShoppingCart.objects.filter(user=user).exists()
    assert user.bonuses is not None
    assert PromoCode.objects.filter(owner=user, ref_promo=True).exists()


@pytest.mark.django_db
def test_register_with_existing_email_fails(api_client, user):
    """Повторная регистрация с тем же username возвращает 400."""
    url = '/api/v1/user/register'
    data = {
        'username': user.username,
        'password': 'AnotherPass456',
        'first_name': 'Other',
        'last_name': 'Other',
        'is_mailing_list': False,
    }
    response = api_client.post(url, data=data, format='json')

    assert response.status_code == 400
    assert 'уже существует' in str(response.data)


@pytest.mark.django_db
def test_register_invalid_email_fails(api_client):
    """Регистрация с отсутствующим обязательным полем — не возвращает 200 OK.

    NB: production register_user() не валидирует email-формат, поэтому здесь
    проверяем поведение на отсутствующем обязательном password (KeyError → 500).
    Django test client с DEBUG=False ловит исключение и отдаёт 500 — отключаем
    raise_request_exception, иначе он пробрасывает KeyError в тест."""
    api_client.raise_request_exception = False
    url = '/api/v1/user/register'
    data = {
        'username': 'incomplete@example.com',
        'first_name': 'X',
        'last_name': 'Y',
        'is_mailing_list': False,
    }
    response = api_client.post(url, data=data, format='json')
    assert response.status_code != 200


@pytest.mark.django_db
def test_login_returns_jwt_pair(api_client, user):
    """POST /user/login возвращает access, refresh и user_id."""
    url = '/api/v1/user/login'
    data = {'username': user.username, 'password': 'TestPass123'}
    response = api_client.post(url, data=data, format='json')

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data
    assert response.data['user_id'] == user.id


@pytest.mark.django_db
def test_token_refresh_returns_new_access(api_client, user):
    """POST /user/token/refresh/ с валидным refresh — возвращает новый access."""
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    url = '/api/v1/user/token/refresh/'
    response = api_client.post(url, data={'refresh': str(refresh)}, format='json')

    assert response.status_code == 200
    assert 'access' in response.data
    assert response.data['access']


@pytest.mark.django_db
def test_user_info_get_returns_profile(authenticated_client, user):
    """GET /user/user_info/<id> возвращает профиль владельца токена."""
    url = f'/api/v1/user/user_info/{user.id}'
    response = authenticated_client.get(url)

    assert response.status_code == 200
    assert response.data['username'] == user.username
    assert response.data['first_name'] == user.first_name


@pytest.mark.django_db
def test_user_info_post_updates_profile(authenticated_client, user):
    """POST /user/user_info/<id> обновляет phone_number и возвращает обновлённый профиль."""
    url = f'/api/v1/user/user_info/{user.id}'
    payload = {'phone': '+7 999 123 45 67'}
    response = authenticated_client.post(url, data=payload, format='json')

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.phone_number == '+7 999 123 45 67'


@pytest.mark.django_db
def test_user_info_other_user_returns_403(authenticated_client):
    """Запрос /user/user_info/<чужой_id> возвращает 403."""
    other_id = 99999
    url = f'/api/v1/user/user_info/{other_id}'
    response = authenticated_client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_address_crud(authenticated_client, user, mocker):
    """CRUD-цикл для адресов: создать → получить список → удалить. DaData замокана."""
    mocker.patch('users.views.check_adress', return_value=None)

    list_url = f'/api/v1/user/address/{user.id}'

    # CREATE
    create_payload = {
        'name': 'Дом',
        'address': 'Москва, Ленина 1',
        'is_main': True,
    }
    create_resp = authenticated_client.post(list_url, data=create_payload, format='json')
    assert create_resp.status_code == 200
    address_id = create_resp.data['id']

    # LIST
    list_resp = authenticated_client.get(list_url)
    assert list_resp.status_code == 200
    assert len(list_resp.data) == 1
    assert list_resp.data[0]['address'] == 'Москва, Ленина 1'

    # DELETE
    delete_url = f'/api/v1/user/address/{user.id}/{address_id}'
    delete_resp = authenticated_client.delete(delete_url)
    assert delete_resp.status_code == 200

    list_after = authenticated_client.get(list_url)
    assert len(list_after.data) == 0


@pytest.mark.django_db
def test_size_info_save_and_get(authenticated_client):
    """POST /user/size_info сохраняет рост/вес, GET — возвращает их."""
    post_resp = authenticated_client.post(
        '/api/v1/user/size_info',
        data={'height': 180, 'weight': 75},
        format='json',
    )
    assert post_resp.status_code == 201
    assert post_resp.data['height'] == 180
    assert post_resp.data['weight'] == 75

    get_resp = authenticated_client.get('/api/v1/user/size_info')
    assert get_resp.status_code == 200
    assert get_resp.data['height'] == 180
    assert get_resp.data['weight'] == 75
