import logging

from django.db.utils import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from redis import Redis
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.main._actions import (
    is_verified_code_and_registration_time,
    send_code_via_call,
)
from src.main.redis_init import get_redis
from src.main.serializers import (
    UserAddToRedisSerializer,
    UserCreateSerializer,
    UserShowSerializer,
)
from src.main.user_dal import UserDbDal, UserRedisDAL
from src.main.utils import get_additional_properties, get_openapi_response_with_one_key

logger = logging.getLogger(__name__)


class CreateUserView(APIView):
    @swagger_auto_schema(
        request_body=UserCreateSerializer,
        responses={
            201: UserShowSerializer,
            400: get_openapi_response_with_one_key(
                key="detail", description="Wrong verification code OR code has expired"
            ),
            409: get_additional_properties("Unique constraint violation"),
            422: get_additional_properties("Serializer errors"),
            503: get_openapi_response_with_one_key(
                key="detail", description="Database error"
            ),
        },
    )
    def post(self, request, redis_client: Redis = get_redis()):
        is_verified_code_and_reg_time = is_verified_code_and_registration_time(
            request, redis_client
        )
        if is_verified_code_and_reg_time is True:
            user_db_dal = UserDbDal()
            try:
                user_db_dal.create_user(
                    tg_id=request.data["tg_id"],
                    phone_number=request.data["phone_number"],
                    tg_nickname=request.data["tg_nickname"],
                )
                user_by_tg_id = user_db_dal.get_user_by_tg_id(request.data["tg_id"])
                new_user_serializer = UserShowSerializer(instance=user_by_tg_id)
                return Response(
                    status=status.HTTP_201_CREATED,
                    data=new_user_serializer.data,
                )

            except IntegrityError as err:
                logger.error(err)
                return Response(
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                    data={"detail": f"Database error: {err}"},
                )

        else:
            return is_verified_code_and_reg_time


class SendCodeView(APIView):
    @swagger_auto_schema(
        request_body=UserAddToRedisSerializer,
        responses={
            200: get_openapi_response_with_one_key(
                key="code", description="Verification code"
            ),
            422: get_additional_properties("Serializer errors"),
            503: get_openapi_response_with_one_key(
                key="detail", description="Sending code service error"
            ),
        },
    )
    def post(self, request, redis_client: Redis = get_redis()):
        user_add_to_redis_serializer = UserAddToRedisSerializer(data=request.data)
        if user_add_to_redis_serializer.is_valid():
            valid_data = user_add_to_redis_serializer.validated_data
            verification_code = send_code_via_call(valid_data)
            user_redis_dal = UserRedisDAL(redis_client)
            user_redis_dal.create_user(
                tg_id=valid_data["tg_id"],  # type: ignore
                phone_number=valid_data["phone_number"],  # type: ignore
                tg_nickname=valid_data["tg_nickname"],  # type: ignore
                verification_code=verification_code,  # type: ignore
            )
            return Response(status=status.HTTP_200_OK, data={"code": verification_code})
        else:
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                data=user_add_to_redis_serializer.errors,
            )
