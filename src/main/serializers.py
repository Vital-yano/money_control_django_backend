import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from .models import UserAccount

PHONE_NUMBER_MATCH_PATTERN = re.compile(r"^\+7[0-9]+$")

VERIFICATION_CODE_MATCH_PATTERN = re.compile(r"^[0-9]{4}$")


def _validate_phone_number(value):
    if not PHONE_NUMBER_MATCH_PATTERN.match(value):
        raise ValidationError(
            "Phone number should start with +7 and contain only digits after that"
        )
    if len(value) != 12:
        raise ValidationError("Phone number should contain exactly 12 symbols")
    return value


class NaiveDateTimeField(serializers.DateTimeField):
    def enforce_timezone(self, value):
        if value.tzinfo is not None:
            return super().enforce_timezone(value)
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    verification_code = serializers.CharField()
    registration_time = NaiveDateTimeField(format="%Y-%m-%d %H:%M:%S", required=True)  # type: ignore
    phone_number = serializers.CharField(
        max_length=12,
        error_messages={"max_length": "Phone number should contain exactly 12 symbols"},
        validators=[UniqueValidator(queryset=UserAccount.objects.all())],  # type: ignore
    )

    def validate_phone_number(self, value):
        return _validate_phone_number(value)

    def validate_verification_code(self, value):
        if not VERIFICATION_CODE_MATCH_PATTERN.match(value):
            raise ValidationError("Code should contain exactly 4 digits")
        return value

    class Meta:
        model = UserAccount
        fields = (
            "tg_id",
            "phone_number",
            "tg_nickname",
            "registration_time",
            "verification_code",
        )


class UserShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ("id", "tg_id", "phone_number", "tg_nickname")


class UserAddToRedisSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        max_length=12,
        error_messages={"max_length": "Phone number should contain exactly 12 symbols"},
    )

    def validate_phone_number(self, value):
        return _validate_phone_number(value)

    class Meta:
        model = UserAccount
        fields = ("tg_id", "phone_number", "tg_nickname")
