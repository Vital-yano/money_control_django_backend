# ruff: noqa
from datetime import timedelta

from .base import *

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres_local",
        "USER": "postgres_local",
        "PASSWORD": "postgres_local",
        "HOST": "localhost",
        "PORT": 5432,
    },
}

REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "password": "redis_local",
    "decode_responses": True,
    "db": 0,
}

USER_REGISTRATION_TIMEDELTA = timedelta(minutes=60)

# API_ID сервиса sms.ru
SMS_API_ID = os.getenv("SMS_API_ID")

# Параметр переопределяется в settings_test.py,
# чтобы при тестировании не отправлять запрос в sms.ru
TEST_RUNNING = False
