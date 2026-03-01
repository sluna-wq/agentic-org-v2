"""
test_api.py — Adversarial contract tests for Agent B's Debate Engine API.

=============================================================================
ASSUMED API CONTRACT  (source: product/debate-engine/adversarial/schema.md)
=============================================================================

Endpoints:
  POST   /api/v1/debates                          → 201 / 422
  GET    /api/v1/debates                          → 200  (bare array)
  GET    /api/v1/debates/{debate_id}              → 200 / 404
  POST   /api/v1/debates/{debate_id}/arguments    → 201 / 404 / 422
  GET    /api/v1/debates/{debate_id}/arguments    → 200 / 404 / 422

Debate object fields (exactly):    id, title, description, created_at
Argument object fields (exactly):  id, debate_id, side, body, created_at

List responses are bare JSON arrays — NOT {"debates": [...]} or {"arguments": [...]}.

Status codes:
  - 201 on successful POST (not 200)
  - 200 on successful GET
  - 404 when debate_id does not exist
  - 422 when body or query-param fails validation

422 body shape: {"error": "string"} — NO "detail" key (FastAPI default is non-compliant)

?side= filter (GET arguments):
  - ?side=for    → only "for" arguments
  - ?side=against → only "against" arguments
  - absent       → all arguments
  - invalid value → 422 BEFORE checking debate existence (note 17)

Debate existence vs body validation precedence (note 19–20):
  - POST arguments with missing debate + invalid body → 404, not 422

Input sanitisation (note 23–24):
  - Leading/trailing whitespace stripped before storage and length check
  - "  " (spaces only) fails min-length → 422

Server-generated fields (notes 5–6):
  - id and created_at always assigned by server; client-supplied values ignored

=============================================================================
"""

import re
import uuid

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
_ISO8601_UTC_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$"
)

_DEBATE_PAYLOAD = {
    "title": "Pineapple belongs on pizza",
    "description": "A debate on the merits of pineapple as a pizza topping.",
}

_ARGUMENT_FOR_PAYLOAD = {
    "side": "for",
    "body": "Pineapple adds a sweet contrast.",
}

_ARGUMENT_AGAINST_PAYLOAD = {
    "side": "against",
    "body": "Fruit has no place on a savoury dish.",
}


def _create_debate(client, payload=None):
    """Helper: create a debate and return the JSON body."""
    r = client.post("/api/v1/debates", json=payload or _DEBATE_PAYLOAD)
    assert r.status_code == 201, f"expected 201, got {r.status_code}: {r.text}"
    return r.json()


def _create_argument(client, debate_id, payload=None):
    """Helper: add an argument to debate_id and return the JSON body."""
    r = client.post(
        f"/api/v1/debates/{debate_id}/arguments",
        json=payload or _ARGUMENT_FOR_PAYLOAD,
    )
    assert r.status_code == 201, f"expected 201, got {r.status_code}: {r.text}"
    return r.json()


# ===========================================================================
# 1. Create Debate — POST /api/v1/debates
# ===========================================================================


class TestCreateDebate:
    def test_returns_201_not_200(self, client):
        """Schema note 25: POST must return 201, not 200."""
        r = client.post("/api/v1/debates", json=_DEBATE_PAYLOAD)
        assert r.status_code == 201

    def test_response_contains_exact_debate_fields(self, client):
        """Schema notes 1, 26: exactly {id, title, description, created_at}."""
        body = _create_debate(client)
        assert "id" in body
        assert "title" in body
        assert "description" in body
        assert "created_at" in body

    def test_response_has_no_extra_fields(self, client):
        """Schema note 1: no extras (e.g. no 'topic', 'text', 'timestamp')."""
        body = _create_debate(client)
        assert set(body.keys()) == {"id", "title", "description", "created_at"}

    def test_id_is_uuid4_string(self, client):
        """Schema note 3: id is a string in UUID v4 format."""
        body = _create_debate(client)
        assert isinstance(body["id"], str)
        assert _UUID4_RE.match(body["id"]), f"id not UUID v4: {body['id']}"

    def test_created_at_is_iso8601_utc(self, client):
        """Schema note 4: created_at is YYYY-MM-DDTHH:MM:SS.ffffffZ."""
        body = _create_debate(client)
        assert isinstance(body["created_at"], str)
        assert _ISO8601_UTC_RE.match(body["created_at"]), (
            f"created_at format wrong: {body['created_at']}"
        )

    def test_title_and_description_stored_correctly(self, client):
        """Schema: title and description are echoed back after stripping."""
        body = _create_debate(client, {"title": "Tabs vs spaces", "description": "Classic debate."})
        assert body["title"] == "Tabs vs spaces"
        assert body["description"] == "Classic debate."

    def test_whitespace_stripped_from_title(self, client):
        """Schema note 23: leading/trailing whitespace stripped before storage."""
        body = _create_debate(client, {"title": "  Tabs vs spaces  ", "description": "Desc."})
        assert body["title"] == "Tabs vs spaces"

    def test_whitespace_stripped_from_description(self, client):
        """Schema note 23: leading/trailing whitespace stripped from description."""
        body = _create_debate(client, {"title": "Title", "description": "  Some description.  "})
        assert body["description"] == "Some description."

    def test_spaces_only_title_returns_422(self, client):
        """Schema note 23-24: '  ' strips to '' which fails min-length → 422."""
        r = client.post("/api/v1/debates", json={"title": "   ", "description": "Valid."})
        assert r.status_code == 422

    def test_422_envelope_has_error_key_not_detail(self, client):
        """Schema note 21: 422 body must be {"error": "..."}, not {"detail": [...]}."""
        r = client.post("/api/v1/debates", json={"title": "   ", "description": "Valid."})
        assert r.status_code == 422
        body = r.json()
        assert "error" in body, f"missing 'error' key: {body}"
        assert "detail" not in body, f"forbidden 'detail' key present: {body}"

    def test_422_error_value_is_nonempty_string(self, client):
        """Schema note 22: error must be a non-empty string."""
        r = client.post("/api/v1/debates", json={"title": "   ", "description": "Valid."})
        body = r.json()
        assert isinstance(body["error"], str)
        assert len(body["error"]) > 0

    def test_missing_title_returns_422(self, client):
        """Required field absent → 422."""
        r = client.post("/api/v1/debates", json={"description": "No title."})
        assert r.status_code == 422
        body = r.json()
        assert "error" in body
        assert "detail" not in body

    def test_missing_description_returns_422(self, client):
        """Required field absent → 422."""
        r = client.post("/api/v1/debates", json={"title": "No description."})
        assert r.status_code == 422
        body = r.json()
        assert "error" in body
        assert "detail" not in body

    def test_client_supplied_id_is_ignored(self, client):
        """Schema note 5: server ignores client-supplied id."""
        client_id = str(uuid.uuid4())
        body = _create_debate(
            client, {"title": "T", "description": "D", "id": client_id}
        )
        assert body["id"] != client_id, "server must not reflect client-supplied id"
        assert _UUID4_RE.match(body["id"]), "id must still be a valid UUID v4"

    def test_client_supplied_created_at_is_ignored(self, client):
        """Schema note 6: server ignores client-supplied created_at."""
        fake_ts = "2000-01-01T00:00:00.000000Z"
        body = _create_debate(
            client, {"title": "T", "description": "D", "created_at": fake_ts}
        )
        assert body["created_at"] != fake_ts, "server must not reflect client-supplied created_at"


# ===========================================================================
# 2. List Debates — GET /api/v1/debates
# ===========================================================================


class TestListDebates:
    def test_returns_200(self, client):
        r = client.get("/api/v1/debates")
        assert r.status_code == 200

    def test_empty_store_returns_bare_empty_array(self, client):
        """Schema: empty array [], NOT {"debates": []}."""
        r = client.get("/api/v1/debates")
        body = r.json()
        assert isinstance(body, list), f"expected list, got {type(body)}: {body}"
        assert len(body) == 0

    def test_response_is_bare_array_not_wrapped_object(self, client):
        """Schema dimension 2: envelope must be [...], not {"debates": [...]}."""
        _create_debate(client)
        r = client.get("/api/v1/debates")
        body = r.json()
        assert isinstance(body, list), (
            f"expected bare array, got {type(body).__name__}: {body}"
        )
        assert "debates" not in body if isinstance(body, dict) else True

    def test_debates_contain_all_required_fields(self, client):
        """Schema note 26: complete objects — id, title, description, created_at."""
        _create_debate(client)
        r = client.get("/api/v1/debates")
        body = r.json()
        assert len(body) == 1
        debate = body[0]
        assert "id" in debate
        assert "title" in debate
        assert "description" in debate
        assert "created_at" in debate

    def test_debates_have_no_extra_fields(self, client):
        """Schema note 1: exactly four fields per debate object."""
        _create_debate(client)
        r = client.get("/api/v1/debates")
        debate = r.json()[0]
        assert set(debate.keys()) == {"id", "title", "description", "created_at"}

    def test_multiple_debates_all_returned(self, client):
        _create_debate(client, {"title": "A", "description": "d1"})
        _create_debate(client, {"title": "B", "description": "d2"})
        r = client.get("/api/v1/debates")
        assert len(r.json()) == 2

    def test_ordering_is_created_at_ascending(self, client):
        """Schema note 10: oldest first."""
        d1 = _create_debate(client, {"title": "First", "description": "d"})
        d2 = _create_debate(client, {"title": "Second", "description": "d"})
        r = client.get("/api/v1/debates")
        ids = [d["id"] for d in r.json()]
        assert ids[0] == d1["id"], "oldest debate must appear first"
        assert ids[1] == d2["id"]


# ===========================================================================
# 3. Get Debate — GET /api/v1/debates/{debate_id}
# ===========================================================================


class TestGetDebate:
    def test_returns_200_for_existing_debate(self, client):
        created = _create_debate(client)
        r = client.get(f"/api/v1/debates/{created['id']}")
        assert r.status_code == 200

    def test_response_contains_all_debate_fields(self, client):
        """Schema note 26: no partial responses."""
        created = _create_debate(client)
        r = client.get(f"/api/v1/debates/{created['id']}")
        body = r.json()
        assert "id" in body
        assert "title" in body
        assert "description" in body
        assert "created_at" in body

    def test_response_has_no_extra_fields(self, client):
        created = _create_debate(client)
        r = client.get(f"/api/v1/debates/{created['id']}")
        body = r.json()
        assert set(body.keys()) == {"id", "title", "description", "created_at"}

    def test_returned_id_matches_requested_id(self, client):
        created = _create_debate(client)
        r = client.get(f"/api/v1/debates/{created['id']}")
        assert r.json()["id"] == created["id"]


# ===========================================================================
# 4. 404 on Missing Debate
# ===========================================================================


class TestMissingDebate:
    def test_get_debate_404_for_unknown_id(self, client):
        """Schema: 404 when debate_id does not exist."""
        r = client.get(f"/api/v1/debates/{uuid.uuid4()}")
        assert r.status_code == 404

    def test_get_debate_404_body_has_error_key(self, client):
        """Schema note 21: {"error": "..."} shape, no "detail"."""
        r = client.get(f"/api/v1/debates/{uuid.uuid4()}")
        body = r.json()
        assert "error" in body, f"missing 'error' key: {body}"
        assert "detail" not in body, f"forbidden 'detail' key: {body}"

    def test_get_debate_404_error_is_nonempty_string(self, client):
        r = client.get(f"/api/v1/debates/{uuid.uuid4()}")
        body = r.json()
        assert isinstance(body["error"], str)
        assert len(body["error"]) > 0

    def test_post_arguments_404_for_unknown_debate(self, client):
        r = client.post(
            f"/api/v1/debates/{uuid.uuid4()}/arguments",
            json=_ARGUMENT_FOR_PAYLOAD,
        )
        assert r.status_code == 404

    def test_get_arguments_404_for_unknown_debate(self, client):
        r = client.get(f"/api/v1/debates/{uuid.uuid4()}/arguments")
        assert r.status_code == 404

    def test_404_takes_precedence_over_422_on_post_arguments(self, client):
        """Schema notes 19-20: missing debate + invalid body → 404, not 422."""
        r = client.post(
            f"/api/v1/debates/{uuid.uuid4()}/arguments",
            json={"side": "INVALID_SIDE", "body": ""},
        )
        assert r.status_code == 404, (
            f"expected 404 (debate missing takes precedence), got {r.status_code}"
        )


# ===========================================================================
# 5. Add Argument — POST /api/v1/debates/{debate_id}/arguments
# ===========================================================================


class TestAddArgument:
    def test_returns_201_not_200(self, client):
        """Schema note 25: POST must return 201."""
        debate = _create_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json=_ARGUMENT_FOR_PAYLOAD,
        )
        assert r.status_code == 201

    def test_response_contains_all_argument_fields(self, client):
        """Schema notes 2, 26: exactly {id, debate_id, side, body, created_at}."""
        debate = _create_debate(client)
        body = _create_argument(client, debate["id"])
        assert "id" in body
        assert "debate_id" in body
        assert "side" in body
        assert "body" in body
        assert "created_at" in body

    def test_response_has_no_extra_fields(self, client):
        """Schema note 2: no extras (e.g. no 'position', 'text', 'content')."""
        debate = _create_debate(client)
        body = _create_argument(client, debate["id"])
        assert set(body.keys()) == {"id", "debate_id", "side", "body", "created_at"}

    def test_debate_id_in_response_matches_path(self, client):
        """Schema note 7: debate_id set from path, not from request body."""
        debate = _create_debate(client)
        body = _create_argument(client, debate["id"])
        assert body["debate_id"] == debate["id"]

    def test_side_for_stored_correctly(self, client):
        debate = _create_debate(client)
        body = _create_argument(client, debate["id"], {"side": "for", "body": "Pro arg."})
        assert body["side"] == "for"

    def test_side_against_stored_correctly(self, client):
        debate = _create_debate(client)
        body = _create_argument(
            client, debate["id"], {"side": "against", "body": "Con arg."}
        )
        assert body["side"] == "against"

    def test_id_is_uuid4_string(self, client):
        """Schema note 3: id is a UUID v4 string."""
        debate = _create_debate(client)
        body = _create_argument(client, debate["id"])
        assert isinstance(body["id"], str)
        assert _UUID4_RE.match(body["id"]), f"id not UUID v4: {body['id']}"

    def test_created_at_is_iso8601_utc(self, client):
        """Schema note 4: created_at is YYYY-MM-DDTHH:MM:SS.ffffffZ."""
        debate = _create_debate(client)
        body = _create_argument(client, debate["id"])
        assert _ISO8601_UTC_RE.match(body["created_at"]), (
            f"created_at format wrong: {body['created_at']}"
        )

    def test_invalid_side_returns_422(self, client):
        """Schema notes 8-9: only 'for' and 'against' accepted (case-sensitive)."""
        debate = _create_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "For", "body": "Capitalised."},
        )
        assert r.status_code == 422

    def test_invalid_side_pro_returns_422(self, client):
        """Schema note 9: 'pro' is not a valid side value."""
        debate = _create_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "pro", "body": "Pro arg."},
        )
        assert r.status_code == 422

    def test_422_argument_envelope_has_error_not_detail(self, client):
        """Schema note 21: 422 body must be {"error": "..."}, not {"detail": [...]}."""
        debate = _create_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "INVALID", "body": "Body."},
        )
        assert r.status_code == 422
        body = r.json()
        assert "error" in body, f"missing 'error' key: {body}"
        assert "detail" not in body, f"forbidden 'detail' key: {body}"

    def test_whitespace_stripped_from_body(self, client):
        """Schema note 23: leading/trailing whitespace stripped from body."""
        debate = _create_debate(client)
        body = _create_argument(
            client, debate["id"], {"side": "for", "body": "  Trimmed.  "}
        )
        assert body["body"] == "Trimmed."

    def test_spaces_only_body_returns_422(self, client):
        """Schema note 23-24: whitespace-only body → 422 after stripping."""
        debate = _create_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "for", "body": "    "},
        )
        assert r.status_code == 422

    def test_client_supplied_debate_id_in_body_is_ignored(self, client):
        """Schema note 7: debate_id always set from path, ignores body value."""
        debate = _create_debate(client)
        fake_id = str(uuid.uuid4())
        body = _create_argument(
            client, debate["id"], {"side": "for", "body": "Arg.", "debate_id": fake_id}
        )
        assert body["debate_id"] == debate["id"], (
            "debate_id must come from path, not request body"
        )


# ===========================================================================
# 6. List Arguments — GET /api/v1/debates/{debate_id}/arguments
# ===========================================================================


class TestListArguments:
    def test_returns_200_for_existing_debate(self, client):
        debate = _create_debate(client)
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments")
        assert r.status_code == 200

    def test_response_is_bare_array_not_wrapped(self, client):
        """Schema dimension 2: bare array [...], NOT {"arguments": [...]}."""
        debate = _create_debate(client)
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments")
        body = r.json()
        assert isinstance(body, list), (
            f"expected bare array, got {type(body).__name__}: {body}"
        )

    def test_empty_when_no_arguments(self, client):
        """Schema: empty array [] when no arguments exist."""
        debate = _create_debate(client)
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments")
        assert r.json() == []

    def test_arguments_contain_all_required_fields(self, client):
        """Schema notes 2, 26: each argument has id, debate_id, side, body, created_at."""
        debate = _create_debate(client)
        _create_argument(client, debate["id"])
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments")
        body = r.json()
        assert len(body) == 1
        arg = body[0]
        assert "id" in arg
        assert "debate_id" in arg
        assert "side" in arg
        assert "body" in arg
        assert "created_at" in arg

    def test_arguments_have_no_extra_fields(self, client):
        """Schema note 2: exactly five fields per argument object."""
        debate = _create_debate(client)
        _create_argument(client, debate["id"])
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments")
        arg = r.json()[0]
        assert set(arg.keys()) == {"id", "debate_id", "side", "body", "created_at"}

    def test_all_argument_debate_ids_match_path(self, client):
        """Schema: every returned argument's debate_id must equal path debate_id."""
        debate = _create_debate(client)
        _create_argument(client, debate["id"], {"side": "for", "body": "F."})
        _create_argument(client, debate["id"], {"side": "against", "body": "A."})
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments")
        for arg in r.json():
            assert arg["debate_id"] == debate["id"]

    def test_ordering_is_created_at_ascending(self, client):
        """Schema note 11: arguments ordered oldest first."""
        debate = _create_debate(client)
        a1 = _create_argument(client, debate["id"], {"side": "for", "body": "First."})
        a2 = _create_argument(client, debate["id"], {"side": "against", "body": "Second."})
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments")
        ids = [a["id"] for a in r.json()]
        assert ids[0] == a1["id"], "oldest argument must appear first"
        assert ids[1] == a2["id"]

    def test_side_filter_for_returns_only_for(self, client):
        """Schema notes 13-14: ?side=for filters to 'for' arguments only."""
        debate = _create_debate(client)
        _create_argument(client, debate["id"], {"side": "for", "body": "Pro."})
        _create_argument(client, debate["id"], {"side": "against", "body": "Con."})
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments?side=for")
        body = r.json()
        assert len(body) == 1, f"expected 1 argument, got {len(body)}"
        assert body[0]["side"] == "for"

    def test_side_filter_against_returns_only_against(self, client):
        """Schema note 15: ?side=against filters to 'against' arguments only."""
        debate = _create_debate(client)
        _create_argument(client, debate["id"], {"side": "for", "body": "Pro."})
        _create_argument(client, debate["id"], {"side": "against", "body": "Con."})
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments?side=against")
        body = r.json()
        assert len(body) == 1, f"expected 1 argument, got {len(body)}"
        assert body[0]["side"] == "against"

    def test_no_side_filter_returns_all_arguments(self, client):
        """Schema note 16: absent ?side= returns all arguments."""
        debate = _create_debate(client)
        _create_argument(client, debate["id"], {"side": "for", "body": "Pro."})
        _create_argument(client, debate["id"], {"side": "against", "body": "Con."})
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments")
        assert len(r.json()) == 2

    def test_side_filter_with_no_matches_returns_empty_array(self, client):
        """Schema: empty array when ?side= filter matches nothing."""
        debate = _create_debate(client)
        _create_argument(client, debate["id"], {"side": "for", "body": "Pro."})
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments?side=against")
        body = r.json()
        assert isinstance(body, list)
        assert len(body) == 0

    def test_invalid_side_filter_returns_422(self, client):
        """Schema note 17: invalid ?side= value → 422."""
        debate = _create_debate(client)
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments?side=pro")
        assert r.status_code == 422

    def test_invalid_side_filter_422_envelope(self, client):
        """Schema note 21: 422 body must be {"error": "..."}, not {"detail": [...]}."""
        debate = _create_debate(client)
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments?side=For")
        assert r.status_code == 422
        body = r.json()
        assert "error" in body, f"missing 'error' key: {body}"
        assert "detail" not in body, f"forbidden 'detail' key: {body}"

    def test_invalid_side_filter_422_before_404_for_missing_debate(self, client):
        """Schema note 17: invalid ?side= → 422 even when debate doesn't exist."""
        r = client.get(
            f"/api/v1/debates/{uuid.uuid4()}/arguments?side=INVALID"
        )
        assert r.status_code == 422, (
            "invalid ?side= must return 422 before checking debate existence"
        )

    def test_unrecognised_query_params_silently_ignored(self, client):
        """Schema note 18: unknown query params do not cause 422."""
        debate = _create_debate(client)
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments?foo=bar&baz=qux")
        assert r.status_code == 200
