from django.conf import settings
from redis import Redis


def get_redis() -> Redis:
    redis_client = Redis(**settings.REDIS_CONFIG)
    return redis_client
