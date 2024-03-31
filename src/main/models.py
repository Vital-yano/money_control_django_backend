import uuid

from django.db import models
from redis.commands.search.field import TextField


class UserAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tg_id = models.TextField(unique=True)
    phone_number = models.CharField(max_length=12, unique=True)
    tg_nickname = models.CharField(max_length=32)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __repr__(self) -> str:
        return f"User(id={self.id}, phone_number={self.phone_number})"


redis_schema = (
    TextField("$.tg_id", as_name="tg_id"),
    TextField("$.phone_number", as_name="phone_number"),
    TextField("$.tg_nickname", as_name="tg_nickname"),
    TextField("$.verification_code", as_name="code"),
    TextField("$.expire_at", as_name="expire_at"),
)
