<a name="up"></a>
# SellOut API
<a name="user"></a>
## User API
[:arrow_up:SellOut API](#up)
### 1. `[GET][Admin] user` информация обо всех пользователях, списком

Response:
```json
[
    {
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
            }
        ]
    }
]
```
[:arrow_up:User API](#user)
### 2. `[GET][Admin] user/<user_id>` данные пользователя

Response:
```json
{
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
}
```
[:arrow_up:User API](#user)
### 3. `[POST][Anon] user/register` регистрация пользователя

Body:
```json
{
    "username": "mail@mail.ru",
    "password": "пароль",
    "first_name": "Имя",
    "last_name": "Фамилия",
    "gender": "male"
}

```
Response:
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4MjA4MjEyOSwiaWF0IjoxNjgxNDc3MzI5LCJqdGkiOiI2ZGExNTQ5MmMyODk0YzVmODhiNWRkN2EyNTcwNTg0MiIsInVzZXJfaWQiOjE3fQ.HhBV5bNIFtEaRaS96q_DAPAu5cdQhfRRHTcSHAl_Ffk",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgxNTYzNzI5LCJpYXQiOjE2ODE0NzczMjksImp0aSI6IjJjY2ZiZjNiZTJhYzQ3YTQ4NWRkNTY4ZGQzNWFiNzRhIiwidXNlcl9pZCI6MTd9.l-PcMX4WeUWmD5-egu1PNlgH_EdQb3tm2uIWUp57MzE"
}
```
[:arrow_up:User API](#user)
### 4. `[POST][Anon] user/login` вход в систему

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
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4MjA4MjEyOSwiaWF0IjoxNjgxNDc3MzI5LCJqdGkiOiI2ZGExNTQ5MmMyODk0YzVmODhiNWRkN2EyNTcwNTg0MiIsInVzZXJfaWQiOjE3fQ.HhBV5bNIFtEaRaS96q_DAPAu5cdQhfRRHTcSHAl_Ffk",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgxNTYzNzI5LCJpYXQiOjE2ODE0NzczMjksImp0aSI6IjJjY2ZiZjNiZTJhYzQ3YTQ4NWRkNTY4ZGQzNWFiNzRhIiwidXNlcl9pZCI6MTd9.l-PcMX4WeUWmD5-egu1PNlgH_EdQb3tm2uIWUp57MzE"
}
```
[:arrow_up:User APIд](#user)
### 5. `[GET][User] user/last_seen/<user_id>` последние 7 просмотренных товаров пользователя

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

<a name="product"></a>
## Product APi
[:arrow_up:SellOut API](#up)

### 1. `[GET][Admin] product` все товары
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
    }
]
```
[:arrow_up:Product API](#product)
### 2. `[GET][Admin] product/<product_id>` данные одного товара
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
    ]
}
```
[:arrow_up:Product API](#product)
### 3. `[GET][Anon] product/all/<num_page>` страница товаров 
Response:
```json
{
    "page number": 1,
    "items": [
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
}
```
[:arrow_up:Product API](#product)
<a name="shipping"></a>
[:arrow_up:SellOut API](#up)
## Shipping API
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
### 2. `[GET][Anon] product_unit/product_main/<product_id>/<user_id>` "картока товара" (если пользователь не авторизован user_id = 0)
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

<a name="wishlist"></a>
## WishList API
[:arrow_up:SellOut API](#up)
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

### 2. `[POST][User] wishlist/add/<user_id>/<product_id>/<size_id>` добавление в вишлист
Response: карточку вишлиста

### 3. `[delete][User] wishlist/delete/<wishlist_unit_id>` Удаление из вишлиста
Response: карточку вишлиста

### 4. `[POST][User] wishlist/add_no_size/<user_id>/<product_id>` добавить товара "без размера"
Response: карточку вишлиста

### 5. `[POST][User] wishlist/change_size/<user_id>/<wishlist_unit_id>/<size_id>` поменять размер в вишлисте
Response: карточку вишлиста
[:arrow_up:WishList API](#wishlist)


<a name="orders"></a>
## Orders API
[:arrow_up:SellOut API](#up)

### 1. `[GET][User] cart/user/<user_id>` корзина пользователя
Response:
```json
{
    "id": 1,
    "user": {
        "id": 1,
        "password": "pbkdf2_sha256$390000$UADInQibzAcqaOZFSEcvAS$A7F5JXyyClktLYYkVZ+mjF7xfF97ArSC/mJW7GEzDA8=",
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
```
[:arrow_up:Orders API](#orders)

### 2. `[POST][User] cart/add/<user_id>/<product_unit_id>` добавить юнит в корзину
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

### 3. `[DELETE][User] cart/delete/<user_id>/<product_unit_id>` удалить юнит из корзины
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

### 4. `[POST][User] cart/checkout/<user_id>` оформить заказ
Body:
```json

```




