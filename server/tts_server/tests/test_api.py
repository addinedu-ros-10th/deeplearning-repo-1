import pytest
from fastapi.testclient import TestClient
from tts_server.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_tts_bad_request(client):
    r = client.get("/api/tts", params={"text": ""})
    assert r.status_code in (400, 422)


