"""
Contract Test Suite — Debate Engine API

Tests are written against the schema contract in:
  product/debate-engine/specialist/schema.md

Every test is designed to be maximally sensitive to contract violations.
Each test docstring states exactly what deviation it would catch.

A failing test means the implementation deviates from the contract.

==========================================================================
ASSUMED API CONTRACT
==========================================================================

Base URL: /api/v1

DEBATE OBJECT
  Required fields : id, title, description, argument_count, created_at
  id              : UUID v4 string (lowercase hex with hyphens)
  argument_count  : integer; server-computed; always equals total arg count
                    for the debate (unfiltered by side)
  created_at      : ISO 8601 UTC string (must end with "Z")
  description     : string; defaults to "" when omitted (never null/None)

ARGUMENT OBJECT
  Required fields : id, debate_id, side, body, created_at
  side            : exactly "for" or "against" — case-sensitive
  debate_id       : set from URL path parameter; never from request body

ENDPOINTS
  POST /api/v1/debates                       -> 201  (Debate object, dict)
  GET  /api/v1/debates                       -> 200  {"debates": [...], "total": N}
  GET  /api/v1/debates/{id}                  -> 200  (Debate) | 404
  POST /api/v1/debates/{id}/arguments        -> 201  (Argument, dict) | 404 | 422
  GET  /api/v1/debates/{id}/arguments        -> 200  {"arguments": [...], "total": N}
                                                | 404 | 422 (invalid ?side=)

ERROR ENVELOPES
  404  : {"error": "Debate not found"}
         key must be "error" (not "detail", "message", or anything else)

  422  : FastAPI native format —
         {"detail": [{"loc": [...], "msg": "...", "type": "..."}]}
         key must be "detail" containing a list of structured error objects
         (NOT {"error": "..."} — that is the 404 shape, not the 422 shape)

ORDERING
  GET /debates              : created_at DESC (newest debate first)
  GET .../arguments         : created_at ASC  (oldest argument first)

SIDE FILTER (?side=)
  Omitted                   : return all arguments for the debate
  "for"                     : return only "for" arguments
  "against"                 : return only "against" arguments
  Any other value           : 422  (case-sensitive: "For", "FOR" are invalid)

STRING CONSTRAINTS
  title       : 1–200 chars   (empty string and >200 chars are invalid)
  description : 0–1000 chars  (empty string is valid; defaults to "")
  body        : 1–2000 chars  (empty string and >2000 chars are invalid)

==========================================================================
"""

import re
import time

import pytest

# ---------------------------------------------------------------------------
# Contract constants
# ---------------------------------------------------------------------------

DEBATE_FIELDS = {"id", "title", "description", "argument_count", "created_at"}
ARGUMENT_FIELDS = {"id", "debate_id", "side", "body", "created_at"}

# ISO 8601 UTC: must contain date, time, and Z suffix (microseconds optional)
ISO8601_Z_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")

# UUID v4: version nibble = 4, variant nibble = 8, 9, a, or b
UUID_V4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

# A nonexistent but well-formed UUID used for 404 tests
MISSING_ID = "00000000-0000-4000-a000-000000000000"


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def _post_debate(client, title="Test Debate", description=None):
    """Create a debate and return the parsed response body."""
    payload = {"title": title}
    if description is not None:
        payload["description"] = description
    r = client.post("/api/v1/debates", json=payload)
    r.raise_for_status()
    return r.json()


def _post_argument(client, debate_id, side="for", body="A substantive argument."):
    """Add an argument to a debate and return the parsed response body."""
    r = client.post(
        f"/api/v1/debates/{debate_id}/arguments",
        json={"side": side, "body": body},
    )
    r.raise_for_status()
    return r.json()


# ==========================================================================
# 1. CREATE DEBATE  (POST /api/v1/debates)
# ==========================================================================


class TestCreateDebate:

    def test_status_201(self, client):
        """
        Catches: implementation returning 200 instead of 201 for resource creation.
        The contract specifies 201 Created for all successful POST /debates requests.
        """
        r = client.post("/api/v1/debates", json={"title": "Solar energy"})
        assert r.status_code == 201

    def test_response_is_dict_not_list(self, client):
        """
        Catches: single-resource endpoint wrapping the Debate in an array or
        a list envelope (e.g., {"debates": [...]}) instead of returning a bare dict.
        """
        r = client.post("/api/v1/debates", json={"title": "Solar energy"})
        assert isinstance(r.json(), dict)

    def test_field_names_exact_set(self, client):
        """
        Catches: missing required fields, extra undocumented fields, field renames
        (e.g., argumentCount instead of argument_count), or camelCase variants.
        Set equality ensures both missing AND extra fields are caught.
        """
        r = client.post("/api/v1/debates", json={"title": "Solar energy"})
        assert set(r.json().keys()) == DEBATE_FIELDS

    def test_argument_count_zero_on_creation(self, client):
        """
        Catches: server omitting argument_count, initializing it to None, or
        initializing it to a nonzero value on a brand-new debate with no arguments.
        """
        r = client.post("/api/v1/debates", json={"title": "Solar energy"})
        assert r.json()["argument_count"] == 0

    def test_argument_count_is_integer(self, client):
        """
        Catches: argument_count returned as a string, float, or null.
        The schema specifies integer type for this field.
        """
        r = client.post("/api/v1/debates", json={"title": "Solar energy"})
        assert isinstance(r.json()["argument_count"], int)

    def test_description_defaults_to_empty_string_not_null(self, client):
        """
        Catches: description returning null/None when omitted by the client.
        The schema specifies description defaults to "" (empty string), never null.
        Checking isinstance(..., str) catches null; checking == "" catches wrong default.
        """
        r = client.post("/api/v1/debates", json={"title": "No description"})
        body = r.json()
        assert isinstance(body["description"], str), "description must be a string, not null"
        assert body["description"] == ""

    def test_title_and_description_reflected_exactly(self, client):
        """
        Catches: title or description being truncated, transformed, or stripped of
        whitespace in the response. The server must echo client-supplied values verbatim.
        """
        title = "Climate change is accelerating faster than models predict"
        desc = "Focus on IPCC AR6 data and tipping points."
        r = client.post("/api/v1/debates", json={"title": title, "description": desc})
        body = r.json()
        assert body["title"] == title
        assert body["description"] == desc

    def test_id_is_uuid_v4_format(self, client):
        """
        Catches: id field using sequential integers, random hex without hyphens,
        UUID v1/v3/v5, or any non-UUID v4 format.
        """
        r = client.post("/api/v1/debates", json={"title": "Solar energy"})
        assert UUID_V4_RE.match(r.json()["id"]), (
            f"id must be UUID v4; got: {r.json()['id']!r}"
        )

    def test_created_at_is_iso8601_utc(self, client):
        """
        Catches: created_at missing the Z UTC suffix, using local time, using a
        date-only format, or using a non-ISO 8601 format.
        """
        r = client.post("/api/v1/debates", json={"title": "Solar energy"})
        assert ISO8601_Z_RE.match(r.json()["created_at"]), (
            f"created_at must be ISO 8601 UTC (Z suffix); got: {r.json()['created_at']!r}"
        )

    def test_missing_title_returns_422(self, client):
        """
        Catches: server accepting a request body that omits the required 'title' field.
        Any response other than 422 indicates the server does not enforce the contract.
        """
        r = client.post("/api/v1/debates", json={})
        assert r.status_code == 422

    def test_empty_title_returns_422(self, client):
        """
        Catches: server accepting title="" (violates min_length=1 constraint).
        An empty string is not a valid debate title per the schema.
        """
        r = client.post("/api/v1/debates", json={"title": ""})
        assert r.status_code == 422

    def test_title_at_max_length_accepted(self, client):
        """
        Catches: off-by-one in max_length=200 constraint that rejects a title of
        exactly 200 characters (the boundary value must be accepted).
        """
        r = client.post("/api/v1/debates", json={"title": "x" * 200})
        assert r.status_code == 201

    def test_title_over_max_length_returns_422(self, client):
        """
        Catches: server accepting title with 201+ characters (violates max_length=200).
        """
        r = client.post("/api/v1/debates", json={"title": "x" * 201})
        assert r.status_code == 422

    def test_description_at_max_length_accepted(self, client):
        """
        Catches: off-by-one in max_length=1000 constraint for description.
        A description of exactly 1000 characters must be accepted.
        """
        r = client.post(
            "/api/v1/debates",
            json={"title": "T", "description": "x" * 1000},
        )
        assert r.status_code == 201

    def test_description_over_max_length_returns_422(self, client):
        """
        Catches: server accepting description with 1001+ characters.
        """
        r = client.post(
            "/api/v1/debates",
            json={"title": "T", "description": "x" * 1001},
        )
        assert r.status_code == 422

    def test_422_error_envelope_uses_detail_list(self, client):
        """
        Catches: 422 response using the application-error envelope {"error": "..."}
        instead of FastAPI's native {"detail": [...]} format.

        The schema explicitly states: 'FastAPI validation errors (422) use FastAPI's
        native format.' This means the top-level key must be "detail" and its value
        must be a list of structured error objects. Returning {"error": "..."} for a
        422 is a contract violation — it collapses the validation-error envelope into
        the same shape as the application-error (404) envelope, breaking consumers
        that parse per-field validation details.
        """
        r = client.post("/api/v1/debates", json={})
        assert r.status_code == 422
        body = r.json()
        assert "detail" in body, (
            "422 must use FastAPI native envelope with 'detail' key; "
            f"got keys: {sorted(body.keys())}"
        )
        assert isinstance(body["detail"], list), (
            "'detail' must be a list of error objects"
        )
        assert len(body["detail"]) > 0, "'detail' list must be non-empty"
        error_obj = body["detail"][0]
        assert "loc" in error_obj, "each error object must have 'loc'"
        assert "msg" in error_obj, "each error object must have 'msg'"


# ==========================================================================
# 2. LIST DEBATES  (GET /api/v1/debates)
# ==========================================================================


class TestListDebates:

    def test_status_200(self, client):
        """
        Catches: wrong status code for a successful list request (e.g., 204, 201).
        """
        r = client.get("/api/v1/debates")
        assert r.status_code == 200

    def test_envelope_is_dict_not_list(self, client):
        """
        Catches: returning a bare JSON array instead of the schema-required
        {"debates": [...], "total": N} wrapper object. A bare array cannot be
        extended with metadata (total, pagination) without a breaking change.
        """
        r = client.get("/api/v1/debates")
        assert isinstance(r.json(), dict), (
            "GET /debates must return a dict envelope, not a bare JSON array"
        )

    def test_envelope_keys_exact(self, client):
        """
        Catches: missing 'debates' or 'total' keys, or extra undocumented keys
        in the list envelope. Both keys are required by the schema.
        """
        r = client.get("/api/v1/debates")
        body = r.json()
        assert "debates" in body, "envelope must contain 'debates' key"
        assert "total" in body, "envelope must contain 'total' key"

    def test_empty_list_shape(self, client):
        """
        Catches: returning null, an empty dict, or a non-empty array when no
        debates exist. The empty-state contract must be: {"debates": [], "total": 0}.
        """
        body = client.get("/api/v1/debates").json()
        assert body["debates"] == []
        assert body["total"] == 0

    def test_total_matches_list_length(self, client):
        """
        Catches: 'total' not being updated when debates are created, or 'total'
        being hardcoded to a wrong value.
        """
        _post_debate(client, "Debate A")
        _post_debate(client, "Debate B")
        body = client.get("/api/v1/debates").json()
        assert body["total"] == 2
        assert len(body["debates"]) == 2

    def test_debate_items_have_exact_fields(self, client):
        """
        Catches: list items having a different or reduced field set compared to
        the single-resource endpoint. Field consistency across representations is
        a contract requirement.
        """
        _post_debate(client, "Solar")
        body = client.get("/api/v1/debates").json()
        assert set(body["debates"][0].keys()) == DEBATE_FIELDS

    def test_ordering_newest_first(self, client):
        """
        Catches: list ordered ascending (oldest first) instead of the schema-required
        descending (newest first) ordering by created_at.
        """
        d1 = _post_debate(client, "Older debate")
        time.sleep(0.05)  # ensure distinct timestamps
        d2 = _post_debate(client, "Newer debate")
        ids = [d["id"] for d in client.get("/api/v1/debates").json()["debates"]]
        assert ids[0] == d2["id"], "newest debate must be first"
        assert ids[1] == d1["id"], "older debate must be second"

    def test_argument_count_in_list_reflects_arguments(self, client):
        """
        Catches: argument_count in the list response being stale or not reflecting
        arguments added after the debate was created.
        """
        debate = _post_debate(client, "Debate with args")
        _post_argument(client, debate["id"], side="for")
        _post_argument(client, debate["id"], side="against")
        body = client.get("/api/v1/debates").json()
        item = next(d for d in body["debates"] if d["id"] == debate["id"])
        assert item["argument_count"] == 2


# ==========================================================================
# 3. GET DEBATE  (GET /api/v1/debates/{debate_id})
# ==========================================================================


class TestGetDebate:

    def test_status_200(self, client):
        """
        Catches: wrong status code for a successful single-debate retrieval.
        """
        debate = _post_debate(client)
        r = client.get(f"/api/v1/debates/{debate['id']}")
        assert r.status_code == 200

    def test_response_is_dict_not_list(self, client):
        """
        Catches: single-resource GET returning a list or envelope instead of a
        bare Debate object.
        """
        debate = _post_debate(client)
        r = client.get(f"/api/v1/debates/{debate['id']}")
        assert isinstance(r.json(), dict)

    def test_field_names_exact_set(self, client):
        """
        Catches: field name drift between the create response and the get response
        (e.g., a field added on create but dropped on retrieval, or vice versa).
        """
        debate = _post_debate(client)
        body = client.get(f"/api/v1/debates/{debate['id']}").json()
        assert set(body.keys()) == DEBATE_FIELDS

    def test_data_matches_created(self, client):
        """
        Catches: GET returning incorrect or stale data for the requested debate.
        The retrieved resource must be identical to what was stored on creation.
        """
        debate = _post_debate(client, "Specific Title", "Specific description.")
        body = client.get(f"/api/v1/debates/{debate['id']}").json()
        assert body["id"] == debate["id"]
        assert body["title"] == "Specific Title"
        assert body["description"] == "Specific description."
        assert body["created_at"] == debate["created_at"]

    def test_not_found_status_404(self, client):
        """
        Catches: server returning 200 with an empty or null body for a nonexistent
        debate instead of 404.
        """
        r = client.get(f"/api/v1/debates/{MISSING_ID}")
        assert r.status_code == 404

    def test_not_found_response_is_dict(self, client):
        """
        Catches: 404 response being a bare string or array instead of the
        required dict envelope.
        """
        r = client.get(f"/api/v1/debates/{MISSING_ID}")
        assert isinstance(r.json(), dict)

    def test_not_found_error_key_name(self, client):
        """
        Catches: 404 using 'message', 'detail', 'msg', or any key other than
        'error'. The schema mandates {"error": "..."} for all 404 responses.
        """
        body = client.get(f"/api/v1/debates/{MISSING_ID}").json()
        assert "error" in body, (
            f"404 must use 'error' key; got: {sorted(body.keys())}"
        )

    def test_not_found_error_message_exact(self, client):
        """
        Catches: wrong error message string — e.g., "Not found", "no debate",
        or a generic server message instead of the schema-specified string.
        """
        body = client.get(f"/api/v1/debates/{MISSING_ID}").json()
        assert body["error"] == "Debate not found"


# ==========================================================================
# 4. ADD ARGUMENT  (POST /api/v1/debates/{debate_id}/arguments)
# ==========================================================================


class TestAddArgument:

    def test_status_201(self, client):
        """
        Catches: implementation returning 200 instead of 201 for argument creation.
        """
        debate = _post_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "for", "body": "The transition is economically viable."},
        )
        assert r.status_code == 201

    def test_response_is_dict_not_list(self, client):
        """
        Catches: argument creation response wrapped in a list or envelope object.
        """
        debate = _post_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "for", "body": "Arg body."},
        )
        assert isinstance(r.json(), dict)

    def test_field_names_exact_set(self, client):
        """
        Catches: missing fields, extra fields, or renamed fields in the argument
        response (e.g., 'text' instead of 'body', or 'debateId' instead of 'debate_id').
        """
        debate = _post_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "for", "body": "Arg body."},
        )
        assert set(r.json().keys()) == ARGUMENT_FIELDS

    def test_debate_id_comes_from_path_not_body(self, client):
        """
        Catches: server reading debate_id from the request body instead of the
        URL path parameter. The schema requires debate_id to always be set from
        the path. Sending a fake debate_id in the body must be silently ignored;
        the response must still show the path's debate_id.
        """
        debate = _post_debate(client)
        fake_id = "ffffffff-ffff-4fff-afff-ffffffffffff"
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "for", "body": "Arg.", "debate_id": fake_id},
        )
        assert r.status_code == 201
        assert r.json()["debate_id"] == debate["id"], (
            "debate_id in response must be the path parameter, not the body value"
        )

    def test_side_for_accepted(self, client):
        """
        Catches: "for" being incorrectly rejected as an invalid side value.
        """
        debate = _post_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "for", "body": "Arg."},
        )
        assert r.status_code == 201
        assert r.json()["side"] == "for"

    def test_side_against_accepted(self, client):
        """
        Catches: "against" being incorrectly rejected as an invalid side value.
        """
        debate = _post_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "against", "body": "Arg."},
        )
        assert r.status_code == 201
        assert r.json()["side"] == "against"

    def test_side_for_capitalized_returns_422(self, client):
        """
        Catches: case-insensitive side validation accepting 'For' when only 'for'
        is valid. The schema is explicit: side values are case-sensitive.
        """
        debate = _post_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "For", "body": "Arg."},
        )
        assert r.status_code == 422

    def test_side_for_uppercase_returns_422(self, client):
        """
        Catches: server accepting 'FOR' as a valid side value.
        """
        debate = _post_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "FOR", "body": "Arg."},
        )
        assert r.status_code == 422

    def test_side_against_capitalized_returns_422(self, client):
        """
        Catches: server accepting 'Against' as a valid side value.
        """
        debate = _post_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "Against", "body": "Arg."},
        )
        assert r.status_code == 422

    def test_side_arbitrary_value_returns_422(self, client):
        """
        Catches: server accepting values like 'pro', 'con', 'yes', 'neutral' as
        valid side values. Only 'for' and 'against' are permitted by the schema.
        """
        debate = _post_debate(client)
        for invalid_side in ("pro", "con", "yes", "neutral", "support"):
            r = client.post(
                f"/api/v1/debates/{debate['id']}/arguments",
                json={"side": invalid_side, "body": "Arg."},
            )
            assert r.status_code == 422, (
                f"Expected 422 for side={invalid_side!r}, got {r.status_code}"
            )

    def test_body_empty_string_returns_422(self, client):
        """
        Catches: server accepting body="" (violates min_length=1 constraint).
        An empty argument body is not meaningful and must be rejected.
        """
        debate = _post_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "for", "body": ""},
        )
        assert r.status_code == 422

    def test_body_at_max_length_accepted(self, client):
        """
        Catches: off-by-one in max_length=2000 that rejects a body of exactly 2000
        characters. The boundary value must be accepted.
        """
        debate = _post_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "for", "body": "x" * 2000},
        )
        assert r.status_code == 201

    def test_body_over_max_length_returns_422(self, client):
        """
        Catches: server accepting body with 2001+ characters.
        """
        debate = _post_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "for", "body": "x" * 2001},
        )
        assert r.status_code == 422

    def test_missing_side_returns_422(self, client):
        """
        Catches: server accepting an argument payload without the required 'side' field.
        """
        debate = _post_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"body": "Arg without side."},
        )
        assert r.status_code == 422

    def test_missing_body_returns_422(self, client):
        """
        Catches: server accepting an argument payload without the required 'body' field.
        """
        debate = _post_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "for"},
        )
        assert r.status_code == 422

    def test_debate_not_found_returns_404(self, client):
        """
        Catches: server not verifying debate existence before storing an argument,
        allowing orphaned arguments to be created against nonexistent debates.
        """
        r = client.post(
            f"/api/v1/debates/{MISSING_ID}/arguments",
            json={"side": "for", "body": "Arg."},
        )
        assert r.status_code == 404

    def test_debate_not_found_error_shape(self, client):
        """
        Catches: 404 for missing debate parent using wrong error envelope or
        wrong error message string.
        """
        r = client.post(
            f"/api/v1/debates/{MISSING_ID}/arguments",
            json={"side": "for", "body": "Arg."},
        )
        body = r.json()
        assert isinstance(body, dict)
        assert "error" in body
        assert body["error"] == "Debate not found"

    def test_argument_id_is_uuid_v4(self, client):
        """
        Catches: argument id not being a UUID v4 (e.g., sequential integer or UUID
        of a different version).
        """
        debate = _post_debate(client)
        r = client.post(
            f"/api/v1/debates/{debate['id']}/arguments",
            json={"side": "for", "body": "Arg."},
        )
        assert UUID_V4_RE.match(r.json()["id"]), (
            f"argument id must be UUID v4; got: {r.json()['id']!r}"
        )

    def test_argument_count_increments_on_each_argument(self, client):
        """
        Catches: argument_count on the debate not being updated when an argument is
        added, or being updated only on the first argument.
        """
        debate = _post_debate(client)
        assert debate["argument_count"] == 0

        _post_argument(client, debate["id"], side="for", body="First arg.")
        count = client.get(f"/api/v1/debates/{debate['id']}").json()["argument_count"]
        assert count == 1

        _post_argument(client, debate["id"], side="against", body="Second arg.")
        count = client.get(f"/api/v1/debates/{debate['id']}").json()["argument_count"]
        assert count == 2

    def test_argument_count_counts_all_sides(self, client):
        """
        Catches: argument_count being filtered by side (e.g., counting only 'for'
        arguments). The schema states argument_count is always the full count,
        regardless of side.
        """
        debate = _post_debate(client)
        _post_argument(client, debate["id"], side="for", body="For 1.")
        _post_argument(client, debate["id"], side="for", body="For 2.")
        _post_argument(client, debate["id"], side="against", body="Against 1.")

        body = client.get(f"/api/v1/debates/{debate['id']}").json()
        assert body["argument_count"] == 3


# ==========================================================================
# 5. LIST ARGUMENTS  (GET /api/v1/debates/{debate_id}/arguments)
# ==========================================================================


class TestListArguments:

    def test_status_200(self, client):
        """
        Catches: wrong status code for a successful argument list request.
        """
        debate = _post_debate(client)
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments")
        assert r.status_code == 200

    def test_envelope_is_dict_not_list(self, client):
        """
        Catches: returning a bare JSON array instead of the schema-required
        {"arguments": [...], "total": N} wrapper. A bare array prevents adding
        metadata (total, pagination) without a breaking change.
        """
        debate = _post_debate(client)
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments")
        assert isinstance(r.json(), dict), (
            "GET .../arguments must return a dict envelope, not a bare list"
        )

    def test_envelope_keys_exact(self, client):
        """
        Catches: missing 'arguments' or 'total' keys in the envelope, or using
        the wrong key name (e.g., 'items', 'results', 'data').
        """
        debate = _post_debate(client)
        body = client.get(f"/api/v1/debates/{debate['id']}/arguments").json()
        assert "arguments" in body, "envelope must contain 'arguments' key"
        assert "total" in body, "envelope must contain 'total' key"

    def test_empty_argument_list_shape(self, client):
        """
        Catches: returning null or omitting 'arguments' when a debate exists but
        has no arguments yet. The empty state must be {"arguments": [], "total": 0}.
        """
        debate = _post_debate(client)
        body = client.get(f"/api/v1/debates/{debate['id']}/arguments").json()
        assert body["arguments"] == []
        assert body["total"] == 0

    def test_argument_items_have_exact_fields(self, client):
        """
        Catches: argument list items having a different field set than the
        single-argument create response (field consistency across representations).
        """
        debate = _post_debate(client)
        _post_argument(client, debate["id"])
        body = client.get(f"/api/v1/debates/{debate['id']}/arguments").json()
        assert set(body["arguments"][0].keys()) == ARGUMENT_FIELDS

    def test_total_matches_returned_count(self, client):
        """
        Catches: 'total' not matching len(arguments), or 'total' being hardcoded.
        """
        debate = _post_debate(client)
        _post_argument(client, debate["id"], side="for", body="For arg.")
        _post_argument(client, debate["id"], side="against", body="Against arg.")
        body = client.get(f"/api/v1/debates/{debate['id']}/arguments").json()
        assert body["total"] == 2
        assert len(body["arguments"]) == 2

    def test_no_filter_returns_all_sides(self, client):
        """
        Catches: omitting ?side= not returning arguments of both sides (e.g., a
        default filter being applied when the parameter is absent).
        """
        debate = _post_debate(client)
        _post_argument(client, debate["id"], side="for", body="For arg.")
        _post_argument(client, debate["id"], side="against", body="Against arg.")
        body = client.get(f"/api/v1/debates/{debate['id']}/arguments").json()
        sides = {a["side"] for a in body["arguments"]}
        assert sides == {"for", "against"}

    def test_ordering_oldest_first(self, client):
        """
        Catches: arguments ordered descending instead of the schema-required ascending
        (oldest first) ordering within a debate. Chronological order matters for debate
        readability.
        """
        debate = _post_debate(client)
        a1 = _post_argument(client, debate["id"], side="for", body="First argument.")
        time.sleep(0.05)  # ensure distinct created_at timestamps
        a2 = _post_argument(client, debate["id"], side="against", body="Second argument.")
        ids = [a["id"] for a in
               client.get(f"/api/v1/debates/{debate['id']}/arguments").json()["arguments"]]
        assert ids[0] == a1["id"], "oldest argument must appear first"
        assert ids[1] == a2["id"], "newer argument must appear second"

    def test_side_filter_for_excludes_against(self, client):
        """
        Catches: ?side=for filter not excluding 'against' arguments, or filtering
        by a different mechanism than exact string match.
        """
        debate = _post_debate(client)
        _post_argument(client, debate["id"], side="for", body="For arg.")
        _post_argument(client, debate["id"], side="against", body="Against arg.")
        body = client.get(
            f"/api/v1/debates/{debate['id']}/arguments?side=for"
        ).json()
        assert body["total"] == 1
        assert all(a["side"] == "for" for a in body["arguments"])

    def test_side_filter_against_excludes_for(self, client):
        """
        Catches: ?side=against filter not excluding 'for' arguments.
        """
        debate = _post_debate(client)
        _post_argument(client, debate["id"], side="for", body="For arg.")
        _post_argument(client, debate["id"], side="against", body="Against arg.")
        body = client.get(
            f"/api/v1/debates/{debate['id']}/arguments?side=against"
        ).json()
        assert body["total"] == 1
        assert all(a["side"] == "against" for a in body["arguments"])

    def test_side_filter_total_reflects_filtered_count(self, client):
        """
        Catches: 'total' returning the unfiltered count when ?side= is active,
        instead of the count of items actually returned after filtering.
        """
        debate = _post_debate(client)
        _post_argument(client, debate["id"], side="for", body="For 1.")
        _post_argument(client, debate["id"], side="for", body="For 2.")
        _post_argument(client, debate["id"], side="against", body="Against 1.")
        body = client.get(
            f"/api/v1/debates/{debate['id']}/arguments?side=for"
        ).json()
        assert body["total"] == 2
        assert len(body["arguments"]) == 2

    def test_side_filter_invalid_value_returns_422(self, client):
        """
        Catches: server treating an invalid side value as an empty filter and
        returning 200 with an empty list, instead of rejecting with 422.
        """
        debate = _post_debate(client)
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments?side=pro")
        assert r.status_code == 422

    def test_side_filter_yes_returns_422(self, client):
        """
        Catches: server accepting 'yes' as a proxy for 'for' or treating it as
        a truthy value rather than an exact string match.
        """
        debate = _post_debate(client)
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments?side=yes")
        assert r.status_code == 422

    def test_side_filter_case_sensitive_For_returns_422(self, client):
        """
        Catches: case-insensitive ?side= filtering accepting 'For' when only
        lowercase 'for' is a valid value per the schema.
        """
        debate = _post_debate(client)
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments?side=For")
        assert r.status_code == 422

    def test_side_filter_empty_string_returns_422(self, client):
        """
        Catches: server treating ?side= (empty string) as equivalent to omitting
        the parameter (returning all arguments) instead of rejecting it as invalid.
        An empty string is not a valid value for a constrained enum parameter.
        """
        debate = _post_debate(client)
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments?side=")
        assert r.status_code == 422

    def test_debate_not_found_returns_404(self, client):
        """
        Catches: server returning 200 with an empty list instead of 404 when the
        debate does not exist. Returning an empty list would silently hide the error.
        """
        r = client.get(f"/api/v1/debates/{MISSING_ID}/arguments")
        assert r.status_code == 404

    def test_debate_not_found_error_shape(self, client):
        """
        Catches: 404 for missing debate using wrong error envelope or wrong message.
        """
        r = client.get(f"/api/v1/debates/{MISSING_ID}/arguments")
        body = r.json()
        assert isinstance(body, dict)
        assert "error" in body
        assert body["error"] == "Debate not found"

    def test_422_error_envelope_uses_detail_list(self, client):
        """
        Catches: 422 response (from invalid ?side= value) using {"error": "..."}
        instead of FastAPI's native {"detail": [...]} format.

        This is the same contract violation as in the create-debate 422 test.
        The schema requires the native FastAPI format for ALL 422 responses,
        including those triggered by invalid query parameter values.
        """
        debate = _post_debate(client)
        r = client.get(f"/api/v1/debates/{debate['id']}/arguments?side=invalid_value")
        assert r.status_code == 422
        body = r.json()
        assert "detail" in body, (
            "422 must use FastAPI native envelope with 'detail' key; "
            f"got keys: {sorted(body.keys())}"
        )
        assert isinstance(body["detail"], list)

    def test_arguments_isolated_per_debate(self, client):
        """
        Catches: argument list returning arguments from other debates (isolation
        failure), or shared global argument state across debates.
        """
        d1 = _post_debate(client, "Debate 1")
        d2 = _post_debate(client, "Debate 2")
        _post_argument(client, d1["id"], side="for", body="D1 arg.")
        _post_argument(client, d2["id"], side="against", body="D2 arg.")

        body1 = client.get(f"/api/v1/debates/{d1['id']}/arguments").json()
        body2 = client.get(f"/api/v1/debates/{d2['id']}/arguments").json()

        assert body1["total"] == 1
        assert body2["total"] == 1
        assert body1["arguments"][0]["debate_id"] == d1["id"]
        assert body2["arguments"][0]["debate_id"] == d2["id"]
