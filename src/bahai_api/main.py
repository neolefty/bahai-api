from fastapi import FastAPI

from bahai_api import __version__

API_VERSION = "v1"

app = FastAPI(title="bahai-api", version=__version__)


@app.get("/api/v1")
def discovery() -> dict[str, object]:
    return {
        "name": "bahai-api",
        "version": __version__,
        "api_version": API_VERSION,
        "capabilities": [
            "texts",
            "search",
            "passages",
            "subscriptions",
            "compilations",
        ],
        "endpoints": {
            "texts": "/api/v1/texts",
            "search": "/api/v1/search",
            "passages": "/api/v1/passages",
            "subscriptions": "/api/v1/subscriptions",
            "compilations": "/api/v1/compilations",
        },
    }
