from http import HTTPStatus

from fastapi.testclient import TestClient

from src.estoque_ai.app import app


def test_root():
    client = TestClient(app)

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello World!'}
