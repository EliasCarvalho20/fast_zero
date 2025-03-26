from http import HTTPStatus

route = "/auth/token"


def test_get_token(client, user):
    response = client.post(
        route,
        data={"username": user.email, "password": user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token["token_type"] == "Bearer"
    assert token["access_token"]


def test_get_token_unauthorized(client, user):
    response = client.post(
        route,
        data={"username": "test", "password": "test"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
