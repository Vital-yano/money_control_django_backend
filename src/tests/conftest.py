import json
from datetime import UTC, datetime

import pytest
from django.conf import settings
from redis import ConnectionPool, Redis
from redis.commands.json.path import Path
from rest_framework.test import APIClient

from src.main.models import UserAccount


@pytest.fixture(scope="function")
def client():
    client = APIClient()
    yield client


@pytest.fixture
def create_user_in_database():
    def create_user_in_database(
        id: str, tg_id: str, phone_number: str, tg_nickname: str
    ):
        return UserAccount.objects.create(  # type: ignore
            id=id, tg_id=tg_id, phone_number=phone_number, tg_nickname=tg_nickname
        )

    return create_user_in_database


@pytest.fixture
def get_user_from_database():
    def get_user_from_database_by_id(tg_id):
        return UserAccount.objects.get(tg_id=tg_id)  # type: ignore

    return get_user_from_database_by_id


@pytest.fixture(scope="session")
def redis_pool():
    pool = ConnectionPool(**settings.REDIS_CONFIG)
    redis_client = Redis.from_pool(pool)
    yield redis_client
    redis_client.close()


@pytest.fixture
def get_user_from_redis(redis_pool):
    def get_user_from_redis_by_tg_id(tg_id: str):
        user_from_redis = (redis_pool.ft(index_name="idx:user").search(tg_id)).docs[0]
        user_from_redis = json.loads(user_from_redis.json)
        return user_from_redis

    return get_user_from_redis_by_tg_id


@pytest.fixture(scope="function", autouse=True)
def clean_redis(redis_pool):
    redis_pool.json().delete(Path.root_path())


@pytest.fixture
def add_user_to_redis(redis_pool):
    def add_user_to_redis(
        tg_id: str, phone_number: str, tg_nickname: str, verification_code: int
    ) -> dict:
        new_user = {
            "tg_id": tg_id,
            "phone_number": phone_number,
            "tg_nickname": tg_nickname,
            "verification_code": verification_code,
            "expire_at": datetime.strftime(
                datetime.now(UTC) + settings.USER_REGISTRATION_TIMEDELTA,
                "%Y-%m-%d %H:%M:%S",
            ),
        }

        redis_pool.json().set(f"user:{new_user['tg_id']}", Path.root_path(), new_user)

        return new_user

    return add_user_to_redis
