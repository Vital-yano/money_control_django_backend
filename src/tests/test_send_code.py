import pytest


@pytest.mark.django_db
def test_send_code(client, get_user_from_redis):
    user_data = {
        "tg_id": "88005553535",
        "phone_number": "+79991234567",
        "tg_nickname": "pogchamp",
    }
    response = client.post("/api/v1/user/send_code", data=user_data)
    assert response.status_code == 200
    data_from_resp = response.json()
    redis_user_data = get_user_from_redis(user_data["tg_id"])
    assert data_from_resp["code"] == "1234"
    assert user_data["tg_id"] == redis_user_data["tg_id"]
    assert user_data["phone_number"] == redis_user_data["phone_number"]
    assert user_data["tg_nickname"] == redis_user_data["tg_nickname"]
    assert data_from_resp["code"] == redis_user_data["verification_code"]


@pytest.mark.django_db
def test_send_code_to_incorrect_phone_number(client):
    user_data = {
        "tg_id": "88005553535",
        "phone_number": "+799912343344567",
        "tg_nickname": "pogchamp",
    }
    response = client.post("/api/v1/user/send_code", data=user_data)
    assert response.json() == {
        "phone_number": ["Phone number should contain exactly 12 symbols"]
    }
