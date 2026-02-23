import hashlib

from dadata import Dadata
from django.core.exceptions import ObjectDoesNotExist

from orders.models import ShoppingCart
from promotions.models import Bonuses, PromoCode
from users.models import User, EmailConfirmation, UserStatus
from wishlist.models import Wishlist
from django.core import signing



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
    print(data)

    new_user = User(username=data['username'].strip().lower(), password=data['password'], first_name=data['first_name'],
                    last_name=data['last_name'],
                    is_mailing_list=data['is_mailing_list'], email=data['username'].strip().lower())

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

    try:
        if "referral_id" in data:
            referral_promo = PromoCode.objects.get(string_representation=data['referral_id'].upper())

            ref_user = referral_promo.owner
            # new_user.ref_user = ref_user
            if PromoCode.objects.filter(owner=ref_user, ref_promo=True).exists():
                promo = PromoCode.objects.filter(owner=ref_user, ref_promo=True).first()
                cart.promo_code = promo
                cart.save()

    except ObjectDoesNotExist:
        # Обработка исключения, когда пользователя не существует
        print("Что то не найдено")

    except ValueError:
        # Обработка исключения, когда значение не может быть преобразовано в целое число
        print("Некорректное значение referral_id")

    except Exception as e:
        # Обработка других исключений
        print(f"Произошло исключение: {e}")

    # Создайте список желаний, связанный с пользователем
    wl = Wishlist(user=new_user)
    wl.save()

    # Создайте и сохраните бонусы
    bonus = Bonuses()
    bonus.save()

    # Присвойте бонусы пользователю и сохраните его снова
    new_user.bonuses = bonus
    new_user.user_status = UserStatus.objects.get(name='Amethyst')
    promo_string = data['username'].split("@")[0].upper()
    if PromoCode.objects.filter(string_representation=promo_string).exists():
        promo_string += str(new_user.id)
    promo = PromoCode(string_representation=promo_string, ref_promo=True, unlimited=True, owner=new_user)
    promo.save()
    new_user.referral_promo = promo

    def default_referral_data(promo):
        return {
            "order_amounts": [2500, 15000, 25000, 35000, 70000, 90000],
            "partner_bonus_amounts": [250, 500, 750, 1000, 1250, 1500],
            "client_sale_amounts": [0, 0, 0, 0, 0, 0],
            "client_bonus_amounts": [1000, 1000, 1000, 1000, 1000, 1000],
            "promo_text": None,
            "promo_link": f"https://sellout.su?referral_id={promo}",
        }

    new_user.referral_data = default_referral_data(promo_string)
    new_user.save()

    email_confirmation = EmailConfirmation(user=new_user)
    email_confirmation.token = signing.dumps(new_user.email)
    email_confirmation.save()
    # print(f"http://127.0.0.1:8000/api/v1/user")

# check_adress("белгород губкина 17б")
