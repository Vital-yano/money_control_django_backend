from django.conf import settings
from django.core.management.base import BaseCommand
from redis import Redis

from config.settings_test import REDIS_CONFIG as REDIS_CONFIG_TEST
from src.main.user_dal import UserRedisDAL


def create_index(redis_config: dict):
    redis_client = Redis(**redis_config)
    user_redis_dal = UserRedisDAL(redis_client)
    user_redis_dal.create_index()
    redis_client.close()


class Command(BaseCommand):
    create_redis_index = "Create redis index"

    def handle(self, *args, **kwargs):
        create_index(REDIS_CONFIG_TEST)
        create_index(settings.REDIS_CONFIG)
