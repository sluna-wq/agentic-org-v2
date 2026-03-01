import sys
import os

# Ensure the pipeline directory is on sys.path so `api` can be imported directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api import app  # noqa: F401 — re-exported for test modules

import pytest
from starlette.testclient import TestClient


@pytest.fixture()
def client():
    """Return a fresh TestClient for each test, with a clean in-memory store."""
    # Reset in-memory storage between tests so tests are independent.
    import api as _api
    _api._debates.clear()
    _api._arguments.clear()

    with TestClient(app) as c:
        yield c
