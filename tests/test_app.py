from http import HTTPStatus


def test_read_root_returns_200(client):
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Hello World!"}
