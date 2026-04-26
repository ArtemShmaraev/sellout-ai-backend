from .settings import *

# В тестах — отдельный минимальный URLConf без products (там SyntaxError).
ROOT_URLCONF = 'sellout.urls_test'

# Локальная SQLite вместо production PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# In-memory кеш вместо Memcached
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Elasticsearch не дёргается в тестах — связь не устанавливается, но если
# documents.py успел зарегистрировать соединение, переключаем хост на localhost.
ELASTIC_HOST = 'localhost'
ELASTICSEARCH_DSL = {
    'default': {'hosts': 'localhost:9200'},
}

# Отключаем безопасные cookie-флаги, чтобы test client не падал на них.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Быстрый хешер паролей.
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
