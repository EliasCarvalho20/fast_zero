from http import HTTPStatus

from fast_zero.schemas import UserPublic

route = "/users"


def test_create_user_returns_201(client):
    response = client.post(
        route,
        json={
            "username": "test",
            "email": "test@test.com",
            "password": "test",
        },
    )

    assert response.status_code == HTTPStatus.CREATED


def test_username_already_exist(client, user):
    response = client.post(
        route,
        json={
            "username": user.username,
            "email": user.email,
            "password": user.clean_password,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_email_already_exist(client, user):
    response = client.post(
        route,
        json={
            "username": "test2",
            "email": user.email,
            "password": user.clean_password,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_get_users(client):
    response = client.get(route)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": []}


def test_get_user_created(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(route)

    assert response.json() == {"users": [user_schema]}


def test_update_user(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.put(
        f"{route}/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={**user_schema, "password": user.clean_password},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_update_without_permission(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.put(
        f"{route}/2",
        headers={"Authorization": f"Bearer {token}"},
        json={**user_schema, "password": "123"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permission"}


def test_user_not_found(client, user):
    response = client.put(
        f"{route}/2",
        json={
            "id": "2",
            "username": "123",
            "email": "test@test.com",
            "password": "123",
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_user_deleted(client, user, token):
    response = client.delete(
        f"{route}/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.json() == {"message": "User deleted successfully"}


def test_delete_without_permission(client, user, token):
    response = client.delete(
        f"{route}/2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permission"}


def test_user_deleted_not_found(client, user):
    response = client.delete(f"{route}/2")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_update_integrity_error(client, user, token):
    user_data = {
        "username": "bily",
        "email": "bily@example.com",
        "password": "bily",
    }
    client.post(route, json=user_data)

    user_data["email"] = "bily@teste.com"
    response = client.put(
        f"{route}/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=user_data,
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"detail": "Username or Email already exists"}
