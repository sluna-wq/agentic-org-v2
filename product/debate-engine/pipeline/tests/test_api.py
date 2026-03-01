# ============================================================
# API CONTRACT ASSUMED BY THESE TESTS
# Source: product/debate-engine/pipeline/schema.md (Agent A)
# Confirmed against: product/debate-engine/pipeline/api.py (Agent B)
# Pipeline role: Agent C — test author
#
# Base URL: /api/v1
# Content-Type: application/json
#
# Endpoints:
#   1. POST   /api/v1/debates
#        Request:  { "topic": str, "description": str }
#        Response: 201  { "id": uuid-str, "topic": str, "description": str, "created_at": iso8601-str }
#
#   2. GET    /api/v1/debates
#        Response: 200  { "debates": [ <Debate>, ... ] }
#        Ordered by created_at descending; empty list when no debates exist.
#
#   3. GET    /api/v1/debates/{debate_id}
#        Response: 200  <Debate>
#        Response: 404  { "error": "Debate not found" }
#
#   4. POST   /api/v1/debates/{debate_id}/arguments
#        Request:  { "side": "for"|"against", "content": str }
#        Response: 201  { "id": uuid-str, "debate_id": uuid-str, "side": str, "content": str, "created_at": iso8601-str }
#        Response: 404  { "error": "Debate not found" }
#
#   5. GET    /api/v1/debates/{debate_id}/arguments
#        Response: 200  { "arguments": [ <Argument>, ... ] }
#        Optional query param: ?side=for|against
#        Ordered by created_at ascending; 404 if debate does not exist.
#
# Error envelope for all 4xx: { "error": "string" }
# All ids are server-generated UUIDs. All created_at are server-generated ISO 8601 UTC.
# ============================================================

import re

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
ISO8601_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_debate(client, topic="Test topic", description="Test description"):
    r = client.post("/api/v1/debates", json={"topic": topic, "description": description})
    assert r.status_code == 201
    return r.json()


def _add_argument(client, debate_id, side="for", content="An argument"):
    r = client.post(
        f"/api/v1/debates/{debate_id}/arguments",
        json={"side": side, "content": content},
    )
    assert r.status_code == 201
    return r.json()


# ---------------------------------------------------------------------------
# 1. Create a debate — 201 + response body shape
# ---------------------------------------------------------------------------

class TestCreateDebate:
    def test_returns_201(self, client):
        r = client.post(
            "/api/v1/debates",
            json={"topic": "AI judges", "description": "Should AI replace judges?"},
        )
        assert r.status_code == 201

    def test_response_body_shape(self, client):
        r = client.post(
            "/api/v1/debates",
            json={"topic": "AI judges", "description": "Should AI replace judges?"},
        )
        body = r.json()
        assert "id" in body
        assert "topic" in body
        assert "description" in body
        assert "created_at" in body

    def test_id_is_uuid(self, client):
        debate = _create_debate(client)
        assert UUID_RE.match(debate["id"]), f"id {debate['id']!r} is not a UUID"

    def test_created_at_is_iso8601(self, client):
        debate = _create_debate(client)
        assert ISO8601_RE.match(debate["created_at"]), (
            f"created_at {debate['created_at']!r} is not ISO 8601 UTC"
        )

    def test_fields_echo_request_values(self, client):
        debate = _create_debate(client, topic="Climate change", description="A hot topic")
        assert debate["topic"] == "Climate change"
        assert debate["description"] == "A hot topic"

    def test_missing_topic_returns_422(self, client):
        r = client.post("/api/v1/debates", json={"description": "No topic"})
        assert r.status_code == 422

    def test_missing_description_returns_422(self, client):
        r = client.post("/api/v1/debates", json={"topic": "No description"})
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# 2. List debates — 200 + list structure
# ---------------------------------------------------------------------------

class TestListDebates:
    def test_returns_200(self, client):
        r = client.get("/api/v1/debates")
        assert r.status_code == 200

    def test_response_has_debates_key(self, client):
        r = client.get("/api/v1/debates")
        body = r.json()
        assert "debates" in body

    def test_empty_when_none_exist(self, client):
        r = client.get("/api/v1/debates")
        assert r.json()["debates"] == []

    def test_contains_created_debates(self, client):
        _create_debate(client, topic="First")
        _create_debate(client, topic="Second")
        debates = client.get("/api/v1/debates").json()["debates"]
        topics = [d["topic"] for d in debates]
        assert "First" in topics
        assert "Second" in topics

    def test_each_item_has_required_fields(self, client):
        _create_debate(client)
        debates = client.get("/api/v1/debates").json()["debates"]
        assert len(debates) == 1
        d = debates[0]
        for field in ("id", "topic", "description", "created_at"):
            assert field in d, f"field {field!r} missing from list item"


# ---------------------------------------------------------------------------
# 3. Get a single debate by ID — 200
# ---------------------------------------------------------------------------

class TestGetDebate:
    def test_returns_200_for_existing(self, client):
        debate = _create_debate(client)
        r = client.get(f"/api/v1/debates/{debate['id']}")
        assert r.status_code == 200

    def test_body_matches_created_debate(self, client):
        debate = _create_debate(client, topic="Solo topic", description="Solo desc")
        r = client.get(f"/api/v1/debates/{debate['id']}")
        body = r.json()
        assert body["id"] == debate["id"]
        assert body["topic"] == "Solo topic"
        assert body["description"] == "Solo desc"

    def test_body_shape(self, client):
        debate = _create_debate(client)
        body = client.get(f"/api/v1/debates/{debate['id']}").json()
        for field in ("id", "topic", "description", "created_at"):
            assert field in body


# ---------------------------------------------------------------------------
# 4. Get a non-existent debate by ID — 404
# ---------------------------------------------------------------------------

class TestGetDebateNotFound:
    def test_returns_404_for_unknown_id(self, client):
        r = client.get("/api/v1/debates/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404

    def test_404_body_has_error_key(self, client):
        r = client.get("/api/v1/debates/00000000-0000-0000-0000-000000000000")
        body = r.json()
        assert "error" in body
        assert isinstance(body["error"], str)


# ---------------------------------------------------------------------------
# 5. Add an argument to a debate — 201 + response body shape
# ---------------------------------------------------------------------------

class TestAddArgument:
    def test_returns_201(self, client):
        debate = _create_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "for", "content": "Good point"},
        )
        assert r.status_code == 201

    def test_response_body_shape(self, client):
        debate = _create_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "against", "content": "Counter point"},
        )
        body = r.json()
        for field in ("id", "debate_id", "side", "content", "created_at"):
            assert field in body, f"field {field!r} missing from argument response"

    def test_id_is_uuid(self, client):
        debate = _create_debate(client)
        arg = _add_argument(client, debate["id"])
        assert UUID_RE.match(arg["id"]), f"id {arg['id']!r} is not a UUID"

    def test_debate_id_matches(self, client):
        debate = _create_debate(client)
        arg = _add_argument(client, debate["id"])
        assert arg["debate_id"] == debate["id"]

    def test_side_for_echoed(self, client):
        debate = _create_debate(client)
        arg = _add_argument(client, debate["id"], side="for", content="Pro argument")
        assert arg["side"] == "for"
        assert arg["content"] == "Pro argument"

    def test_side_against_echoed(self, client):
        debate = _create_debate(client)
        arg = _add_argument(client, debate["id"], side="against", content="Con argument")
        assert arg["side"] == "against"

    def test_invalid_side_returns_422(self, client):
        debate = _create_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "maybe", "content": "Indecisive"},
        )
        assert r.status_code == 422

    def test_unknown_debate_returns_404(self, client):
        r = client.post(
            "/api/v1/debates/00000000-0000-0000-0000-000000000000/arguments",
            json={"side": "for", "content": "Orphan"},
        )
        assert r.status_code == 404
        assert "error" in r.json()


# ---------------------------------------------------------------------------
# 6. List arguments for a debate — 200 + list structure
# ---------------------------------------------------------------------------

class TestListArguments:
    def test_returns_200(self, client):
        debate = _create_debate(client)
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments")
        assert r.status_code == 200

    def test_response_has_arguments_key(self, client):
        debate = _create_debate(client)
        body = client.get(f"/api/v1/debates/{debate['id']}/arguments").json()
        assert "arguments" in body

    def test_empty_when_no_arguments(self, client):
        debate = _create_debate(client)
        body = client.get(f"/api/v1/debates/{debate['id']}/arguments").json()
        assert body["arguments"] == []

    def test_contains_added_arguments(self, client):
        debate = _create_debate(client)
        _add_argument(client, debate["id"], side="for", content="Pro")
        _add_argument(client, debate["id"], side="against", content="Con")
        args = client.get(f"/api/v1/debates/{debate['id']}/arguments").json()["arguments"]
        assert len(args) == 2

    def test_each_item_has_required_fields(self, client):
        debate = _create_debate(client)
        _add_argument(client, debate["id"])
        args = client.get(f"/api/v1/debates/{debate['id']}/arguments").json()["arguments"]
        assert len(args) == 1
        for field in ("id", "debate_id", "side", "content", "created_at"):
            assert field in args[0], f"field {field!r} missing from argument list item"

    def test_side_filter_for(self, client):
        debate = _create_debate(client)
        _add_argument(client, debate["id"], side="for", content="Pro")
        _add_argument(client, debate["id"], side="against", content="Con")
        args = client.get(
            f"/api/v1/debates/{debate['id']}/arguments?side=for"
        ).json()["arguments"]
        assert len(args) == 1
        assert args[0]["side"] == "for"

    def test_side_filter_against(self, client):
        debate = _create_debate(client)
        _add_argument(client, debate["id"], side="for", content="Pro")
        _add_argument(client, debate["id"], side="against", content="Con")
        args = client.get(
            f"/api/v1/debates/{debate['id']}/arguments?side=against"
        ).json()["arguments"]
        assert len(args) == 1
        assert args[0]["side"] == "against"

    def test_unknown_debate_returns_404(self, client):
        r = client.get("/api/v1/debates/00000000-0000-0000-0000-000000000000/arguments")
        assert r.status_code == 404
        assert "error" in r.json()
