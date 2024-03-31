import uuid
from datetime import UTC, datetime, timedelta

import pytest
from django.conf import settings


@pytest.mark.django_db
def test_create_user(client, get_user_from_database, add_user_to_redis):
    user_data = {
        "tg_id": "88005553535",
        "phone_number": "+79991234567",
        "tg_nickname": "pogchamp",
        "verification_code": "1234",
        "registration_time": datetime.strftime(datetime.now(UTC), "%Y-%m-%d %H:%M:%S"),
    }
    add_user_to_redis(
        user_data["tg_id"],
        user_data["phone_number"],
        user_data["tg_nickname"],
        user_data["verification_code"],
    )
    response = client.post(path="/api/v1/user/create", data=user_data)
    assert response.status_code == 201
    data_from_resp = response.json()
    assert data_from_resp["tg_id"] == user_data["tg_id"]
    assert data_from_resp["phone_number"] == user_data["phone_number"]
    assert data_from_resp["tg_nickname"] == user_data["tg_nickname"]
    user_from_db = get_user_from_database(data_from_resp["tg_id"])
    assert user_from_db.tg_id == user_data["tg_id"]
    assert user_from_db.phone_number == user_data["phone_number"]
    assert user_from_db.tg_nickname == user_data["tg_nickname"]
    assert user_from_db.tg_id == data_from_resp["tg_id"]


@pytest.mark.django_db
def test_create_user_with_the_same_tg_id(
    client, create_user_in_database, get_user_from_database, add_user_to_redis
):
    user_data = {
        "id": uuid.uuid4(),
        "tg_id": "88005553535",
        "phone_number": "+79991234567",
        "tg_nickname": "pogchamp",
    }
    user_data_with_the_same_tg_id = {
        "tg_id": "88005553535",
        "phone_number": "+71234567890",
        "tg_nickname": "pogchamp2",
        "verification_code": "1234",
        "registration_time": datetime.strftime(datetime.now(UTC), "%Y-%m-%d %H:%M:%S"),
    }
    create_user_in_database(
        user_data["id"],
        user_data["tg_id"],
        user_data["phone_number"],
        user_data["tg_nickname"],
    )
    user_from_db = get_user_from_database(user_data["tg_id"])
    assert user_from_db.tg_id == user_data["tg_id"]
    assert user_from_db.phone_number == user_data["phone_number"]
    assert user_from_db.tg_nickname == user_data["tg_nickname"]
    add_user_to_redis(
        user_data_with_the_same_tg_id["tg_id"],
        user_data_with_the_same_tg_id["phone_number"],
        user_data_with_the_same_tg_id["tg_nickname"],
        user_data_with_the_same_tg_id["verification_code"],
    )
    response = client.post("/api/v1/user/create", data=user_data_with_the_same_tg_id)
    assert response.status_code == 409

    assert response.json() == {
        "tg_id": ["user account with this tg id already exists."]
    }


@pytest.mark.django_db
def test_create_user_with_the_same_phone_number(
    client, create_user_in_database, get_user_from_database, add_user_to_redis
):
    user_data = {
        "id": uuid.uuid4(),
        "tg_id": "88005553535",
        "phone_number": "+79991234567",
        "tg_nickname": "pogchamp",
    }
    user_data_with_the_same_phone_number = {
        "tg_id": "2323909093",
        "phone_number": "+79991234567",
        "tg_nickname": "pogchamp2",
        "verification_code": "1234",
        "registration_time": datetime.strftime(datetime.now(UTC), "%Y-%m-%d %H:%M:%S"),
    }
    create_user_in_database(
        user_data["id"],
        user_data["tg_id"],
        user_data["phone_number"],
        user_data["tg_nickname"],
    )
    user_from_db = get_user_from_database(user_data["tg_id"])
    assert user_from_db.tg_id == user_data["tg_id"]
    assert user_from_db.phone_number == user_data["phone_number"]
    assert user_from_db.tg_nickname == user_data["tg_nickname"]
    add_user_to_redis(
        user_data_with_the_same_phone_number["tg_id"],
        user_data_with_the_same_phone_number["phone_number"],
        user_data_with_the_same_phone_number["tg_nickname"],
        user_data_with_the_same_phone_number["verification_code"],
    )
    response = client.post(
        "/api/v1/user/create", data=user_data_with_the_same_phone_number
    )
    assert response.status_code == 409
    assert response.json() == {"phone_number": ["This field must be unique."]}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_data_for_creation, expected_status_code, expected_detail",
    [
        (
            {},
            422,
            {
                "tg_id": ["This field is required."],
                "phone_number": ["This field is required."],
                "tg_nickname": ["This field is required."],
                "registration_time": ["This field is required."],
                "verification_code": ["This field is required."],
            },
        ),
        (
            {
                "tg_id": "88005553535",
                "phone_number": "9232453434",
                "tg_nickname": "pogchamp",
                "verification_code": "1234",
                "registration_time": datetime.strftime(
                    datetime.now(UTC), "%Y-%m-%d %H:%M:%S"
                ),
            },
            422,
            {
                "phone_number": [
                    "Phone number should start with +7 and contain only digits after that"
                ],
            },
        ),
        (
            {
                "tg_id": "88005553535",
                "phone_number": "+7880055535353232",
                "tg_nickname": "pogchamp",
                "verification_code": "1234",
                "registration_time": datetime.strftime(
                    datetime.now(UTC), "%Y-%m-%d %H:%M:%S"
                ),
            },
            422,
            {
                "phone_number": ["Phone number should contain exactly 12 symbols"],
            },
        ),
    ],
)
def test_create_user_validation_error(
    client, user_data_for_creation, expected_status_code, expected_detail
):
    response = client.post("/api/v1/user/create", data=user_data_for_creation)
    data_from_resp = response.json()
    assert response.status_code == expected_status_code
    assert data_from_resp == expected_detail


@pytest.mark.django_db
def test_create_user_with_wrong_verification_code(client, add_user_to_redis):
    user_data = {
        "tg_id": "88005553535",
        "phone_number": "+79991234567",
        "tg_nickname": "pogchamp",
        "verification_code": "4321",
        "registration_time": datetime.strftime(datetime.now(UTC), "%Y-%m-%d %H:%M:%S"),
    }
    add_user_to_redis(
        user_data["tg_id"], user_data["phone_number"], user_data["tg_nickname"], "1234"
    )
    response = client.post("/api/v1/user/create", data=user_data)
    assert response.status_code == 422
    assert "Wrong verification code" in response.json()["detail"]


@pytest.mark.django_db
def test_create_user_with_expired_code(client, add_user_to_redis):
    user_data = {
        "tg_id": "88005553535",
        "phone_number": "+79991234567",
        "tg_nickname": "pogchamp",
        "verification_code": "1234",
        "registration_time": datetime.strftime(
            datetime.now(UTC)
            + settings.USER_REGISTRATION_TIMEDELTA
            + timedelta(minutes=1),
            "%Y-%m-%d %H:%M:%S",
        ),
    }
    add_user_to_redis(
        user_data["tg_id"], user_data["phone_number"], user_data["tg_nickname"], "1234"
    )
    response = client.post("/api/v1/user/create", data=user_data)
    assert response.status_code == 422
    assert "The code has expired. Request new code" in response.json()["detail"]
