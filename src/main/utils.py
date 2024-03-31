import logging
from typing import Protocol

import requests
from drf_yasg import openapi
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class SendCodeProtocol(Protocol):
    def send_code(self) -> str | Response:
        ...


class SendCodeViaCallProtocol(SendCodeProtocol):
    def __init__(self, url: str, test: bool = False):
        self.url = url
        self.test = test

    def send_code(self) -> str | Response:
        if self.test:
            return "1234"
        response = requests.get(self.url)
        if response.json().get("status", None) == "OK":
            return str(response.json()["code"])
        else:
            logger.error("Send code service error.")
            return Response(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                data={
                    "detail": "Проблемы с сервисом отправки смс. Попробуйте зарегистрироваться позже"
                },
            )


def get_openapi_response_with_one_key(key: str, description: str) -> openapi.Response:
    openapi_response = openapi.Response(
        description=description,
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                key: openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    return openapi_response


def get_additional_properties(msg: str) -> openapi.Response:
    return openapi.Response(
        description=msg,
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            additional_properties=openapi.Schema(type=openapi.TYPE_STRING),
        ),
    )
