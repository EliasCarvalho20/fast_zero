from dataclasses import asdict
from http import HTTPStatus
from typing import Any

import pytest

from tests.factories import TodoFactory

route = "/todos"


def create_todos_factory(
    user_id: int,
    n_factories: int = 1,
    **kwargs: Any,
):
    return TodoFactory.create_batch(n_factories, user_id=user_id, **kwargs)


def test_create_todo(client, user, token):
    todo = {
        "title": "test",
        "description": "test",
        "state": "draft",
    }
    response = client.post(
        f"{route}", headers={"Authorization": f"Bearer {token}"}, json=todo
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"id": 1, "user_id": user.id, **todo}


@pytest.mark.asyncio
async def test_get_todo_nonexistent(client, session, todo, token):
    response = client.get(
        f"{route}/{5}",
        headers={"Authorization": f"Bearer {token}"},
        params={"title": "test"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_todos_content_are_identical(client, session, user, token):
    n_factories = 5
    todo = create_todos_factory(
        user_id=user.id,
        n_factories=n_factories,
    )
    session.add_all(todo)

    response = client.get(
        route,
        headers={"Authorization": f"Bearer {token}"},
    )
    created_todos = response.json()["todos"]

    assert response.status_code == HTTPStatus.OK
    assert len(created_todos) == n_factories
    assert created_todos == [asdict(t) for t in todo]


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(client, session, user, token):
    n_factories = 5
    session.add_all(create_todos_factory(user_id=user.id, n_factories=5))

    response = client.get(
        route,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["todos"]) == n_factories


@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2_todos(
    client, session, user, token
):
    session.add_all(create_todos_factory(user_id=user.id, n_factories=5))

    response = client.get(
        route,
        headers={"Authorization": f"Bearer {token}"},
        params={"limit": 2, "offset": 1},
    )

    expected = 2
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["todos"]) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filter_name, filter_value",
    [
        ("title", "test"),
        ("description", "lorem ipsun"),
        ("state", "done"),
    ],
)
async def test_todos_filters(
    client,
    session,
    user,
    token,
    filter_name,
    filter_value,
):
    n_factories = 5
    if filter_name == "state":
        todo = create_todos_factory(
            user_id=user.id, n_factories=n_factories, state=filter_value
        )
    elif filter_name == "title":
        todo = create_todos_factory(
            user_id=user.id, n_factories=n_factories, title=filter_value
        )
    elif filter_name == "description":
        todo = create_todos_factory(
            user_id=user.id, n_factories=n_factories, description=filter_value
        )

    session.add_all(todo)
    session.add_all(
        create_todos_factory(user_id=user.id, n_factories=2, state="draft")
    )

    response = client.get(
        route,
        headers={"Authorization": f"Bearer {token}"},
        params={filter_name: filter_value},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["todos"]) == n_factories


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filter_name, filter_value",
    [
        ("title", "updated"),
        ("description", "updated"),
        ("state", "doing"),
    ],
)
async def test_update_todo(client, todo, token, filter_name, filter_value):
    response = client.patch(
        f"{route}/{todo['id']}",
        headers={"Authorization": f"Bearer {token}"},
        params={filter_name: filter_value},
    )
    assert response.status_code == HTTPStatus.OK

    response = client.get(
        f"{route}/{todo['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK

    updated_todo = response.json()
    assert updated_todo[filter_name] == filter_value


@pytest.mark.asyncio
async def test_update_todo_nonexistent(client, token):
    response = client.patch(
        f"{route}/{5}",
        headers={"Authorization": f"Bearer {token}"},
        params={"title": "test"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_delete_todo(client, todo, token):
    response = client.delete(
        f"{route}/{todo['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_delete_todo_nonexistent(client, token):
    response = client.delete(
        f"{route}/{10}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_filter_combined(client, session, user, token):
    n_factories = 5
    session.add_all(
        create_todos_factory(
            user_id=user.id,
            n_factories=n_factories,
            title="title",
            description="description",
        )
    )
    session.add_all(
        create_todos_factory(
            user_id=user.id,
            n_factories=2,
            title="something",
            description="something",
        )
    )

    response = client.get(
        route,
        headers={"Authorization": f"Bearer {token}"},
        params={"title": "title", "description": "description"},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["todos"]) == n_factories
