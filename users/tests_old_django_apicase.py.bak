

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.reverse import reverse
from products.models import Product, Category, Brand
from shipping.models import ProductUnit, Platform, DeliveryType
from shipping.serializers import ProductUnitSerializer
from users.models import User, Gender
from orders.models import ShoppingCart
from users.serializers import UserSerializer
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

    def test_reg_user(self):
        url = reverse("register")
        data = {'username': "tema@mail.ru",
                "password": "1234",
                "first_name": "artem",
                "last_name": "ash",
                "gender": "male"}
        response = self.client.post(url, format='json', data=data)
        self.assertIn('refresh', response.json())


    def test_login_user(self):
        url = reverse("token_obtain_pair")
        data = {"username": "artem@mail.ru",
                "password": "1234"}
        response = self.client.post(url, format='json', data=data)
        self.access = response.json().get("access")

        url = reverse("product_main_view", kwargs={"product_id": 1, "user_id": 1})
        # headers = {"Authorization": f"Bearer {self.access}"}

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        response = client.get(url)
        self.assertEquals(response.json().get("model"), "Air Force 1")
        self.assertEquals(response.json().get("in_wishlist"), False)

    def test_user_info(self):
        url = reverse("token_obtain_pair")
        data = {"username": "artem@mail.ru",
                "password": "1234"}
        response = self.client.post(url, format='json', data=data)
        self.access = response.json().get("access")

        url = reverse("user_info", kwargs={"user_id": 1})
        # headers = {"Authorization": f"Bearer {self.access}"}

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        response = client.get(url)
        self.assertEquals(response.json(), UserSerializer(self.new_user).data)

        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(YourModel.objects.count(), 1)
        # self.assertEqual(YourModel.objects.get().name, 'Test')

    # def test_retrieve_object(self):
    #     your_model = YourModel.objects.create(name='Test')
    #     url = reverse('your_model-detail',
    #                   args=[your_model.id])  # Замените 'your_model-detail' на фактическое имя URL-маршрута
    #     response = self.client.get(url)
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['name'], 'Test')
    #
    # def test_update_object(self):
    #     your_model = YourModel.objects.create(name='Test')
    #     url = reverse('your_model-detail',
    #                   args=[your_model.id])  # Замените 'your_model-detail' на фактическое имя URL-маршрута
    #     data = {'name': 'Updated'}
    #     response = self.client.put(url, data, format='json')
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(YourModel.objects.get().name, 'Updated')
    #
    # def test_delete_object(self):
    #     your_model = YourModel.objects.create(name='Test')
    #     url = reverse('your_model-detail',
    #                   args=[your_model.id])  # Замените 'your_model-detail' на фактическое имя URL-маршрута
    #     response = self.client.delete(url)
    #
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertEqual(YourModel.objects.count(), 0)
