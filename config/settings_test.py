# ruff: noqa
from datetime import timedelta

from .base import *

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres_test_local",
        "USER": "postgres_test_local",
        "PASSWORD": "postgres_test_local",
        "HOST": "localhost",
        "PORT": 5433,
    },
}

REDIS_CONFIG = {
    "host": "localhost",
    "port": 6380,
    "password": "redis_test",
    "decode_responses": True,
    "db": 0,
}

USER_REGISTRATION_TIMEDELTA = timedelta(minutes=60)

TEST_RUNNING = True
