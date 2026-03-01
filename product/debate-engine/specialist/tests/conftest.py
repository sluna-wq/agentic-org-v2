"""
Pytest configuration for the Debate Engine contract test suite.

Imports the real FastAPI app from product/debate-engine/specialist/api.py
and provides fixtures for a test client with clean in-memory state per test.
"""

import os
import sys

import pytest

# Add the specialist directory to the path so api.py can be imported directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import api as debate_api  # noqa: E402
from api import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture
def client():
    """
    HTTP test client with isolated in-memory state for each test.

    Clears _debates and _arguments before yielding the client so tests
    do not share state regardless of execution order.
    """
    debate_api._debates.clear()
    debate_api._arguments.clear()
    with TestClient(app) as c:
        yield c
