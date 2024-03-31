from datetime import datetime

from django.conf import settings
from redis import Redis
from rest_framework import status
from rest_framework.response import Response

from src.main.serializers import (
    UserCreateSerializer,
)
from src.main.user_dal import UserRedisDAL
from src.main.utils import SendCodeViaCallProtocol


def is_verified_code_and_registration_time(request, redis_client: Redis):
    user_redis_dal = UserRedisDAL(redis_client)
    user_create_serializer = UserCreateSerializer(data=request.data)
    if user_create_serializer.is_valid():
        valid_data = user_create_serializer.validated_data
        redis_user = user_redis_dal.get_user(valid_data["tg_id"])  # type: ignore
        expire_at = datetime.strptime(redis_user["expire_at"], "%Y-%m-%d %H:%M:%S")

        if valid_data["verification_code"] != redis_user["verification_code"]:  # type: ignore
            return Response(
                {"detail": " Wrong verification code"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if valid_data["registration_time"] > expire_at:  # type: ignore
            return Response(
                {"detail": "The code has expired. Request new code"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return True
    else:
        # Если все ошибки связаны только с уникальностью полей
        if all(
            [
                err_detail[0].code == "unique"
                for err_detail in user_create_serializer.errors.values()  # type: ignore
            ]
        ):
            return Response(
                user_create_serializer.errors,
                status=status.HTTP_409_CONFLICT,
            )
        else:
            return Response(
                user_create_serializer.errors,
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )


def send_code_via_call(body):
    # Получение кода не происходит при прохождении тестов,
    # в settings_test не определена переменная SMS_API_ID

    sms_api_id = getattr(settings, "SMS_API_ID", None)
    get_call_url = f"https://sms.ru/code/call?api_id={sms_api_id}&phone={body['phone_number'][1:]}&ip=-1"
    send_code_via_call_instance = SendCodeViaCallProtocol(
        get_call_url, settings.TEST_RUNNING
    )
    verification_code = send_code_via_call_instance.send_code()
    return verification_code
