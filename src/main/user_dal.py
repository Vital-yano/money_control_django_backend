import json
import logging
from datetime import UTC, datetime

from django.conf import settings
from redis import Redis
from redis.commands.json.path import Path
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.exceptions import ResponseError

from src.main.models import UserAccount, redis_schema

logger = logging.getLogger(__name__)


class UserDbDal:
    """Data Access Layer для операций с пользователями в db"""

    def create_user(self, tg_id: str, phone_number: str, tg_nickname: str):
        new_user = UserAccount.objects.create(  # type: ignore
            tg_id=tg_id, phone_number=phone_number, tg_nickname=tg_nickname
        )
        return new_user

    def get_user_by_tg_id(self, tg_id: str):
        user_by_tg_id = UserAccount.objects.get(tg_id=tg_id)  # type: ignore
        return user_by_tg_id


class UserRedisDAL:
    """Data Access Layer для операций с пользователями в Redis"""

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    def create_index(self):
        index = self.redis_client.ft("idx:user")
        try:
            index.create_index(
                redis_schema,
                definition=IndexDefinition(prefix=["user:"], index_type=IndexType.JSON),
            )
            logger.info("Index has been created!")
        except ResponseError as exc:
            if exc.args[0] == "Index already exists":
                logger.info(exc.args[0])

    def create_user(
        self, tg_id: str, phone_number: str, tg_nickname: str, verification_code: str
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

        self.redis_client.json().set(
            f"user:{new_user['tg_id']}", Path.root_path(), new_user
        )

        return new_user

    def get_user(self, tg_id: str) -> dict:
        user_from_redis = (
            self.redis_client.ft(index_name="idx:user").search(tg_id)
        ).docs[0]  # type: ignore
        user_from_redis = json.loads(user_from_redis.json)
        return user_from_redis
