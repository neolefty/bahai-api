from fastapi import FastAPI
from pydantic import BaseModel, Field

from bahai_api import __version__

API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

CAPABILITIES: tuple[str, ...] = (
    "texts",
    "search",
    "passages",
    "subscriptions",
    "compilations",
)


class DiscoveryResponse(BaseModel):
    """Service-discovery payload returned at the API root.

    Stable shape: clients depend on it to locate capabilities without
    hard-coding paths.
    """

    name: str = Field(description="Service identifier.")
    version: str = Field(description="Implementation version (semver).")
    api_version: str = Field(description="Wire-protocol version. Bumped only on breaking changes.")
    capabilities: list[str] = Field(description="Capability names advertised by this service.")
    endpoints: dict[str, str] = Field(description="Map from capability name to its base URL path.")


class HealthResponse(BaseModel):
    """Liveness probe payload. Lives outside `API_PREFIX` so probes are
    stable across wire-protocol version bumps."""

    status: str = Field(description="Liveness status. `ok` when the process is up.")


app = FastAPI(title="bahai-api", version=__version__)


@app.get(API_PREFIX, response_model=DiscoveryResponse)
def discovery() -> DiscoveryResponse:
    return DiscoveryResponse(
        name="bahai-api",
        version=__version__,
        api_version=API_VERSION,
        capabilities=list(CAPABILITIES),
        endpoints={cap: f"{API_PREFIX}/{cap}" for cap in CAPABILITIES},
    )


@app.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok")
