import pytest
from rest_framework.test import APIClient


@pytest.fixture(autouse=True)
def _setup_reference_data(db):
    """Справочные сущности, без которых модели и эндпоинты падают.

    Запускается перед каждым тестом. get_or_create переиспользует записи
    при --reuse-db.
    """
    from users.models import UserStatus, Gender
    from orders.models import Status as OrderStatus
    from shipping.models import DeliveryType, Platform
    from utils.models import Currency

    UserStatus.objects.get_or_create(
        name='Amethyst',
        defaults={
            'total_orders_amount': 0,
            'percentage_bonuses': 10,
            'free_ship_amount': 20000,
            'base': True,
            'start_bonuses': True,
        },
    )
    UserStatus.objects.get_or_create(
        name='Sapphire',
        defaults={
            'total_orders_amount': 50000,
            'percentage_bonuses': 12,
            'free_ship_amount': 20000,
            'base': True,
        },
    )

    Gender.objects.get_or_create(name='M')
    Gender.objects.get_or_create(name='F')

    for status_name in [
        'Заказ принят',
        'Оплачен',
        'Отменён',
        'В пути до международного склада',
        'В пути до московского склада',
        'Прибыл в Москву',
        'Частично прибыл в Москву',
        'Передан в службу доставки по России',
        'Частично передан в службу доставки по России',
        'Доставлен',
    ]:
        OrderStatus.objects.get_or_create(name=status_name)

    DeliveryType.objects.get_or_create(
        name='pending', defaults={'days_min': 7, 'days_max': 14}
    )
    DeliveryType.objects.get_or_create(
        name='Boxberry', defaults={'days_min': 5, 'days_max': 10}
    )
    Platform.objects.get_or_create(platform='Poizon', defaults={'site': 'Poizon'})

    Currency.objects.get_or_create(name='pending')
    Currency.objects.get_or_create(name='RUB')


@pytest.fixture(autouse=True)
def _patch_user_save(monkeypatch):
    """User.save() в проде требует SizeTable("Shoes_Adults"/"Clothes_Men") для
    установки preferred_size_row. В тестах нам это не нужно — принудительно
    передаём size_info=True, чтобы пропустить эту ветку.
    """
    from users.models import User
    original_save = User.save

    def patched(self, *args, **kwargs):
        kwargs.setdefault('size_info', True)
        return original_save(self, *args, **kwargs)

    monkeypatch.setattr(User, 'save', patched)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(_setup_reference_data, _patch_user_save):
    """Пользователь, созданный реальной register_user() — с корзиной, бонусами и
    реферальным промокодом."""
    from users.tools import register_user
    from users.models import User

    data = {
        'username': 'test@example.com',
        'password': 'TestPass123',
        'first_name': 'Тест',
        'last_name': 'Пользователь',
        'is_mailing_list': False,
    }
    register_user(data)
    return User.objects.get(username='test@example.com')


@pytest.fixture
def authenticated_client(user):
    """APIClient с JWT-токеном пользователя в Authorization."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def product_unit(_setup_reference_data):
    """Минимальный стек Product → ProductUnit."""
    from products.models import Product, Brand, Category
    from shipping.models import ProductUnit, DeliveryType, Platform

    brand = Brand.objects.create(name='TestBrand')
    category = Category.objects.create(name='Кроссовки')

    product = Product.objects.create(
        model='Test Sneaker',
        colorway='White',
        manufacturer_sku='TEST-001',
        slug='test-sneaker-white',
    )
    product.brands.add(brand)
    product.categories.add(category)

    delivery_type = DeliveryType.objects.get(name='Boxberry')
    platform = Platform.objects.get(platform='Poizon')

    return ProductUnit.objects.create(
        product=product,
        delivery_type=delivery_type,
        platform=platform,
        start_price=15000,
        final_price=12000,
        availability=True,
    )


@pytest.fixture
def promo_code(user):
    from promotions.models import PromoCode
    from datetime import date, timedelta
    return PromoCode.objects.create(
        string_representation='SAVE10',
        discount_percentage=10,
        active_status=True,
        active_until_date=date.today() + timedelta(days=30),
        max_activation_count=100,
        owner=None,
    )


@pytest.fixture
def expired_promo(user):
    from promotions.models import PromoCode
    from datetime import date, timedelta
    return PromoCode.objects.create(
        string_representation='EXPIRED',
        discount_percentage=20,
        active_status=True,
        active_until_date=date.today() - timedelta(days=1),
        max_activation_count=100,
        owner=None,
    )


MOCK_PRICE = {
    'start_price': 15000,
    'final_price': 12000,
    'bonus': 500,
    'total_profit': 0,
}
