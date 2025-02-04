from fastapi.testclient import TestClient
from http import HTTPStatus

from fast_zero.app import app


def test_read_root_returns_200():
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Hello World!"}
