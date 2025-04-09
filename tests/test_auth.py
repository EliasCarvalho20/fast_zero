from http import HTTPStatus

from freezegun import freeze_time

route = "/auth"


def test_get_token(client, user):
    response = client.post(
        f"{route}/token",
        data={"username": user.email, "password": user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token["token_type"] == "Bearer"
    assert token["access_token"]


def test_get_token_unauthorized(client, user):
    response = client.post(
        f"{route}/token",
        data={"username": "test", "password": "test"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_refresh_token(client, user):
    with freeze_time("2025-01-01 00:00:00"):
        response = client.post(
            f"{route}/token",
            data={"username": user.email, "password": user.clean_password},
        )

    assert response.status_code == HTTPStatus.OK
    token = response.json()

    with freeze_time("2025-01-07 23:59:00"):
        response = client.post(
            f"{route}/refresh_token",
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

    assert response.status_code == HTTPStatus.OK
    assert token["access_token"] != response.json()["access_token"]


def test_token_expired(client, user):
    with freeze_time("2025-01-01 00:00:00"):
        response = client.post(
            f"{route}/token",
            data={"username": user.email, "password": user.clean_password},
        )

    assert response.status_code == HTTPStatus.OK
    token = response.json()

    with freeze_time("2025-01-08 00:00:00"):
        response = client.delete(
            "/users/1",
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_token_expired_dont_refresh(client, user):
    with freeze_time("2025-01-01 00:00:00"):
        response = client.post(
            f"{route}/token",
            data={"username": user.email, "password": user.clean_password},
        )

    assert response.status_code == HTTPStatus.OK
    token = response.json()

    with freeze_time("2025-01-08 00:00:00"):
        response = client.post(
            f"{route}/refresh_token",
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
