from fastapi.testclient import TestClient

from bahai_api import __version__
from bahai_api.main import API_PREFIX, API_VERSION, CAPABILITIES, app

client = TestClient(app)


def test_discovery_returns_service_identity() -> None:
    response = client.get(API_PREFIX)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "bahai-api"
    assert body["version"] == __version__
    assert body["api_version"] == API_VERSION


def test_discovery_advertises_all_capabilities() -> None:
    body = client.get(API_PREFIX).json()

    assert set(body["capabilities"]) == set(CAPABILITIES)
    assert "search" in body["capabilities"]


def test_discovery_capability_set_matches_endpoint_set() -> None:
    body = client.get(API_PREFIX).json()

    assert set(body["capabilities"]) == set(body["endpoints"]), (
        "capabilities list and endpoints map must stay aligned"
    )


def test_discovery_endpoint_paths_share_api_prefix() -> None:
    endpoints = client.get(API_PREFIX).json()["endpoints"]

    for capability, path in endpoints.items():
        assert path == f"{API_PREFIX}/{capability}"


def test_discovery_response_is_published_in_openapi_schema() -> None:
    schema = client.get("/openapi.json").json()

    assert "DiscoveryResponse" in schema["components"]["schemas"], (
        "discovery endpoint must publish a typed schema so generated "
        "clients can rely on the response shape"
    )
