from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_read_root_returns_200(client):
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Hello World!"}


def test_create_user_returns_201(client):
    response = client.post(
        "/users",
        json={
            "username": "test",
            "email": "test@test.com",
            "password": "test",
        },
    )

    assert response.status_code == HTTPStatus.CREATED


def test_username_already_exist(client, user):
    response = client.post(
        "/users",
        json={
            "username": user.username,
            "email": user.email,
            "password": user.clean_password,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_email_already_exist(client, user):
    response = client.post(
        "/users",
        json={
            "username": "test2",
            "email": user.email,
            "password": user.clean_password,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_get_users(client):
    response = client.get("/users")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": []}


def test_get_user_created(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get("/users")

    assert response.json() == {"users": [user_schema]}


def test_update_user(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.put(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={**user_schema, "password": user.clean_password},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_update_user_not_found(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.put(
        "/users/2",
        headers={"Authorization": f"Bearer {token}"},
        json={**user_schema, "password": "123"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_user_not_found(client, user):
    response = client.put(
        "/users/2",
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
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.json() == {"message": "User deleted successfully"}


def test_user_deleted_not_found(client, user):
    response = client.delete("/users/2")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_get_token(client, user):
    response = client.post(
        "/token",
        data={"username": user.email, "password": user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token["token_type"] == "Bearer"
    assert token["access_token"]


def test_get_token_unauthorized(client, user):
    response = client.post(
        "/token",
        data={"username": "test", "password": "test"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_update_integrity_error(client, user, token):
    user_data = {
        "username": "bily",
        "email": "bily@example.com",
        "password": "bily",
    }
    client.post("/users", json=user_data)

    user_data["email"] = "bily@teste.com"
    response = client.put(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=user_data,
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"detail": "Username or Email already exists"}
