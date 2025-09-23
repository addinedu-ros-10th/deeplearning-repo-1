import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.adapters.http.ws_router import router as ws_router


def create_test_app():
    app = FastAPI()
    app.include_router(ws_router)
    return app


@pytest.fixture
def client():
    return TestClient(create_test_app())


def test_ws_connect(client):
    with client.websocket_connect("/ws?user_id=00000000-0000-0000-0000-000000000000") as ws:
        ws.send_text("ping")
        # server ignores; connection stays open
        assert ws is not None


