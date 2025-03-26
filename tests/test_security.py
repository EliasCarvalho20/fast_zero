from http import HTTPStatus

from jwt import decode

from fast_zero.security import (
    ALGORITHM,
    SECRET_KEY,
    create_acess_token,
)


def test_jwt_decode():
    data = {"sub": "test@test.com"}
    token = create_acess_token(data)

    decoded = decode(token, SECRET_KEY, algorithms=ALGORITHM)

    assert decoded["sub"] == data["sub"]
    assert decoded["exp"]


def test_jwt_invalid(client):
    response = client.delete(
        "/users/1",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials."}


def test_invalid_user(client):
    data = {"sub": ""}
    token = create_acess_token(data)

    response = client.delete(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials."}


def test_invalid_user_data(client):
    token = create_acess_token({})
    response = client.delete(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials."}
