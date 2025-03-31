from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.reverse import reverse
from products.models import Product, Category, Brand
from shipping.models import ProductUnit, Platform, DeliveryType
from shipping.serializers import ProductUnitSerializer
from users.models import User, Gender
from orders.models import ShoppingCart
from wishlist.models import Wishlist
from products.serializers import ProductSerializer


class YourAPITests(APITestCase):
    def setUp(self):
        # Логика, которая будет выполняться перед каждым тестом.
        self.category = Category(name='Обувь')
        self.category.save()
        self.category2 = Category(name='Кроссовки')
        self.category2.save()
        self.category2.parent_category = self.category
        self.category2.save()

        self.brand = Brand(name="Nike")
        self.brand.save()

        self.product = Product(model="Air Force 1",
                               colorway="White",
                               manufacturer_sku="123",
                               russian_name="Эйр Форс 1",
                               slug="123"
                               )
        self.product.save()
        self.product.brands.add(self.brand)
        self.product.categories.add(self.category)
        self.product.slug = ""
        self.product.save()

        self.platform = Platform(platform='Poizon', site="Poizon")
        self.delivery = DeliveryType(name="Садовод")
        self.platform.save()
        self.delivery.save()

        self.product_unit = ProductUnit(product=self.product, delivery_type=self.delivery, platform=self.platform,
                                        final_price=100)
        self.product_unit.save()
        self.gender = Gender(name="Male")
        self.gender.save()
        genders = {'male': 1, "female": 2}
        self.new_user = User(username="artem@mail.ru", password="1234", first_name="artem",
                             last_name="sh", gender_id=genders["male"])
        self.new_user.set_password("1234")
        self.new_user.save()
        # создание корзины и вл для пользователя
        self.cart = ShoppingCart(user_id=self.new_user.id)
        self.wl = Wishlist(user_id=self.new_user.id)
        self.cart.save()
        self.wl.save()

    def tearDown(self):
        # Логика, которая будет выполняться после каждого теста.
        pass

    def test_view_product_unit_for_product_id(self):
        url = reverse("product-list")
        response = self.client.get(url, format='json')
        self.assertEquals(response.json().get("count"), 1)
