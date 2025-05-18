import hashlib

from dadata import Dadata

from orders.models import ShoppingCart
from promotions.models import Bonuses
from users.models import User
from wishlist.models import Wishlist


def check_adress(text):
    token = "7b8466ea8df30fc6a906c7e351e1da4160766933"
    secret = "962187b66460ed2f92c257b7bb2778d2c293cefb"
    dadata = Dadata(token)
    result = dadata.suggest("address", text)
    if len(result) > 0:
        return result[0]
    return None



def hash_string(input_string):
    # Создаем объект хэша
    sha256_hash = hashlib.sha256()

    # Обновляем хэш с входными данными в виде байтов
    sha256_hash.update(input_string.encode('utf-8'))

    # Получаем хэш-значение в виде шестнадцатеричной строки
    hashed_string = sha256_hash.hexdigest()

    return hashed_string

def secret_password(email):
    secret_key = "fsdhjk348290fjdsklfdsfj&*(esdfnklm fjvвыаw" + email
    return hash_string(secret_key)




def register_user(data):

    new_user = User(username=data['username'], password=data['password'], first_name=data['first_name'],
                    last_name=data['last_name'],
                    is_mailing_list=data['is_mailing_list'], email=data['username'])
    genders = {'male': 1, "female": 2}
    if 'gender' in data:
        new_user.gender_id = genders[data['gender']]
    if 'phone' in data:
        new_user.phone_number = data['phone']

    new_user.set_password(data['password'])
    new_user.save()

    # Создайте корзину покупок, связанную с пользователем
    cart = ShoppingCart(user=new_user)
    cart.save()

    # Создайте список желаний, связанный с пользователем
    wl = Wishlist(user=new_user)
    wl.save()

    # Создайте и сохраните бонусы
    bonus = Bonuses()
    bonus.save()

    # Присвойте бонусы пользователю и сохраните его снова
    new_user.bonuses = bonus
    new_user.save()



# check_adress("белгород губкина 17б")

