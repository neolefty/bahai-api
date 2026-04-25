from fastapi.testclient import TestClient

from bahai_api import __version__
from bahai_api.main import app

client = TestClient(app)


def test_discovery_root_returns_version_and_capabilities() -> None:
    response = client.get("/api/v1")

    assert response.status_code == 200
    body = response.json()
    assert body["version"] == __version__
    assert body["api_version"] == "v1"
    assert isinstance(body["capabilities"], list)
    assert "search" in body["capabilities"]


def test_discovery_root_lists_endpoints() -> None:
    response = client.get("/api/v1")

    endpoints = response.json()["endpoints"]
    assert endpoints["search"] == "/api/v1/search"
    assert endpoints["passages"] == "/api/v1/passages"
