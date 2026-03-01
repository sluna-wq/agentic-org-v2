"""
=============================================================================
API CONTRACT — Agent C (tests) independent invention
=============================================================================

This comment block is the research measurement artifact for the BROADCAST
topology experiment. It documents the API contract that Agent C independently
invented while writing these tests, without reading any other agent's files.

DEBATES
-------
Create a debate
  Method : POST
  Path   : /debates
  Request: {"title": "<string>", "description": "<string (optional)>"}
  200 → 201
  Body   : {
      "id":          "<uuid string>",
      "title":       "<string>",
      "description": "<string>",
      "created_at":  "<ISO-8601 datetime string>"
  }

List debates
  Method : GET
  Path   : /debates
  Status : 200
  Body   : [<debate object>, ...]   (array, may be empty)

Get a debate by ID
  Method : GET
  Path   : /debates/{debate_id}
  Status : 200
  Body   : <debate object>

Get a non-existent debate
  Method : GET
  Path   : /debates/{debate_id}
  Status : 404

ARGUMENTS
---------
Add an argument to a debate
  Method : POST
  Path   : /debates/{debate_id}/arguments
  Request: {"content": "<string>", "position": "for" | "against"}
  Status : 201
  Body   : {
      "id":         "<uuid string>",
      "debate_id":  "<uuid string>",
      "content":    "<string>",
      "position":   "for" | "against",
      "created_at": "<ISO-8601 datetime string>"
  }

List arguments for a debate
  Method : GET
  Path   : /debates/{debate_id}/arguments
  Status : 200
  Body   : [<argument object>, ...]   (array, may be empty)

=============================================================================
"""

import pytest
from starlette.testclient import TestClient  # noqa: F401 — imported via conftest


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _create_debate(client: TestClient, title: str = "AI vs Humans", description: str = "") -> dict:
    resp = client.post("/debates", json={"title": title, "description": description})
    assert resp.status_code == 201
    return resp.json()


def _add_argument(client: TestClient, debate_id: str, content: str, position: str = "for") -> dict:
    resp = client.post(
        f"/debates/{debate_id}/arguments",
        json={"content": content, "position": position},
    )
    assert resp.status_code == 201
    return resp.json()


# ---------------------------------------------------------------------------
# Debate tests
# ---------------------------------------------------------------------------


class TestCreateDebate:
    def test_returns_201(self, client: TestClient):
        resp = client.post("/debates", json={"title": "Space exploration funding"})
        assert resp.status_code == 201

    def test_response_body_has_required_fields(self, client: TestClient):
        resp = client.post(
            "/debates",
            json={"title": "Universal Basic Income", "description": "Should governments implement UBI?"},
        )
        body = resp.json()
        assert "id" in body
        assert body["title"] == "Universal Basic Income"
        assert body["description"] == "Should governments implement UBI?"
        assert "created_at" in body

    def test_id_is_a_non_empty_string(self, client: TestClient):
        body = _create_debate(client)
        assert isinstance(body["id"], str)
        assert len(body["id"]) > 0

    def test_created_at_is_a_string(self, client: TestClient):
        body = _create_debate(client)
        assert isinstance(body["created_at"], str)

    def test_title_only_request_accepted(self, client: TestClient):
        resp = client.post("/debates", json={"title": "Climate change action"})
        assert resp.status_code == 201


class TestListDebates:
    def test_empty_list_when_no_debates(self, client: TestClient):
        resp = client.get("/debates")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_200(self, client: TestClient):
        resp = client.get("/debates")
        assert resp.status_code == 200

    def test_returns_list_structure(self, client: TestClient):
        _create_debate(client, title="Net neutrality")
        _create_debate(client, title="Renewable energy subsidies")

        resp = client.get("/debates")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_each_item_has_required_fields(self, client: TestClient):
        _create_debate(client, title="Open-source software in government")

        debates = client.get("/debates").json()
        assert len(debates) == 1
        debate = debates[0]
        assert "id" in debate
        assert "title" in debate
        assert "created_at" in debate


class TestGetDebate:
    def test_returns_200_for_existing_debate(self, client: TestClient):
        created = _create_debate(client)
        resp = client.get(f"/debates/{created['id']}")
        assert resp.status_code == 200

    def test_response_matches_created_debate(self, client: TestClient):
        created = _create_debate(client, title="Drug legalisation", description="Pros and cons")
        resp = client.get(f"/debates/{created['id']}")
        body = resp.json()
        assert body["id"] == created["id"]
        assert body["title"] == created["title"]
        assert body["description"] == created["description"]

    def test_returns_404_for_missing_debate(self, client: TestClient):
        resp = client.get("/debates/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    def test_404_body_is_not_a_debate(self, client: TestClient):
        resp = client.get("/debates/nonexistent-id")
        assert resp.status_code == 404
        body = resp.json()
        # Should not look like a debate — no "title" key
        assert "title" not in body


# ---------------------------------------------------------------------------
# Argument tests
# ---------------------------------------------------------------------------


class TestAddArgument:
    def test_returns_201(self, client: TestClient):
        debate = _create_debate(client)
        resp = client.post(
            f"/debates/{debate['id']}/arguments",
            json={"content": "It creates jobs", "position": "for"},
        )
        assert resp.status_code == 201

    def test_response_body_has_required_fields(self, client: TestClient):
        debate = _create_debate(client)
        resp = client.post(
            f"/debates/{debate['id']}/arguments",
            json={"content": "It is too expensive", "position": "against"},
        )
        body = resp.json()
        assert "id" in body
        assert "debate_id" in body
        assert body["content"] == "It is too expensive"
        assert body["position"] == "against"
        assert "created_at" in body

    def test_debate_id_in_argument_matches_parent(self, client: TestClient):
        debate = _create_debate(client)
        arg = _add_argument(client, debate["id"], "Strong argument here")
        assert arg["debate_id"] == debate["id"]

    def test_for_position_accepted(self, client: TestClient):
        debate = _create_debate(client)
        arg = _add_argument(client, debate["id"], "Supports the motion", position="for")
        assert arg["position"] == "for"

    def test_against_position_accepted(self, client: TestClient):
        debate = _create_debate(client)
        arg = _add_argument(client, debate["id"], "Opposes the motion", position="against")
        assert arg["position"] == "against"

    def test_argument_on_missing_debate_returns_404(self, client: TestClient):
        resp = client.post(
            "/debates/00000000-0000-0000-0000-000000000000/arguments",
            json={"content": "Lost argument", "position": "for"},
        )
        assert resp.status_code == 404


class TestListArguments:
    def test_returns_200(self, client: TestClient):
        debate = _create_debate(client)
        resp = client.get(f"/debates/{debate['id']}/arguments")
        assert resp.status_code == 200

    def test_empty_list_when_no_arguments(self, client: TestClient):
        debate = _create_debate(client)
        resp = client.get(f"/debates/{debate['id']}/arguments")
        assert resp.json() == []

    def test_returns_list_structure(self, client: TestClient):
        debate = _create_debate(client)
        _add_argument(client, debate["id"], "First point", position="for")
        _add_argument(client, debate["id"], "Counterpoint", position="against")

        resp = client.get(f"/debates/{debate['id']}/arguments")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_each_argument_has_required_fields(self, client: TestClient):
        debate = _create_debate(client)
        _add_argument(client, debate["id"], "Evidence A", position="for")

        args = client.get(f"/debates/{debate['id']}/arguments").json()
        assert len(args) == 1
        arg = args[0]
        assert "id" in arg
        assert "debate_id" in arg
        assert "content" in arg
        assert "position" in arg

    def test_arguments_are_isolated_per_debate(self, client: TestClient):
        debate1 = _create_debate(client, title="Debate One")
        debate2 = _create_debate(client, title="Debate Two")

        _add_argument(client, debate1["id"], "Only in debate 1", position="for")

        args1 = client.get(f"/debates/{debate1['id']}/arguments").json()
        args2 = client.get(f"/debates/{debate2['id']}/arguments").json()

        assert len(args1) == 1
        assert len(args2) == 0
