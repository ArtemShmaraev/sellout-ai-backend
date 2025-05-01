<a name="up"></a>

# SellOut API

Небольшое пояснение: первые квадратные скобки перед запросом это тип запроса, вторые это уровень доступа (Admin > User >
Anon)

### Запрос на сервер `http://сервер:порт/api/v1/...`

## User API

1. `[GET][Admin] user` информация обо всех пользователях, списком [⬇️](#users)
2. `[GET][Admin] user/<user_id>` данные пользователя [⬇️](#user_id)
3. `[GET][User] user_info/<user_id>` данные пользователя [⬇️](#user_id)
4. `[POST][User] user_info/<user_id>` редактирование данных пользователя [⬇️](#edit_user_id)
5. `[POST][Anon] user/register` регистрация пользователя [⬇️](#reg)
6. `[POST][Anon] user/login` вход в систему [⬇️](#log)
7. `[POST][User] user/token/refresh/` рефреш токена [⬇️](#refresh)
8. `[POST][User] user/token/verify/` валиден ли токен (передать access токен {"token": "тут access токен")
статус ответа 200 если токен валиден, иначе 401
-
9. `[GET][User] user/address/<user_id>` адреса пользователя [⬇️](#address)
10. `[POST][User] user/address/<user_id>` добавление адреса пользователя [⬇️](#add_address)
11. `[PUT][User] user/address/<user_id>/<address_id>` редактирование адреса пользователя [⬇️](#edit_address)
12. `[DELETE][User] user/address/<user_id>/<address_id>`удаление адреса пользователя [⬇️](#del_address)
13. `[POST][Anon] https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address` Header: ```Authorization: Token 7b8466ea8df30fc6a906c7e351e1da4160766933``` Body: ```{ "query": "москва хабар" }``` Response: Список словарей, нужная подсказка  dict["value"]
-
13. `[GET][User] user/last_seen/<user_id>` последние 7 просмотренных товаров пользователя [⬇️](#last)
14. `[POST][User] user/last_seen/<user_id>` добавление товара в просмотренные [⬇️](#add_last)
15. `[GET][User] user/favorite_brand/<user_id>/<brand_id>` добавить любимый бренд, чтобы удалить метод Delete
16. `[GET][User] user/size_info` Response: ```{"preferred_shoes_size_row": 1, "preferred_clothes_size_row": 43, "shoes_size": 8, "clothes_size": 55, "height": 175, "weight": 60 }```
17. `[POST][User] user/size_info` Body: Верхний Response
18. `[GET][User] user/get_size_table` Вернет две таблица для отображения в ЛК

## Product API

1. `[GET][Anon] product/products/<product_id>` данные одного товара [⬇️](#product_id)
2. `[GET][Anon] product/slug/<slug>` данные товара по slug [⬇️](#product_slug)
3. `[GET][Anon] product/products/&page=n` страница товаров [⬇️](#product_all)
4. `[PUT][Anon] product/update/<product_id>` редактирование товара [⬇️](#product_update)
5. `[DELETE][Anon] product/update/<product_id>` удаление товара по id
6. `[POST][Anon] product/list_product` карточки товаров по массиву {"products": [1, 2]}
7. `[GET][Anon] product/size_table`таблица размеров для фильтра [⬇️](#product_size_table)

## Category, Line, Color, Brand API
у каждой сущности есть все виды запросов [GET]
1. `[GET][Anon] product/[categories|lines|colors|brands|collections]` вернет все сущности [⬇️](#clcb)
2. `[GET][Anon] product/cat_no_child` список всех категорий для админки
3. `[GET][Anon] product/line_no_child` список всех линеек для админки


## Shipping API

1. `[GET][Anon] product_unit/product/<product_id>` все product_unit для данного товара [⬇️](#product_unit)
2. `[GET][Anon] product_unit/product/<slug>` все product_unit для данного товара [⬇️](#product_unit)
3. `[GET][Anon] product_unit/product_main/<product_id>/<user_id>` "карточка товара" [⬇️](#product_main)
4. `[GET][Anon] /product` фильтрация товаров [⬇️](#product_filter)
5. `[GET][Anon] product_unit/<product_unit_id>` информация о product_unit
6. `[POST][Anon] product_unit/list` Body: ```{"product_unit_list": [2, 3]}``` Response Список product_unit
7. `[POST][Anon] product_unit/total_amount_list` Body: ```{"product_unit_list": [2, 3]}``` Response: Сумма

5. `[GET][Anon] product_unit/min_price/<product_id>` Вернет цены для отображения по каждому размеру [⬇️](#product_min_price)
6. `[GET][Anon] product_unit/delivery/<product_id>/<size_id>` Вернет способы доставки для определенной цены [⬇️](#product_delivery)

## WishList API

1. `[GET][User] wishlist/<user_id>` вишлист пользователя [⬇️](#wl)
2. `[POST][User] wishlist/<user_id>/<product_id>` добавление в вишлист [⬇️](#add_wl)
3. `[DELETE][User] wishlist/<user_id>/<wishlist_unit_id>` Удаление из вишлиста [⬇️](#del_wl)
4. `[POST][User] wishlist/change_size/<user_id>/<wishlist_unit_id>/<size_id>` поменять размер в
   вишлисте [⬇️](#change_wl)

## Orders API

1. `[GET][User] order/cart/<user_id>` корзина пользователя [⬇️](#cart)
2. `[POST][User]  order/cart/<user_id>/<product_unit_id>` добавить юнит в корзину [⬇️](#add_to_cart)
3. `[DELETE][User] order/cart/<user_id>/<product_unit_id>` удалить юнит из
   корзины [⬇️](#del_from_cart)
4. `[POST][User] order/checkout/<user_id>` оформить заказ [⬇️](#checkout)
5. `[GET][Admin] order/orders` все заказы [⬇️](#orderss)
6. `[GET][User] order/user_orders/<user_id>` все заказы пользователя [⬇️](#user_orders)
7. `[GET][User] order/<order_id>` информация о заказе [⬇️](#order)
   <a name="user"></a>
8. `[POST]User order/cart_list/<user_id>` Body: ```{"product_unit_list": [2, 3]}``` Response (добавление в корзину или исключение)
9. `[POST][User] promo/check/<user_id>` Body: ```{"promo": "penis"}``` Response  ```{"final_amount": 49490, "message": "Промокод применен", "status": true }```
10. `[POST][Anon] promo/check/` Body: ```{"promo": "penis", "product_unit_list": [2, 3]}``` Response: ```{"final_amount": 115484, "message": "Промокод применен", "status": true, "promo_sale": 100}```


## Dewu Info Для Дениса
1. `[GET] product/dewu_info` Вернуть всё (web_data=false вернёт товары у которых web_data пустая)
2. `[GET] product/dewu_info/<spu_id>` Венуть по Spu Id
3. `[POST] product/dewu_info/<spu_id>` Body: ```{"api_data": api_data, "web_data": web_data, "preprocessed_data": data}``` Можно передать не все параметры для заполнения
# Поиск
Запросы отправляются на сервер с elastic 
### 1. `[GET][Anon] <elastichost>/sellout/_search` поискв

Body:
```json
{
  "query": {
    "multi_match": {
       "query": "Тут запрос например <Nike>",
       "fields": ["name", "brands.name", "categories.name", "tags.name", "description"],
       "fuzziness": 2
    }
  }
}
```

Response:
```json
{
   "took": 9,
   "timed_out": false,
   "_shards": {
      "total": 1,
      "successful": 1,
      "failed": 0
   },
   "hits": {
      "total": 2,
      "max_score": 1.0,
      "hits": [
         {
            "_index": "sellout",
            "_type": "doc",
            "_id": "1",
            "_score": 1.0,
            "_source": {
               "name": "Air Force 1",
               "description": "desc",
               "brands": [
                  {
                     "id": 1,
                     "name": "Nike"
                  }
               ],
               "categories": [
                  {
                     "id": 1,
                     "name": "Sport"
                  }
               ],
               "tags": [
                  {
                     "id": 1,
                     "name": "Style"
                  }
               ],
               "id": 1
            }
         }
      ]
   }
}

```




## User API

[:arrow_up:SellOut API](#up)
<a name="users"></a>

### 1. `[GET][Admin] user` информация обо всех пользователях, списком

Response:

```json
[
  {
    "id": 2,
    "last_login": "2023-04-12T10:07:07Z",
    "is_superuser": false,
    "username": "noadmin",
    "first_name": "no",
    "last_name": "admin",
    "email": "noadmin@mail.ru",
    "is_staff": false,
    "is_active": true,
    "date_joined": "2023-04-12T10:07:34Z",
    "all_purchase_amount": 0,
    "personal_discount_percentage": 0,
    "referral_link": null,
    "preferred_size_grid": null,
    "gender": null,
    "ref_user": null,
    "groups": [],
    "user_permissions": [],
    "my_groups": [],
    "address": [],
    "last_viewed_products": [
      {
        "id": 1,
        "name": "Air Force 1",
        "bucket_link": "/buck",
        "description": "desc",
        "sku": "air_force_1",
        "available_flag": true,
        "last_upd": "2023-04-07T15:28:17Z",
        "add_date": "2023-04-07",
        "fit": 1,
        "rel_num": 1,
        "gender": 1,
        "brands": [
          1
        ],
        "categories": [
          1
        ],
        "tags": [
          1
        ]
      }
    ]
  }
]
```

[:arrow_up:User API](#user)
[:arrow_up:SellOut API](#up)
<a name="user_id"></a>

### 2 - 3. `[GET][Admin] user/<user_id> и [GET][Anon] user/user_info/<user_id>` данные пользователя

Response:

```json
{
  "id": 2,
  "last_login": "2023-04-12T10:07:07Z",
  "is_superuser": false,
  "username": "noadmin",
  "first_name": "no",
  "last_name": "admin",
  "email": "noadmin@mail.ru",
  "is_staff": false,
  "is_active": true,
  "date_joined": "2023-04-12T10:07:34Z",
  "all_purchase_amount": 0,
  "personal_discount_percentage": 0,
  "referral_link": null,
  "preferred_size_grid": null,
  "gender": null,
  "ref_user": null,
  "groups": [],
  "user_permissions": [],
  "my_groups": [],
  "address": [],
  "last_viewed_products": [
    {
      "id": 1,
      "name": "Air Force 1",
      "bucket_link": "/buck",
      "description": "desc",
      "sku": "air_force_1",
      "available_flag": true,
      "last_upd": "2023-04-07T15:28:17Z",
      "add_date": "2023-04-07",
      "fit": 1,
      "rel_num": 1,
      "gender": 1,
      "brands": [
        1
      ],
      "categories": [
        1
      ],
      "tags": [
        1
      ]
    },
    {
      "id": 2,
      "name": "Dunk",
      "bucket_link": "/buck",
      "description": "desc",
      "sku": "sku",
      "available_flag": true,
      "last_upd": "2023-04-07T15:59:39Z",
      "add_date": "2023-04-07",
      "fit": 0,
      "rel_num": 0,
      "gender": 1,
      "brands": [
        1
      ],
      "categories": [
        1
      ],
      "tags": [
        1
      ]
    }
  ]
}
```

[:arrow_up:User API](#user)
[:arrow_up:SellOut API](#up)
<a name="edit_user_id"></a>
### 5 `[POST][User] user/user_info/<user_id>` Изменить данные пользователя
Body: передать измененные параметры
```json
{
  "username": "new_username",
  "first_name": "new_first_name",
  "last_name": "new_last_name",
  "email": "new_email@example.com"
}
```
Response: Данные пользователя

<a name="reg"></a>

### 6. `[POST][Anon] user/register` регистрация пользователя

Body:

```json
{
  "username": "mail@mail.ru",
  "password": "пароль",
  "first_name": "Имя",
  "last_name": "Фамилия",
  "gender": "male",
  "phone": "79524363887"
}

```

Response:

```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4Nzc5MjIzNSwiaWF0IjoxNjg3MTg3NDM1LCJqdGkiOiI3MWFkMWVmMzk1OTk0YjM0YjhjMjc3ZWJlYTk0NmYyOCIsInVzZXJfaWQiOjIsInVzZXJuYW1lIjoiYXJ0ZWRkbUBtYWlsLnJ1IiwiZmlyc3RfbmFtZSI6InNkIiwibGFzdF9uYW1lIjoiZHNmIn0.YsRislGTVld_1c0dgT8OTVGXX7n21DVa2h4gaqDiLWA",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg3MTg3NTU1LCJpYXQiOjE2ODcxODc0MzUsImp0aSI6ImZkZjg3YzI1NDUwYTRlYmU4OGI3MzA2NWMyNjNmNmUzIiwidXNlcl9pZCI6MiwidXNlcm5hbWUiOiJhcnRlZGRtQG1haWwucnUiLCJmaXJzdF9uYW1lIjoic2QiLCJsYXN0X25hbWUiOiJkc2YifQ.3MMCus1wbBr5OO-rZvGkMOCRI5ieoScoLqeBIv_aIco",
    "username": "arteddm@mail.ru",
    "first_name": "artem",
    "last_name": "sh"
}
```

[:arrow_up:User API](#user)
[:arrow_up:SellOut API](#up)
<a name="log"></a>

### 7. `[POST][Anon] user/login` вход в систему

Body:

```json
{
  "username": "mail@mail.ru",
  "password": "пароль"
}
```

Response:

```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4Nzc5MjIzNSwiaWF0IjoxNjg3MTg3NDM1LCJqdGkiOiI3MWFkMWVmMzk1OTk0YjM0YjhjMjc3ZWJlYTk0NmYyOCIsInVzZXJfaWQiOjIsInVzZXJuYW1lIjoiYXJ0ZWRkbUBtYWlsLnJ1IiwiZmlyc3RfbmFtZSI6InNkIiwibGFzdF9uYW1lIjoiZHNmIn0.YsRislGTVld_1c0dgT8OTVGXX7n21DVa2h4gaqDiLWA",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg3MTg3NTU1LCJpYXQiOjE2ODcxODc0MzUsImp0aSI6ImZkZjg3YzI1NDUwYTRlYmU4OGI3MzA2NWMyNjNmNmUzIiwidXNlcl9pZCI6MiwidXNlcm5hbWUiOiJhcnRlZGRtQG1haWwucnUiLCJmaXJzdF9uYW1lIjoic2QiLCJsYXN0X25hbWUiOiJkc2YifQ.3MMCus1wbBr5OO-rZvGkMOCRI5ieoScoLqeBIv_aIco",
    "username": "arteddm@mail.ru",
    "first_name": "sd",
    "last_name": "dsf"
}
```

[:arrow_up:User API](#user)
[:arrow_up:SellOut API](#up)

<a name="refresh"></a>
### 8. `[POST][User] user/token/refresh/` обновление токена
Body:
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4NzcxMzc4NywiaWF0IjoxNjg3MTA4OTg3LCJqdGkiOiJhNzBiN2YxMDg5OTI0ZTMyYmM2YmRiZWU4YWQ2YzY1ZiIsInVzZXJfaWQiOjF9.zyIWDnxf3qU9P5A-JXcTI_XXDJP41hu12VvofqTwJRA",
}
```
Response:
````json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg3MTk1NDg0LCJpYXQiOjE2ODcxMDg5ODcsImp0aSI6IjkzNTEyMzFiNjA4MjRjZWJhOWY3ZDExNDc1OGE4YjYxIiwidXNlcl9pZCI6MX0.RmAOgVudnrfclAapeLEpQSK7Ji-93ECBnCJnz2TzvEQ"
}
````


[:arrow_up:User API](#user)
[:arrow_up:SellOut API](#up)


<a name="address"></a>

### 9. `[GET][User] user/address/<user_id>` адреса пользователя

Response:

```json
[
  {
    "id": 1,
    "name": "name",
    "address": "Проспект Мира 111",
    "post_index": "308033",
     "is_main": true
  }
]
```

[:arrow_up:User API](#user)
[:arrow_up:SellOut API](#up)

<a name="add_address"></a>

### 10. `[POST][User] user/address/<user_id>` добавление адреса пользователя
Body:
```json
{
  "name": "name",
  "address": "Проспект Мира 111",
  "post_index": "308033", 
   "is_main": true
}

```
Response:

```json
  {
    "id": 1,
    "name": "name",
    "address": "Проспект Мира 111",
    "post_index": "308033",
   "is_main": true
  }
```

[:arrow_up:User API](#user)
[:arrow_up:SellOut API](#up)


<a name="edit_address"></a>

### 11. `[PUT][User] user/address/<user_id>/<address_id>` редактирование адреса пользователя
Body:
```json
{
  "name": "name",
  "address": "Проспект Мира 111",
  "post_index": "308033",
   "is_main": true
}

```
Response:

```json
  {
    "id": 1,
    "name": "name",
    "address": "Проспект Мира 111",
    "post_index": "308033",
   "is_main": true
  }
```

[:arrow_up:User API](#user)
[:arrow_up:SellOut API](#up)


<a name="del_address"></a>

### 12. `[DELETE][User] user/address/<user_id>/<address_id>` удаление адреса пользователя
Response("Адрес успешно удален")

[:arrow_up:User API](#user)
[:arrow_up:SellOut API](#up)


<a name="last"></a>

### 13. `[GET][User] user/last_seen/<user_id>` последние 7 просмотренных товаров пользователя

Response:

```json
[
  {
    "id": 1,
    "name": "Air Force 1",
    "bucket_link": "/buck",
    "description": "desc",
    "sku": "air_force_1",
    "available_flag": true,
    "last_upd": "2023-04-07T15:28:17Z",
    "add_date": "2023-04-07",
    "fit": 1,
    "rel_num": 1,
    "gender": {
      "id": 1,
      "name": "M"
    },
    "brands": [
      {
        "id": 1,
        "name": "Nike"
      }
    ],
    "categories": [
      {
        "id": 1,
        "name": "Sport"
      }
    ],
    "tags": [
      {
        "id": 1,
        "name": "Style"
      }
    ],
    "min_price": 7,
    "in_wishlist": true
  },
  {
    "id": 2,
    "name": "Dunk",
    "bucket_link": "/buck",
    "description": "desc",
    "sku": "sku",
    "available_flag": true,
    "last_upd": "2023-04-07T15:59:39Z",
    "add_date": "2023-04-07",
    "fit": 0,
    "rel_num": 0,
    "gender": {
      "id": 1,
      "name": "M"
    },
    "brands": [
      {
        "id": 1,
        "name": "Nike"
      }
    ],
    "categories": [
      {
        "id": 1,
        "name": "Sport"
      }
    ],
    "tags": [
      {
        "id": 1,
        "name": "Style"
      }
    ],
    "min_price": 100,
    "in_wishlist": false
  }
]
```

[:arrow_up:User API](#user)
[:arrow_up:SellOut API](#up)

<a name="add_last"></a>
### 14. `[POST][User] user/last_seen/<user_id>` Добавление товара в просмотренные
Body:
```json
{
   "product_id": id
}
```
Response("Продукт успешно добавлен в список последних просмотров")
Статус ответа 200 иначе ошибка

[:arrow_up:User API](#user)
[:arrow_up:SellOut API](#up)

<a name="product"></a>

## Product APi
[:arrow_up:SellOut API](#up)


<a name="product_id"></a>

### 1. `[GET][Anon] product/<product_id>` данные одного товара

Response:

```json
{
    "id": 516,
    "in_wishlist": false,
    "min_price_product_unit": 83490,
    "main_line": "Nike | Air Force 1 | Low",
    "model": "Louis Vuitton Air Force 1 Low",
    "colorway": "Virgil Abloh - BLACK/BLACK",
    "russian_name": "Louis Vuitton Air Force 1 Low",
    "slug": "nike-louis-vuitton-louis-vuitton-air-force-1-low-virgil-abloh-blackblack-516",
    "manufacturer_sku": "1A9VD6",
    "description": "",
    "bucket_link": "",
    "designer_color": "",
    "min_price": 83490,
    "available_flag": true,
    "last_upd": "2023-06-16T11:41:11.705314Z",
    "add_date": "2023-06-16",
    "release_date": "2023-06-16",
    "fit": 0,
    "rel_num": 0,
    "main_color": {
        "id": 5,
        "name": "black",
        "is_main_color": true,
        "russian_name": "Р§РµСЂРЅС‹Р№",
        "hex": "#000000"
    },
    "recommended_gender": {
        "id": 1,
        "name": "M"
    },
    "size_table": null,
    "brands": [
        {
            "id": 8,
            "name": "Nike"
        },
        {
            "id": 23,
            "name": "Louis Vuitton"
        }
    ],
    "categories": [
        {
            "id": 1,
            "name": "Обувь",
            "eng_name": "shoes_category",
            "full_name": "Обувь",
            "parent_category": null
        }
    ],
    "lines": [
        {
            "id": 3,
            "name": "Nike",
            "full_name": "Nike",
            "full_eng_name": "nike",
            "parent_line": null,
            "brand": {
                "id": 8,
                "name": "Nike"
            }
        },
        {
            "id": 5,
            "name": "Все Nike",
            "full_name": "Nike | Все Nike",
            "full_eng_name": "nike",
            "parent_line": {
                "id": 3,
                "name": "Nike",
                "full_name": "Nike",
                "full_eng_name": "nike",
                "parent_line": null,
                "brand": 8
            },
            "brand": {
                "id": 8,
                "name": "Nike"
            }
        },
        {
            "id": 18,
            "name": "Air Force 1",
            "full_name": "Nike | Air Force 1",
            "full_eng_name": "nike_air_force_1",
            "parent_line": {
                "id": 3,
                "name": "Nike",
                "full_name": "Nike",
                "full_eng_name": "nike",
                "parent_line": null,
                "brand": 8
            },
            "brand": {
                "id": 8,
                "name": "Nike"
            }
        },
        {
            "id": 19,
            "name": "Low",
            "full_name": "Nike | Air Force 1 | Low",
            "full_eng_name": "nike_air_force_1_low",
            "parent_line": {
                "id": 18,
                "name": "Air Force 1",
                "full_name": "Nike | Air Force 1",
                "full_eng_name": "nike_air_force_1",
                "parent_line": 3,
                "brand": 8
            },
            "brand": {
                "id": 8,
                "name": "Nike"
            }
        },
        {
            "id": 20,
            "name": "Все Air Force 1",
            "full_name": "Nike | Air Force 1 | Все Air Force 1",
            "full_eng_name": "nike_air_force_1",
            "parent_line": {
                "id": 18,
                "name": "Air Force 1",
                "full_name": "Nike | Air Force 1",
                "full_eng_name": "nike_air_force_1",
                "parent_line": 3,
                "brand": 8
            },
            "brand": {
                "id": 8,
                "name": "Nike"
            }
        }
    ],
    "collections": [
        {
            "id": 3,
            "name": "Nike x Louis Vuitton"
        }
    ],
    "tags": [],
    "colors": [
        {
            "id": 531,
            "name": "noir",
            "is_main_color": false,
            "russian_name": "",
            "hex": ""
        }
    ],
    "gender": [
        {
            "id": 1,
            "name": "M"
        },
        {
            "id": 2,
            "name": "F"
        }
    ]
}
```

[:arrow_up:Product API](#product)
[:arrow_up:SellOut API](#up)

<a name="product_slug"></a>

### 2. `[GET][Anon] product/slug/<slug>` данные одного товара по slug

Response:

```json
{
    "id": 712,
    "is_favorite": false,
    "model": "Flight Legacy",
    "colorway": "Lakers",
    "russian_name": "Flight Legacy",
    "slug": "nike-flight-legacy-lakers-712",
    "manufacturer_sku": "BQ4212102",
    "description": "",
    "bucket_link": "",
    "designer_color": "",
    "min_price": null,
    "available_flag": true,
    "last_upd": "2023-06-07T13:35:34.003607Z",
    "add_date": "2023-06-07",
    "release_date": "2023-06-07",
    "fit": 0,
    "rel_num": 0,
    "main_color": {
        "id": 7,
        "name": "white"
    },
    "recommended_gender": {
        "id": 1,
        "name": "M"
    },
    "size_table": null,
    "brands": [
        {
            "id": 8,
            "name": "Nike"
        }
    ],
    "categories": [
        {
            "id": 1,
            "name": "Обувь",
            "parent_category": null
        }
    ],
    "lines": [],
    "collections": [],
    "tags": [],
    "colors": [
        {
            "id": 91,
            "name": "102 white"
        },
        {
            "id": 718,
            "name": "regency purple"
        }
    ],
    "gender": [
        {
            "id": 1,
            "name": "M"
        },
        {
            "id": 2,
            "name": "F"
        }
    ]
}
```
[:arrow_up:Product API](#product)
[:arrow_up:SellOut API](#up)

<a name="product_all"></a>

### 3. `[GET][Anon] product/&page=n` страница товаров

Response:

```json
{
    "count": 16400,
    "next": "http://127.0.0.1:8000/api/v1/product/?page=2",
    "previous": null,
    "results": [
        {
            "id": 722,
            "is_favorite": false,
            "model": "0 To 60 STMT Human Race",
            "colorway": "Triple Black",
            "russian_name": "0 To 60 STMT Human Race",
            "slug": "adidas-0-to-60-stmt-human-race-triple-black-722",
            "manufacturer_sku": "GX2486",
            "description": "",
            "bucket_link": "",
            "designer_color": "",
            "min_price": null,
            "available_flag": true,
            "last_upd": "2023-05-29T14:37:02.605662Z",
            "add_date": "2023-05-29",
            "release_date": "2023-05-29",
            "fit": 0,
            "rel_num": 0,
            "main_color": {
                "id": 5,
                "name": "black"
            },
            "recommended_gender": {
                "id": 1,
                "name": "M"
            },
            "size_table": null,
            "brands": [
                {
                    "id": 1,
                    "name": "Adidas"
                }
            ],
            "categories": [
                {
                    "id": 1,
                    "name": "Обувь",
                    "parent_category": null
                }
            ],
            "lines": [],
            "collections": [],
            "tags": [],
            "colors": [
                {
                    "id": 5,
                    "name": "black"
                },
                {
                    "id": 103,
                    "name": "black-black"
                }
            ],
            "gender": [
                {
                    "id": 1,
                    "name": "M"
                },
                {
                    "id": 2,
                    "name": "F"
                }
            ]
        },
       ...
    ]
}
```

[:arrow_up:Product API](#product)
[:arrow_up:SellOut API](#up)
<a name="product_update"></a>

4. `[PUT] product/update/<product_id>` редактироване товара
можно передавать
```json
{
    "categories": ["список id категорий"],
    "lines": ["список id линеек"],
    "brands": ["список id брендов"],
    "model": "название",
    "colorway": "название",
    "russian_name": "название",
    "description": "описание",
    "main_color": "id нового main_color",
}
```
Все параметры необязательные, можно предавать только те, которые меняются

Запрос http://127.0.0.1:8000/api/v1/product/update/2


Body
```json
{
    "model": "название",
    "colorway": "название",
    "russian_name": "название",
    "description": "описание",
    "main_color": 5
}
```
Response
```json
{
    "id": 2,
    "in_wishlist": false,
    "min_price_product_unit": 91990,
    "main_line": "Nike",
    "model": "название",
    "colorway": "название",
    "russian_name": "название",
    "slug": "nike-2",
    "manufacturer_sku": "CZ8100600",
    "description": "описание",
    "bucket_link": "",
    "designer_color": "",
    "min_price": 91990,
    "available_flag": true,
    "last_upd": "2023-06-17T09:51:38.737920Z",
    "add_date": "2023-06-17",
    "release_date": "2023-06-17",
    "fit": 0,
    "rel_num": 0,
    "main_color": {
        "id": 5,
        "name": "orange",
        "is_main_color": true,
        "russian_name": "РћСЂР°РЅР¶РµРІС‹Р№",
        "hex": "#ff9e39"
    },
    "recommended_gender": {
        "id": 1,
        "name": "M"
    },
    "size_table": null,
    "brands": [
        {
            "id": 8,
            "name": "Nike"
        }
    ],
    "categories": [
        {
            "id": 1,
            "name": "Обувь",
            "eng_name": "shoes_category",
            "full_name": "Обувь",
            "parent_category": null
        }
    ],
    "lines": [
        {
            "id": 2,
            "name": "Nike",
            "is_all": false,
            "view_name": "Nike",
            "full_name": "Nike",
            "full_eng_name": "nike",
            "parent_line": null,
            "brand": {
                "id": 8,
                "name": "Nike"
            }
        }
    ],
    "collections": [],
    "tags": [],
    "colors": [
        {
            "id": 3,
            "name": "600 bright crimson",
            "is_main_color": false,
            "russian_name": "",
            "hex": ""
        },
        {
            "id": 4,
            "name": "obsidian",
            "is_main_color": false,
            "russian_name": "",
            "hex": ""
        }
    ],
    "gender": [
        {
            "id": 1,
            "name": "M"
        },
        {
            "id": 2,
            "name": "F"
        }
    ]
}
```
[:arrow_up:Product API](#product)
[:arrow_up:SellOut API](#up)

<a name="clcb"></a>
## Категории, Линейки, Цвета, Бренды
### Категории
`[GET][Anon] product/categories`
Response Категория
```json
[
    {
        "id": 1,
        "name": "Обувь",
        "parent_category":null
    },
    {
        "id": 2,
        "name": "Вся обувь",
        "parent_category": 1
    }
]
```
### также есть запрос для отображения "красивого дерева" категорий
`[GET][Anon] product/tree_cat`
```json
[
   {
      "id": 1,
      "name": "Обувь",
      "parent_category": null,
      "subcategories": [
         {
            "id": 2,
            "name": "Вся обувь",
            "parent_category": 1
         },
         {
            "id": 3,
            "name": "Кроссовки",
            "parent_category": 1,
            "subcategories": [
               {
                  "id": 4,
                  "name": "Все кроссовки",
                  "parent_category": 3
               }
            ]
         }
      ]
   }
]

```

### Линейки
`[GET][Anon] product/lines`
Response:
```json
[
    {
        "id": 1,
        "name": "Jordan",
        "parent_line": null,
        "brand": {
            "id": 5,
            "name": "Jordan"
        }
    },
    {
        "id": 2,
        "name": "Другие Jordan",
        "parent_line": {
            "id": 1,
            "name": "Jordan",
            "parent_line": null,
            "brand": 5
        },
        "brand": {
            "id": 5,
            "name": "Jordan"
        }
    }
]
```
### Есть дерево ленеек
`[GET][Anon] product/tree_line`
Response:
```json
[
    {
        "id": 1,
        "name": "Jordan",
        "parent_line": null,
        "brand": {
            "id": 5,
            "name": "Jordan"
        },
        "children": [
            {
                "id": 2,
                "name": "Другие Jordan",
                "parent_line": {
                    "id": 1,
                    "name": "Jordan",
                    "parent_line": null,
                    "brand": 5
                },
                "brand": {
                    "id": 5,
                    "name": "Jordan"
                }
            }
        ]
    },
    {
        "id": 3,
        "name": "New Balance",
        "parent_line": null,
        "brand": {
            "id": 7,
            "name": "New Balance"
        },
        "children": [
            {
                "id": 4,
                "name": "1906R",
                "parent_line": {
                    "id": 3,
                    "name": "New Balance",
                    "parent_line": null,
                    "brand": 7
                },
                "brand": {
                    "id": 7,
                    "name": "New Balance"
                }
            },
            {
                "id": 5,
                "name": "2002R",
                "parent_line": {
                    "id": 3,
                    "name": "New Balance",
                    "parent_line": null,
                    "brand": 7
                },
                "brand": {
                    "id": 7,
                    "name": "New Balance"
                }
            }
        ]
    }
]
```

### Бренды
`[GET][Anon] product/brands`
Response:
```json
[
    {
        "id": 1,
        "name": "Adidas"
    },
    {
        "id": 2,
        "name": "Asics"
    },
    {
        "id": 3,
        "name": "Converse"
    },
    {
        "id": 4,
        "name": "Fila"
    },
    {
        "id": 5,
        "name": "Jordan"
    },
    {
        "id": 6,
        "name": "Karhu"
    },
    {
        "id": 7,
        "name": "New Balance"
    }
]
```

### Цвета
`[GET][Anon] product/colors` 
Response:
```json
[
    {
        "id": 1,
        "name": "black",
        "is_main_color": true
    },
    {
        "id": 5,
        "name": "orange",
        "is_main_color": true
    },
    {
        "id": 8,
        "name": "blue",
        "is_main_color": true
    },
    {
        "id": 10,
        "name": "grey",
        "is_main_color": true
    },
    {
        "id": 13,
        "name": "neutrals",
        "is_main_color": true
    },
    {
        "id": 18,
        "name": "white",
        "is_main_color": true
    }
]
```
[:arrow_up:Product API](#product)
[:arrow_up:SellOut API](#up)


<a name="product_size_table"></a>
### `[GET][Anon] product/size_table`таблица размеров для фильтра 
Можно передать параметры в строке запроса `product/size_table?gender=F&category=shoes_category `
gender и category
по умолчанию отображать "is_user_main": true, ту у которой 
Response:
```json
[
   {
      "id": 3,
      "size_rows": [
         {
            "id": 19,
            "is_main": false,
            "filter_name": "Итальянский(IT)",
            "filter_logo": "-",
            "sizes": [
               {
                  "size": "XXS",
                  "query": [
                     212,
                     213
                  ]
               },
               {
                  "size": "XS",
                  "query": [
                     214,
                     215
                  ]
               },
               {
                  "size": "S",
                  "query": [
                     216,
                     217
                  ]
               }
            ]
         }
      ],
      "name": "Clothes_Women",
      "filter_name": "Женская одежда",
      "standard": true,
      "category": [
         {
            "id": 21,
            "name": "Одежда",
            "eng_name": "clothes",
            "is_all": false,
            "full_name": "Одежда",
            "parent_category": null
         }
      ],
      "gender": [
         {
            "id": 2,
            "name": "F"
         }
      ]
   }
]
```

[:arrow_up:Product API](#product)
[:arrow_up:SellOut API](#up)


<a name="shipping"></a>

## Shipping API

<a name="product_unit"></a>

### 1. `[GET][Anon] product_unit/product/<product_id>` все product_unit для данного товара

Response:

```json
[
  {
    "id": 1,
    "final_price": 7,
    "availability": true,
    "product": {
      "id": 1,
      "name": "Air Force 1",
      "bucket_link": "/buck",
      "description": "desc",
      "sku": "air_force_1",
      "available_flag": true,
      "last_upd": "2023-04-07T15:28:17Z",
      "add_date": "2023-04-07",
      "fit": 1,
      "rel_num": 1,
      "gender": {
        "id": 1,
        "name": "M"
      },
      "brands": [
        {
          "id": 1,
          "name": "Nike"
        }
      ],
      "categories": [
        {
          "id": 1,
          "name": "Sport"
        }
      ],
      "tags": [
        {
          "id": 1,
          "name": "Style"
        }
      ]
    },
    "size": {
      "id": 1,
      "INT": "12",
      "US": "12",
      "UK": "12",
      "EU": "12",
      "IT": "12",
      "RU": "12",
      "product": {
        "id": 1,
        "name": "Air Force 1",
        "bucket_link": "/buck",
        "description": "desc",
        "sku": "air_force_1",
        "available_flag": true,
        "last_upd": "2023-04-07T15:28:17Z",
        "add_date": "2023-04-07",
        "fit": 1,
        "rel_num": 1,
        "gender": 1,
        "brands": [
          1
        ],
        "categories": [
          1
        ],
        "tags": [
          1
        ]
      }
    },
    "currency": {
      "id": 2,
      "name": "pending"
    },
    "delivery_type": {
      "id": 1,
      "name": "Самолёт"
    },
    "platform": {
      "id": 1,
      "platform": "Poizon",
      "site": "/poizon"
    }
  }
]
```

[:arrow_up:Shipping API](#shipping)
[:arrow_up:SellOut API](#up)
<a name="product_main"></a>

### 2-3. `[GET][Anon] product_unit/product_main/<product_id>/<user_id>` "картока товара" (если пользователь не авторизован user_id = 0)

Response:

```json
{
  "id": 1,
  "name": "Air Force 1",
  "bucket_link": "/buck",
  "description": "desc",
  "sku": "air_force_1",
  "available_flag": true,
  "last_upd": "2023-04-07T15:28:17Z",
  "add_date": "2023-04-07",
  "fit": 1,
  "rel_num": 1,
  "gender": {
    "id": 1,
    "name": "M"
  },
  "brands": [
    {
      "id": 1,
      "name": "Nike"
    }
  ],
  "categories": [
    {
      "id": 1,
      "name": "Sport"
    }
  ],
  "tags": [
    {
      "id": 1,
      "name": "Style"
    }
  ],
  "min_price": 7,
  "in_wishlist": true
}

```

[:arrow_up:Shipping API](#shipping)
[:arrow_up:SellOut API](#up)


<a name="product_filter"></a>
### 3. `[GET][Anon] product` фильтрация товаров
параметры пример: `product/?brands=Nike&gender=F&colors=white&categories=Обувь&brands=Supreme`

    category = Фильтр по категориям (eng_name)
    brand = Фильтр по брендам
    gender = Пол (M, F, K) male, female, kids
    collection = Фильтр по коллекциям, колоборациям (query_name)
    color = Фильтр по цветам (name)
    price_min = Фильтр по цене мин
    price_max = Фильтр по цене макс
    line = Линейки (full_eng_name)
    page = Номер страницы, (на странице 50 товаров)
    ordering = (min_price, -min_price, release_date)

Response:
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1164,
            "is_favorite": false,
            "model": "Air Bakin SP",
            "colorway": "Supreme - Black",
            "russian_name": "Air Bakin SP",
            "slug": "nike-supreme-air-bakin-sp-supreme-black-1164",
            "manufacturer_sku": "DX3292001",
            "description": "",
            "bucket_link": "",
            "designer_color": "",
            "min_price": null,
            "available_flag": true,
            "last_upd": "2023-05-18T15:37:08.902726Z",
            "add_date": "2023-05-18",
            "release_date": "2023-05-18",
            "fit": 0,
            "rel_num": 0,
            "main_color": {
                "id": 2,
                "name": "black"
            },
            "recommended_gender": {
                "id": 1,
                "name": "M"
            },
            "brands": [
                {
                    "id": 8,
                    "name": "Supreme"
                },
                {
                    "id": 3,
                    "name": "Nike"
                }
            ],
            "categories": [
                {
                    "id": 2,
                    "name": "Обувь",
                    "parent_category": null
                }
            ],
            "lines": [],
            "collections": [
                {
                    "id": 1,
                    "name": "Nike x Supreme"
                }
            ],
            "tags": [],
            "colors": [
                {
                    "id": 2,
                    "name": "black"
                },
                {
                    "id": 612,
                    "name": "speed red-multi-color"
                }
            ],
            "gender": [
                {
                    "id": 1,
                    "name": "M"
                },
                {
                    "id": 2,
                    "name": "F"
                }
            ]
        }
    ]
}
```
[:arrow_up:Shipping API](#shipping)
[:arrow_up:SellOut API](#up)


<a name="product_min_price"></a>
### 5. `[GET][Anon] product_unit/min_price/<product_id>` Вернет цены для отображения по каждому размеру 
Response:
```json
[
    {
        "min_price": 79990,
        "size": {
            "id": 87,
            "US": "9.5",
            "UK": "8.5",
            "EU": "43",
            "RU": "42",
            "CM": null,
            "table": 6
        },
        "view_size": "43"
    },
    {
        "min_price": 60490,
        "size": {
            "id": 73,
            "US": "6",
            "UK": "4",
            "EU": "36.5",
            "RU": "35.5",
            "CM": null,
            "table": 5
        },
        "view_size": "36.5"
    },
    {
        "min_price": 44490,
        "size": {
            "id": 76,
            "US": "7.5",
            "UK": "5.5",
            "EU": "38",
            "RU": "37",
            "CM": null,
            "table": 5
        },
        "view_size": "38"
    },
    {
        "min_price": 34490,
        "size": {
            "id": 41,
            "US": "12",
            "UK": "10.5",
            "EU": "45 1/3",
            "RU": "44",
            "CM": null,
            "table": 2
        },
        "view_size": "45 1/3"
    },
    {
        "min_price": 76990,
        "size": {
            "id": 7,
            "US": "6.5",
            "UK": "6",
            "EU": "39 1/3",
            "RU": "38",
            "CM": null,
            "table": 1
        },
        "view_size": "39 1/3"
    },
    {
        "min_price": 36990,
        "size": {
            "id": 57,
            "US": "5",
            "UK": "4",
            "EU": "37",
            "RU": "36",
            "CM": null,
            "table": 4
        },
        "view_size": "37"
    }
]
```

[:arrow_up:Shipping API](#shipping)
[:arrow_up:SellOut API](#up)

<a name="product_delivery"></a>
### 6. `[GET][Anon] product_unit/delivery/<product_id>/<size_id>` Вернет способы доставки для определенной цен
Response:
```json
[
    {
        "id": 1,
        "final_price": 79990,
        "start_price": 79990,
        "delivery": {
            "id": 1,
            "name": "poizon"
        }
    }
]
```
[:arrow_up:Shipping API](#shipping)
[:arrow_up:SellOut API](#up)

<a name="wishlist"></a>

## WishList API

[:arrow_up:SellOut API](#up)
<a name="wl"></a>

### 1. `[GET][User] wishlist/<user_id>` вишлист пользователя

Response:

```json
[
  {
    "id": 4,
    "product": {
      "id": 1,
      "name": "Air Force 1",
      "bucket_link": "/buck",
      "description": "desc",
      "sku": "air_force_1",
      "available_flag": true,
      "last_upd": "2023-04-07T15:28:17Z",
      "add_date": "2023-04-07",
      "fit": 1,
      "rel_num": 1,
      "gender": {
        "id": 1,
        "name": "M"
      },
      "brands": [
        {
          "id": 1,
          "name": "Nike"
        }
      ],
      "categories": [
        {
          "id": 1,
          "name": "Sport"
        }
      ],
      "tags": [
        {
          "id": 1,
          "name": "Style"
        }
      ],
      "min_price": 7,
      "in_wishlist": true
    },
    "size": {
      "id": 2,
      "INT": "0",
      "US": "0",
      "UK": "0",
      "EU": "0",
      "IT": "0",
      "RU": "0",
      "product": 1
    },
    "product_unit": {
      "id": 1,
      "final_price": 7,
      "availability": true,
      "product": {
        "id": 1,
        "name": "Air Force 1",
        "bucket_link": "/buck",
        "description": "desc",
        "sku": "air_force_1",
        "available_flag": true,
        "last_upd": "2023-04-07T15:28:17Z",
        "add_date": "2023-04-07",
        "fit": 1,
        "rel_num": 1,
        "gender": {
          "id": 1,
          "name": "M"
        },
        "brands": [
          {
            "id": 1,
            "name": "Nike"
          }
        ],
        "categories": [
          {
            "id": 1,
            "name": "Sport"
          }
        ],
        "tags": [
          {
            "id": 1,
            "name": "Style"
          }
        ]
      },
      "size": {
        "id": 1,
        "INT": "12",
        "US": "12",
        "UK": "12",
        "EU": "12",
        "IT": "12",
        "RU": "12",
        "product": {
          "id": 1,
          "name": "Air Force 1",
          "bucket_link": "/buck",
          "description": "desc",
          "sku": "air_force_1",
          "available_flag": true,
          "last_upd": "2023-04-07T15:28:17Z",
          "add_date": "2023-04-07",
          "fit": 1,
          "rel_num": 1,
          "gender": 1,
          "brands": [
            1
          ],
          "categories": [
            1
          ],
          "tags": [
            1
          ]
        }
      },
      "currency": {
        "id": 2,
        "name": "pending"
      },
      "delivery_type": {
        "id": 1,
        "name": "Самолёт"
      },
      "platform": {
        "id": 1,
        "platform": "Poizon",
        "site": "/poizon"
      }
    }
  }
]
```

[:arrow_up:WishList API](#wishlist)
[:arrow_up:SellOut API](#up)
<a name="add_wl"></a>

### 2. `[POST][User] wishlist/add/<user_id>` добавление в вишлист
Body:
```json
{
   
   "product_id": id,
   "size_id": id
}
```

Response: карточку вишлиста
<a name="del_wl"></a>

### 3. `[delete][User] wishlist/delete/<wishlist_unit_id>` Удаление из вишлиста
Response("Элемент успешно удален из списка желаний")

Response: карточку вишлиста
<a name="change_wl"></a>

### 4. `[POST][User] wishlist/change_size/<user_id>/<wishlist_unit_id>/<size_id>` поменять размер в вишлисте

Response: карточку вишлиста
[:arrow_up:WishList API](#wishlist)
[:arrow_up:SellOut API](#up)

<a name="orders"></a>

## Orders API

[:arrow_up:SellOut API](#up)
<a name="cart"></a>

### 1. `[GET][User] order/cart/<user_id>` корзина пользователя

Response:

```json
{
    "id": 1,
    "promo_code": {
        "id": 1,
        "owner": null,
        "string_representation": "PENIS",
        "discount_percentage": 50,
        "discount_absolute": 0,
        "activation_count": 0,
        "max_activation_count": 1,
        "active_status": true,
        "active_until_date": "2023-08-02"
    },
    "product_units": [
        {
            "id": 3,
            "product": {
                "id": 1,
                "in_wishlist": false,
                "min_price_product_unit": 32990,
                "model": "Баскетбольные шорты",
                "colorway": "SS18 Bolt Basketball Short Black",
                "russian_name": "SS18 Bolt Basketball Short Black",
                "slug": "supreme-ss18-bolt-basketball-short-black-1",
                "manufacturer_sku": "SUP-SS18-407",
                "description": "",
                "is_custom": false,
                "is_collab": false,
                "designer_color": "",
                "min_price": 32990,
                "available_flag": true,
                "has_many_sizes": false,
                "has_many_colors": false,
                "has_many_configurations": false,
                "exact_date": "2018-06-07",
                "approximate_date": "07.06.2018",
                "fit": 0,
                "rel_num": 442,
                "main_line": null,
                "collab": null,
                "main_color": {
                    "id": 1,
                    "name": "multicolour",
                    "is_main_color": false,
                    "russian_name": "",
                    "hex": ""
                },
                "recommended_gender": null,
                "size_table_platform": null,
                "brands": [
                    {
                        "id": 1,
                        "name": "Supreme",
                        "query_name": "supreme"
                    }
                ],
                "categories": [
                    {
                        "id": 21,
                        "name": "Одежда",
                        "eng_name": "clothes",
                        "is_all": false,
                        "full_name": "Одежда",
                        "parent_category": null
                    },
                    {
                        "id": 22,
                        "name": "Вся одежда",
                        "eng_name": "clothes",
                        "is_all": true,
                        "full_name": "Одежда | Вся одежда",
                        "parent_category": {
                            "id": 21,
                            "name": "Одежда",
                            "eng_name": "clothes",
                            "is_all": false,
                            "full_name": "Одежда",
                            "parent_category": null
                        }
                    },
                    {
                        "id": 39,
                        "name": "Спортивная одежда",
                        "eng_name": "sport_clothes",
                        "is_all": false,
                        "full_name": "Одежда | Спортивная одежда",
                        "parent_category": {
                            "id": 21,
                            "name": "Одежда",
                            "eng_name": "clothes",
                            "is_all": false,
                            "full_name": "Одежда",
                            "parent_category": null
                        }
                    },
                    {
                        "id": 40,
                        "name": "Вся спортивная одежда",
                        "eng_name": "sport_clothes",
                        "is_all": true,
                        "full_name": "Одежда | Спортивная одежда | Вся спортивная одежда",
                        "parent_category": {
                            "id": 39,
                            "name": "Спортивная одежда",
                            "eng_name": "sport_clothes",
                            "is_all": false,
                            "full_name": "Одежда | Спортивная одежда",
                            "parent_category": 21
                        }
                    },
                    {
                        "id": 42,
                        "name": "Баскетбольные шорты",
                        "eng_name": "basketball_shorts",
                        "is_all": false,
                        "full_name": "Одежда | Спортивная одежда | Баскетбольные шорты",
                        "parent_category": {
                            "id": 39,
                            "name": "Спортивная одежда",
                            "eng_name": "sport_clothes",
                            "is_all": false,
                            "full_name": "Одежда | Спортивная одежда",
                            "parent_category": 21
                        }
                    }
                ],
                "lines": [
                    {
                        "id": 224,
                        "name": "Supreme",
                        "is_all": false,
                        "view_name": "Supreme",
                        "full_name": "Supreme",
                        "full_eng_name": "supreme",
                        "parent_line": null
                    }
                ],
                "tags": [],
                "bucket_link": [
                    {
                        "id": 1,
                        "url": "https://cdn.poizon.com/pro-img/origin-img/20220602/8aee0879b67c44d6aaadb7e1543f3c83.jpg"
                    },
                    {
                        "id": 2,
                        "url": "https://cdn.poizon.com/pro-img/origin-img/20220602/673a05450cef44a6b6fd0f8a309b4694.jpg"
                    },
                    {
                        "id": 3,
                        "url": "https://cdn.poizon.com/pro-img/origin-img/20220602/baaed7d7c48d4156860e578e241e3d99.jpg"
                    }
                ],
                "colors": [],
                "gender": [
                    {
                        "id": 1,
                        "name": "M"
                    },
                    {
                        "id": 2,
                        "name": "F"
                    }
                ]
            },
            "size_platform": "",
            "good_size_platform": "36.5",
            "size_table_platform": "",
            "color": "",
            "configuration": "",
            "start_price": 65990,
            "final_price": 65990,
            "url": "",
            "availability": true,
            "warehouse": false,
            "is_multiple": false,
            "is_return": true,
            "is_fast_shipping": false,
            "is_sale": false,
            "currency": {
                "id": 1,
                "name": "pending"
            },
            "delivery_type": {
                "id": 4,
                "name": "до 30 дней",
                "view_name": null
            },
            "platform": {
                "id": 2,
                "platform": "poizon",
                "site": "poizon"
            }
        },
        {
            "id": 4,
            "product": {
                "id": 1,
                "in_wishlist": false,
                "min_price_product_unit": 32990,
                "model": "Баскетбольные шорты",
                "colorway": "SS18 Bolt Basketball Short Black",
                "russian_name": "SS18 Bolt Basketball Short Black",
                "slug": "supreme-ss18-bolt-basketball-short-black-1",
                "manufacturer_sku": "SUP-SS18-407",
                "description": "",
                "is_custom": false,
                "is_collab": false,
                "designer_color": "",
                "min_price": 32990,
                "available_flag": true,
                "has_many_sizes": false,
                "has_many_colors": false,
                "has_many_configurations": false,
                "exact_date": "2018-06-07",
                "approximate_date": "07.06.2018",
                "fit": 0,
                "rel_num": 442,
                "main_line": null,
                "collab": null,
                "main_color": {
                    "id": 1,
                    "name": "multicolour",
                    "is_main_color": false,
                    "russian_name": "",
                    "hex": ""
                },
                "recommended_gender": null,
                "size_table_platform": null,
                "brands": [
                    {
                        "id": 1,
                        "name": "Supreme",
                        "query_name": "supreme"
                    }
                ],
                "categories": [
                    {
                        "id": 21,
                        "name": "Одежда",
                        "eng_name": "clothes",
                        "is_all": false,
                        "full_name": "Одежда",
                        "parent_category": null
                    },
                    {
                        "id": 22,
                        "name": "Вся одежда",
                        "eng_name": "clothes",
                        "is_all": true,
                        "full_name": "Одежда | Вся одежда",
                        "parent_category": {
                            "id": 21,
                            "name": "Одежда",
                            "eng_name": "clothes",
                            "is_all": false,
                            "full_name": "Одежда",
                            "parent_category": null
                        }
                    },
                    {
                        "id": 39,
                        "name": "Спортивная одежда",
                        "eng_name": "sport_clothes",
                        "is_all": false,
                        "full_name": "Одежда | Спортивная одежда",
                        "parent_category": {
                            "id": 21,
                            "name": "Одежда",
                            "eng_name": "clothes",
                            "is_all": false,
                            "full_name": "Одежда",
                            "parent_category": null
                        }
                    },
                    {
                        "id": 40,
                        "name": "Вся спортивная одежда",
                        "eng_name": "sport_clothes",
                        "is_all": true,
                        "full_name": "Одежда | Спортивная одежда | Вся спортивная одежда",
                        "parent_category": {
                            "id": 39,
                            "name": "Спортивная одежда",
                            "eng_name": "sport_clothes",
                            "is_all": false,
                            "full_name": "Одежда | Спортивная одежда",
                            "parent_category": 21
                        }
                    },
                    {
                        "id": 42,
                        "name": "Баскетбольные шорты",
                        "eng_name": "basketball_shorts",
                        "is_all": false,
                        "full_name": "Одежда | Спортивная одежда | Баскетбольные шорты",
                        "parent_category": {
                            "id": 39,
                            "name": "Спортивная одежда",
                            "eng_name": "sport_clothes",
                            "is_all": false,
                            "full_name": "Одежда | Спортивная одежда",
                            "parent_category": 21
                        }
                    }
                ],
                "lines": [
                    {
                        "id": 224,
                        "name": "Supreme",
                        "is_all": false,
                        "view_name": "Supreme",
                        "full_name": "Supreme",
                        "full_eng_name": "supreme",
                        "parent_line": null
                    }
                ],
                "tags": [],
                "bucket_link": [
                    {
                        "id": 1,
                        "url": "https://cdn.poizon.com/pro-img/origin-img/20220602/8aee0879b67c44d6aaadb7e1543f3c83.jpg"
                    },
                    {
                        "id": 2,
                        "url": "https://cdn.poizon.com/pro-img/origin-img/20220602/673a05450cef44a6b6fd0f8a309b4694.jpg"
                    },
                    {
                        "id": 3,
                        "url": "https://cdn.poizon.com/pro-img/origin-img/20220602/baaed7d7c48d4156860e578e241e3d99.jpg"
                    }
                ],
                "colors": [],
                "gender": [
                    {
                        "id": 1,
                        "name": "M"
                    },
                    {
                        "id": 2,
                        "name": "F"
                    }
                ]
            },
            "size_platform": "",
            "good_size_platform": "36",
            "size_table_platform": "",
            "color": "",
            "configuration": "",
            "start_price": 32990,
            "final_price": 32990,
            "url": "",
            "availability": false,
            "warehouse": false,
            "is_multiple": false,
            "is_return": true,
            "is_fast_shipping": true,
            "is_sale": true,
            "currency": {
                "id": 1,
                "name": "pending"
            },
            "delivery_type": {
                "id": 4,
                "name": "до 30 дней",
                "view_name": null
            },
            "platform": {
                "id": 2,
                "platform": "poizon",
                "site": "poizon"
            }
        }
    ],
    "bonus": 0,
    "total_amount": 98980,
    "bonus_sale": 0,
    "promo_sale": 49490,
    "final_amount": 49490
}
```

[:arrow_up:Orders API](#orders)
[:arrow_up:SellOut API](#up)
<a name="add_to_cart"></a>

### 2. `[POST][User] order/cart/<user_id>/<product_unit_id>` добавить юнит в корзину

Response:
Вернет unit

[:arrow_up:Orders API](#orders)
[:arrow_up:SellOut API](#up)
<a name="del_from_cart"></a>

### 3. `[DELETE][User] order/cart/<user_id>/<product_unit_id>` удалить юнит из корзины

Response:

```json
{
  "id": 2,
  "final_price": 100,
  "availability": true,
  "product": {
    "id": 2,
    "name": "Dunk",
    "bucket_link": "/buck",
    "description": "desc",
    "sku": "sku",
    "available_flag": true,
    "last_upd": "2023-04-07T15:59:39Z",
    "add_date": "2023-04-07",
    "fit": 0,
    "rel_num": 0,
    "gender": {
      "id": 1,
      "name": "M"
    },
    "brands": [
      {
        "id": 1,
        "name": "Nike"
      }
    ],
    "categories": [
      {
        "id": 1,
        "name": "Sport"
      }
    ],
    "tags": [
      {
        "id": 1,
        "name": "Style"
      }
    ]
  },
  "size": {
    "id": 1,
    "INT": "12",
    "US": "12",
    "UK": "12",
    "EU": "12",
    "IT": "12",
    "RU": "12",
    "product": {
      "id": 1,
      "name": "Air Force 1",
      "bucket_link": "/buck",
      "description": "desc",
      "sku": "air_force_1",
      "available_flag": true,
      "last_upd": "2023-04-07T15:28:17Z",
      "add_date": "2023-04-07",
      "fit": 1,
      "rel_num": 1,
      "gender": 1,
      "brands": [
        1
      ],
      "categories": [
        1
      ],
      "tags": [
        1
      ]
    }
  },
  "currency": {
    "id": 2,
    "name": "pending"
  },
  "delivery_type": {
    "id": 1,
    "name": "Самолёт"
  },
  "platform": {
    "id": 1,
    "platform": "Poizon",
    "site": "/poizon"
  }
}
```

[:arrow_up:Orders API](#orders)
[:arrow_up:SellOut API](#up)
<a name="checkout"></a>

### 4. `[POST][User] order/checkout/<user_id>` оформить заказ

Body:

```json
{
  "product_unit": [
    1,
    2
  ],
  "email": "mail@mail.ru",
  "tel": 77777777777,
  "first_name": "Имя",
  "last_name": "Фамилия",
  "address_id": 1,
  "promo_code": "SALE",
  "total_amount": 10000
}
```

Response:

```json
{
  "id": 13,
  "total_amount": 10000,
  "email": "mail@mail.ru",
  "tel": "77777777777",
  "name": "Имя",
  "surname": "Фамилия",
  "fact_of_payment": false,
  "user": {
    "id": 1,
    "last_login": "2023-04-12T15:14:50.148633Z",
    "is_superuser": true,
    "username": "artem",
    "first_name": "",
    "last_name": "",
    "email": "arten@mail.ru",
    "is_staff": true,
    "is_active": true,
    "date_joined": "2023-04-07T15:26:38Z",
    "all_purchase_amount": 0,
    "personal_discount_percentage": 0,
    "referral_link": null,
    "preferred_size_grid": null,
    "gender": null,
    "ref_user": null,
    "groups": [],
    "user_permissions": [],
    "my_groups": [],
    "address": [],
    "last_viewed_products": [
      {
        "id": 1,
        "name": "Air Force 1",
        "bucket_link": "/buck",
        "description": "desc",
        "sku": "air_force_1",
        "available_flag": true,
        "last_upd": "2023-04-07T15:28:17Z",
        "add_date": "2023-04-07",
        "fit": 1,
        "rel_num": 1,
        "gender": 1,
        "brands": [
          1
        ],
        "categories": [
          1
        ],
        "tags": [
          1
        ]
      },
      {
        "id": 2,
        "name": "Dunk",
        "bucket_link": "/buck",
        "description": "desc",
        "sku": "sku",
        "available_flag": true,
        "last_upd": "2023-04-07T15:59:39Z",
        "add_date": "2023-04-07",
        "fit": 0,
        "rel_num": 0,
        "gender": 1,
        "brands": [
          1
        ],
        "categories": [
          1
        ],
        "tags": [
          1
        ]
      }
    ]
  },
  "address": {
    "id": 1,
    "address": "Проспект Мира 111",
    "post_index": "308033"
  },
  "promo_code": {
    "id": 1,
    "string_representation": "SALE",
    "discount_percentage": 15,
    "discount_absolute": 0,
    "activation_count": 6,
    "max_activation_count": 10,
    "active_status": true,
    "active_until_date": "2023-04-18",
    "owner": {
      "id": 1,
      "last_login": "2023-04-12T15:14:50.148633Z",
      "is_superuser": true,
      "username": "artem",
      "first_name": "",
      "last_name": "",
      "email": "arten@mail.ru",
      "is_staff": true,
      "is_active": true,
      "date_joined": "2023-04-07T15:26:38Z",
      "all_purchase_amount": 0,
      "personal_discount_percentage": 0,
      "referral_link": null,
      "preferred_size_grid": null,
      "gender": null,
      "ref_user": null,
      "groups": [],
      "user_permissions": [],
      "my_groups": [],
      "address": [],
      "last_viewed_products": [
        1,
        2
      ]
    }
  },
  "status": {
    "id": 1,
    "name": "pending"
  },
  "product_unit": [
    {
      "id": 1,
      "final_price": 7,
      "availability": true,
      "product": {
        "id": 1,
        "name": "Air Force 1",
        "bucket_link": "/buck",
        "description": "desc",
        "sku": "air_force_1",
        "available_flag": true,
        "last_upd": "2023-04-07T15:28:17Z",
        "add_date": "2023-04-07",
        "fit": 1,
        "rel_num": 1,
        "gender": 1,
        "brands": [
          1
        ],
        "categories": [
          1
        ],
        "tags": [
          1
        ]
      },
      "size": {
        "id": 1,
        "INT": "12",
        "US": "12",
        "UK": "12",
        "EU": "12",
        "IT": "12",
        "RU": "12",
        "product": 1
      },
      "currency": {
        "id": 2,
        "name": "pending"
      },
      "delivery_type": {
        "id": 1,
        "name": "Самолёт"
      },
      "platform": {
        "id": 1,
        "platform": "Poizon",
        "site": "/poizon"
      }
    },
    {
      "id": 2,
      "final_price": 100,
      "availability": true,
      "product": {
        "id": 2,
        "name": "Dunk",
        "bucket_link": "/buck",
        "description": "desc",
        "sku": "sku",
        "available_flag": true,
        "last_upd": "2023-04-07T15:59:39Z",
        "add_date": "2023-04-07",
        "fit": 0,
        "rel_num": 0,
        "gender": 1,
        "brands": [
          1
        ],
        "categories": [
          1
        ],
        "tags": [
          1
        ]
      },
      "size": {
        "id": 1,
        "INT": "12",
        "US": "12",
        "UK": "12",
        "EU": "12",
        "IT": "12",
        "RU": "12",
        "product": 1
      },
      "currency": {
        "id": 2,
        "name": "pending"
      },
      "delivery_type": {
        "id": 1,
        "name": "Самолёт"
      },
      "platform": {
        "id": 1,
        "platform": "Poizon",
        "site": "/poizon"
      }
    }
  ]
}
```

[:arrow_up:Orders API](#orders)
[:arrow_up:SellOut API](#up)

<a name="orderss"></a>

5. `[GET][Admin] order/orders` все заказы

Response:

```json
[
  {
    "id": 1,
    "user": {
      "id": 1,
      "password": "pbkdf2_sha256$390000$UADInQibzAcqaOZFSEcvAS$A7F5JXyyClktLYYkVZ+mjF7xfF97ArSC/mJW7GEzDA8=",
      "last_login": "2023-04-21T14:57:10.100840Z",
      "is_superuser": true,
      "username": "artem",
      "first_name": "",
      "last_name": "",
      "email": "arten@mail.ru",
      "is_staff": true,
      "is_active": true,
      "date_joined": "2023-04-07T15:26:38Z",
      "all_purchase_amount": 0,
      "personal_discount_percentage": 0,
      "referral_link": null,
      "preferred_size_grid": null,
      "gender": null,
      "ref_user": null,
      "groups": [],
      "user_permissions": [],
      "my_groups": [],
      "address": [],
      "last_viewed_products": [
        {
          "id": 1,
          "name": "Air Force 1",
          "bucket_link": "/buck",
          "description": "desc",
          "sku": "air_force_1",
          "available_flag": true,
          "last_upd": "2023-04-07T15:28:17Z",
          "add_date": "2023-04-07",
          "fit": 1,
          "rel_num": 1,
          "gender": 1,
          "brands": [
            1
          ],
          "categories": [
            1
          ],
          "tags": [
            1
          ]
        },
        {
          "id": 2,
          "name": "Dunk",
          "bucket_link": "/buck",
          "description": "desc",
          "sku": "sku",
          "available_flag": true,
          "last_upd": "2023-04-07T15:59:39Z",
          "add_date": "2023-04-07",
          "fit": 0,
          "rel_num": 0,
          "gender": 1,
          "brands": [
            1
          ],
          "categories": [
            1
          ],
          "tags": [
            1
          ]
        }
      ]
    },
    "product_units": [
      {
        "id": 1,
        "final_price": 7,
        "availability": true,
        "product": {
          "id": 1,
          "name": "Air Force 1",
          "bucket_link": "/buck",
          "description": "desc",
          "sku": "air_force_1",
          "available_flag": true,
          "last_upd": "2023-04-07T15:28:17Z",
          "add_date": "2023-04-07",
          "fit": 1,
          "rel_num": 1,
          "gender": 1,
          "brands": [
            1
          ],
          "categories": [
            1
          ],
          "tags": [
            1
          ]
        },
        "size": {
          "id": 1,
          "INT": "12",
          "US": "12",
          "UK": "12",
          "EU": "12",
          "IT": "12",
          "RU": "12",
          "product": 1
        },
        "currency": {
          "id": 2,
          "name": "pending"
        },
        "delivery_type": {
          "id": 1,
          "name": "Самолёт"
        },
        "platform": {
          "id": 1,
          "platform": "Poizon",
          "site": "/poizon"
        }
      },
      {
        "id": 2,
        "final_price": 100,
        "availability": true,
        "product": {
          "id": 2,
          "name": "Dunk",
          "bucket_link": "/buck",
          "description": "desc",
          "sku": "sku",
          "available_flag": true,
          "last_upd": "2023-04-07T15:59:39Z",
          "add_date": "2023-04-07",
          "fit": 0,
          "rel_num": 0,
          "gender": 1,
          "brands": [
            1
          ],
          "categories": [
            1
          ],
          "tags": [
            1
          ]
        },
        "size": {
          "id": 1,
          "INT": "12",
          "US": "12",
          "UK": "12",
          "EU": "12",
          "IT": "12",
          "RU": "12",
          "product": 1
        },
        "currency": {
          "id": 2,
          "name": "pending"
        },
        "delivery_type": {
          "id": 1,
          "name": "Самолёт"
        },
        "platform": {
          "id": 1,
          "platform": "Poizon",
          "site": "/poizon"
        }
      }
    ]
  },
  {
    "id": 2,
    "user": {
      "id": 2,
      "password": "pbkdf2_sha256$390000$UADInQibzAcqaOZFSEcvAS$A7F5JXyyClktLYYkVZ+mjF7xfF97ArSC/mJW7GEzDA8=",
      "last_login": "2023-04-12T10:07:07Z",
      "is_superuser": false,
      "username": "noadmin",
      "first_name": "no",
      "last_name": "admin",
      "email": "noadmin@mail.ru",
      "is_staff": false,
      "is_active": true,
      "date_joined": "2023-04-12T10:07:34Z",
      "all_purchase_amount": 0,
      "personal_discount_percentage": 0,
      "referral_link": null,
      "preferred_size_grid": null,
      "gender": null,
      "ref_user": null,
      "groups": [],
      "user_permissions": [],
      "my_groups": [],
      "address": [],
      "last_viewed_products": [
        {
          "id": 1,
          "name": "Air Force 1",
          "bucket_link": "/buck",
          "description": "desc",
          "sku": "air_force_1",
          "available_flag": true,
          "last_upd": "2023-04-07T15:28:17Z",
          "add_date": "2023-04-07",
          "fit": 1,
          "rel_num": 1,
          "gender": 1,
          "brands": [
            1
          ],
          "categories": [
            1
          ],
          "tags": [
            1
          ]
        },
        {
          "id": 2,
          "name": "Dunk",
          "bucket_link": "/buck",
          "description": "desc",
          "sku": "sku",
          "available_flag": true,
          "last_upd": "2023-04-07T15:59:39Z",
          "add_date": "2023-04-07",
          "fit": 0,
          "rel_num": 0,
          "gender": 1,
          "brands": [
            1
          ],
          "categories": [
            1
          ],
          "tags": [
            1
          ]
        }
      ]
    },
    "product_units": [
      {
        "id": 1,
        "final_price": 7,
        "availability": true,
        "product": {
          "id": 1,
          "name": "Air Force 1",
          "bucket_link": "/buck",
          "description": "desc",
          "sku": "air_force_1",
          "available_flag": true,
          "last_upd": "2023-04-07T15:28:17Z",
          "add_date": "2023-04-07",
          "fit": 1,
          "rel_num": 1,
          "gender": 1,
          "brands": [
            1
          ],
          "categories": [
            1
          ],
          "tags": [
            1
          ]
        },
        "size": {
          "id": 1,
          "INT": "12",
          "US": "12",
          "UK": "12",
          "EU": "12",
          "IT": "12",
          "RU": "12",
          "product": 1
        },
        "currency": {
          "id": 2,
          "name": "pending"
        },
        "delivery_type": {
          "id": 1,
          "name": "Самолёт"
        },
        "platform": {
          "id": 1,
          "platform": "Poizon",
          "site": "/poizon"
        }
      }
    ]
  }
]
```

[:arrow_up:Orders API](#orders)
[:arrow_up:SellOut API](#up)

<a name="user_orders"></a>

6. `[GET][User] order/user_orders/<user_id>` все заказы пользователя

Response:

```json
[
  {
    "id": 2,
    "total_amount": 107,
    "email": "sh@mail.ru",
    "tel": "7777777777777",
    "name": "artem",
    "surname": "sh",
    "fact_of_payment": false,
    "user": {
      "id": 2,
      "password": "pbkdf2_sha256$390000$UADInQibzAcqaOZFSEcvAS$A7F5JXyyClktLYYkVZ+mjF7xfF97ArSC/mJW7GEzDA8=",
      "last_login": "2023-04-12T10:07:07Z",
      "is_superuser": false,
      "username": "noadmin",
      "first_name": "no",
      "last_name": "admin",
      "email": "noadmin@mail.ru",
      "is_staff": false,
      "is_active": true,
      "date_joined": "2023-04-12T10:07:34Z",
      "all_purchase_amount": 0,
      "personal_discount_percentage": 0,
      "referral_link": null,
      "preferred_size_grid": null,
      "gender": null,
      "ref_user": null,
      "groups": [],
      "user_permissions": [],
      "my_groups": [],
      "address": [],
      "last_viewed_products": [
        {
          "id": 1,
          "name": "Air Force 1",
          "bucket_link": "/buck",
          "description": "desc",
          "sku": "air_force_1",
          "available_flag": true,
          "last_upd": "2023-04-07T15:28:17Z",
          "add_date": "2023-04-07",
          "fit": 1,
          "rel_num": 1,
          "gender": 1,
          "brands": [
            1
          ],
          "categories": [
            1
          ],
          "tags": [
            1
          ]
        },
        {
          "id": 2,
          "name": "Dunk",
          "bucket_link": "/buck",
          "description": "desc",
          "sku": "sku",
          "available_flag": true,
          "last_upd": "2023-04-07T15:59:39Z",
          "add_date": "2023-04-07",
          "fit": 0,
          "rel_num": 0,
          "gender": 1,
          "brands": [
            1
          ],
          "categories": [
            1
          ],
          "tags": [
            1
          ]
        }
      ]
    },
    "address": {
      "id": 1,
      "address": "Проспект Мира 111",
      "post_index": "308033"
    },
    "promo_code": null,
    "status": {
      "id": 1,
      "name": "pending"
    },
    "product_unit": [
      {
        "id": 1,
        "final_price": 7,
        "availability": true,
        "product": {
          "id": 1,
          "name": "Air Force 1",
          "bucket_link": "/buck",
          "description": "desc",
          "sku": "air_force_1",
          "available_flag": true,
          "last_upd": "2023-04-07T15:28:17Z",
          "add_date": "2023-04-07",
          "fit": 1,
          "rel_num": 1,
          "gender": 1,
          "brands": [
            1
          ],
          "categories": [
            1
          ],
          "tags": [
            1
          ]
        },
        "size": {
          "id": 1,
          "INT": "12",
          "US": "12",
          "UK": "12",
          "EU": "12",
          "IT": "12",
          "RU": "12",
          "product": 1
        },
        "currency": {
          "id": 2,
          "name": "pending"
        },
        "delivery_type": {
          "id": 1,
          "name": "Самолёт"
        },
        "platform": {
          "id": 1,
          "platform": "Poizon",
          "site": "/poizon"
        }
      },
      {
        "id": 2,
        "final_price": 100,
        "availability": true,
        "product": {
          "id": 2,
          "name": "Dunk",
          "bucket_link": "/buck",
          "description": "desc",
          "sku": "sku",
          "available_flag": true,
          "last_upd": "2023-04-07T15:59:39Z",
          "add_date": "2023-04-07",
          "fit": 0,
          "rel_num": 0,
          "gender": 1,
          "brands": [
            1
          ],
          "categories": [
            1
          ],
          "tags": [
            1
          ]
        },
        "size": {
          "id": 1,
          "INT": "12",
          "US": "12",
          "UK": "12",
          "EU": "12",
          "IT": "12",
          "RU": "12",
          "product": 1
        },
        "currency": {
          "id": 2,
          "name": "pending"
        },
        "delivery_type": {
          "id": 1,
          "name": "Самолёт"
        },
        "platform": {
          "id": 1,
          "platform": "Poizon",
          "site": "/poizon"
        }
      }
    ]
  }
]
```

[:arrow_up:Orders API](#orders)
[:arrow_up:SellOut API](#up)

<a name="order"></a>

7. `[GET][User] order/info/<order_id>` информация о заказе

Response:

```json
[
  {
    "id": 2,
    "total_amount": 107,
    "email": "sh@mail.ru",
    "tel": "7777777777777",
    "name": "artem",
    "surname": "sh",
    "fact_of_payment": false,
    "user": {
      "id": 2,
      "password": "pbkdf2_sha256$390000$UADInQibzAcqaOZFSEcvAS$A7F5JXyyClktLYYkVZ+mjF7xfF97ArSC/mJW7GEzDA8=",
      "last_login": "2023-04-12T10:07:07Z",
      "is_superuser": false,
      "username": "noadmin",
      "first_name": "no",
      "last_name": "admin",
      "email": "noadmin@mail.ru",
      "is_staff": false,
      "is_active": true,
      "date_joined": "2023-04-12T10:07:34Z",
      "all_purchase_amount": 0,
      "personal_discount_percentage": 0,
      "referral_link": null,
      "preferred_size_grid": null,
      "gender": null,
      "ref_user": null,
      "groups": [],
      "user_permissions": [],
      "my_groups": [],
      "address": [],
      "last_viewed_products": [
        {
          "id": 1,
          "name": "Air Force 1",
          "bucket_link": "/buck",
          "description": "desc",
          "sku": "air_force_1",
          "available_flag": true,
          "last_upd": "2023-04-07T15:28:17Z",
          "add_date": "2023-04-07",
          "fit": 1,
          "rel_num": 1,
          "gender": 1,
          "brands": [
            1
          ],
          "categories": [
            1
          ],
          "tags": [
            1
          ]
        },
        {
          "id": 2,
          "name": "Dunk",
          "bucket_link": "/buck",
          "description": "desc",
          "sku": "sku",
          "available_flag": true,
          "last_upd": "2023-04-07T15:59:39Z",
          "add_date": "2023-04-07",
          "fit": 0,
          "rel_num": 0,
          "gender": 1,
          "brands": [
            1
          ],
          "categories": [
            1
          ],
          "tags": [
            1
          ]
        }
      ]
    },
    "address": {
      "id": 1,
      "address": "Проспект Мира 111",
      "post_index": "308033"
    },
    "promo_code": null,
    "status": {
      "id": 1,
      "name": "pending"
    },
    "product_unit": [
      {
        "id": 1,
        "final_price": 7,
        "availability": true,
        "product": {
          "id": 1,
          "name": "Air Force 1",
          "bucket_link": "/buck",
          "description": "desc",
          "sku": "air_force_1",
          "available_flag": true,
          "last_upd": "2023-04-07T15:28:17Z",
          "add_date": "2023-04-07",
          "fit": 1,
          "rel_num": 1,
          "gender": 1,
          "brands": [
            1
          ],
          "categories": [
            1
          ],
          "tags": [
            1
          ]
        },
        "size": {
          "id": 1,
          "INT": "12",
          "US": "12",
          "UK": "12",
          "EU": "12",
          "IT": "12",
          "RU": "12",
          "product": 1
        },
        "currency": {
          "id": 2,
          "name": "pending"
        },
        "delivery_type": {
          "id": 1,
          "name": "Самолёт"
        },
        "platform": {
          "id": 1,
          "platform": "Poizon",
          "site": "/poizon"
        }
      },
      {
        "id": 2,
        "final_price": 100,
        "availability": true,
        "product": {
          "id": 2,
          "name": "Dunk",
          "bucket_link": "/buck",
          "description": "desc",
          "sku": "sku",
          "available_flag": true,
          "last_upd": "2023-04-07T15:59:39Z",
          "add_date": "2023-04-07",
          "fit": 0,
          "rel_num": 0,
          "gender": 1,
          "brands": [
            1
          ],
          "categories": [
            1
          ],
          "tags": [
            1
          ]
        },
        "size": {
          "id": 1,
          "INT": "12",
          "US": "12",
          "UK": "12",
          "EU": "12",
          "IT": "12",
          "RU": "12",
          "product": 1
        },
        "currency": {
          "id": 2,
          "name": "pending"
        },
        "delivery_type": {
          "id": 1,
          "name": "Самолёт"
        },
        "platform": {
          "id": 1,
          "platform": "Poizon",
          "site": "/poizon"
        }
      }
    ]
  }
]
```

[:arrow_up:Orders API](#orders)
[:arrow_up:SellOut API](#up)


