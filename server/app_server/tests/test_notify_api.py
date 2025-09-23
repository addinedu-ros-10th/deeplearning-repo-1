import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.adapters.http.notify_queue_router import router as queue_router
from app.adapters.http.notify_delivery_router import router as delivery_router


def create_test_app():
    app = FastAPI(title="Notify API Test")
    app.include_router(queue_router)
    app.include_router(delivery_router)
    return app


@pytest.fixture
def client():
    return TestClient(create_test_app())


def test_routes_exist(client):
    routes = [r.path for r in client.app.routes]
    assert "/api/v1/notify/queue" in routes
    assert any(p.startswith("/api/v1/notify/deliveries/") and p.endswith("/read") for p in routes)
    assert any(p.startswith("/api/v1/notify/deliveries/") and p.endswith("/ack") for p in routes)


