from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from bahai_api.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    # Function-scope: TestClient is cheap, and a fresh client per test
    # avoids order-dependent coupling once tests start mutating state.
    with TestClient(app) as test_client:
        yield test_client
