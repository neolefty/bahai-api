from fastapi.testclient import TestClient

from bahai_api.main import API_PREFIX


def test_healthz_returns_ok(client: TestClient) -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_healthz_lives_outside_api_prefix(client: TestClient) -> None:
    # Probes (compose, k8s, load balancers) should not chase wire-protocol
    # version bumps when API_PREFIX changes.
    assert not "/healthz".startswith(API_PREFIX)


def test_healthz_response_is_published_in_openapi_schema(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    assert "HealthResponse" in schema["components"]["schemas"], (
        "healthz must publish a typed schema so probes and clients can rely on the response shape"
    )
    assert "/healthz" in schema["paths"]
