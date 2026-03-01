"""
conftest.py — imports the real app from product/debate-engine/adversarial/api.py.

Adds the adversarial package directory to sys.path so that `import api` resolves
to the Agent B implementation under review.
"""

import os
import sys

# Make `import api` resolve to product/debate-engine/adversarial/api.py
_ADVERSARIAL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ADVERSARIAL_DIR not in sys.path:
    sys.path.insert(0, _ADVERSARIAL_DIR)

import pytest
from fastapi.testclient import TestClient

import api as _api_module
from api import app


@pytest.fixture
def client():
    """Fresh TestClient with cleared in-memory storage for every test."""
    _api_module._debates.clear()
    _api_module._arguments.clear()
    with TestClient(app) as c:
        yield c
