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
            "username": "teste",
            "email": "teste@teste.com",
            "password": "teste",
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_email_already_exist(client, user):
    response = client.post(
        "/users",
        json={
            "username": "teste2",
            "email": "teste@teste.com",
            "password": "teste",
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


def test_update_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.put("/users/1", json={**user_schema, "password": "123"})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_update_user_not_found(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.put("/users/2", json={**user_schema, "password": "123"})

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

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found"}


def test_user_deleted(client, user):
    response = client.delete("/users/1")

    assert response.json() == {"message": "User deleted successfully"}


def test_user_deleted_not_found(client, user):
    response = client.delete("/users/2")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found"}
