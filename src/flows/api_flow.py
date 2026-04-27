"""API flow — HTTP action helpers and response assertions for the /posts resource.

Public API
----------
    assert_get_all_posts(response)                    -> None  (soft assertions)
    assert_get_single_post(response, expected_id)     -> None  (soft assertions)
    assert_not_found(response, post_id)               -> None  (soft assertion)
    assert_create_post(response, payload)             -> None  (soft assertions)
    assert_update_post(response, payload, target_id)  -> None  (soft assertions)
    assert_delete_post(response)                      -> None  (soft assertions)
"""
from __future__ import annotations

import logging

from assertpy import assert_that, soft_assertions
from httpx import Response

logger = logging.getLogger(__name__)

_POST_SCHEMA_KEYS = {"userId", "id", "title", "body"}


# ── Assertions ────────────────────────────────────────────────────────────

def assert_get_all_posts(response: Response) -> None:
    """Soft-assert a GET /posts response is healthy and schema-correct.

    Checks:
        • HTTP 200.
        • Body is a JSON array with exactly 100 items (JSONPlaceholder contract).
        • First item contains all required schema keys.
        • Each field has the expected type (userId: int, id: int, title/body: str).
    """
    logger.info("[api_flow] Asserting GET /posts response")
    data = response.json() if response.status_code == 200 else []
    first = data[0] if data else {}

    with soft_assertions():
        assert_that(response.status_code) \
            .described_as(
                f"GET /posts — unexpected HTTP status.\n"
                f"  Expected : 200\n"
                f"  Actual   : {response.status_code}\n"
                "The API may be unreachable or returning an error."
            ).is_equal_to(200)

        assert_that(data) \
            .described_as(
                "GET /posts — response body must be a JSON array. "
                "Received a non-list type; the API contract may have changed."
            ).is_instance_of(list)

        assert_that(len(data)) \
            .described_as(
                f"GET /posts — JSONPlaceholder always returns exactly 100 posts.\n"
                f"  Got {len(data)} item(s). "
                "The endpoint or environment may have changed."
            ).is_equal_to(100)

        missing_keys = _POST_SCHEMA_KEYS - first.keys()
        assert_that(missing_keys) \
            .described_as(
                f"GET /posts — first post is missing required schema keys: {missing_keys}.\n"
                f"  Full post received: {first}\n"
                "The API schema may have changed — review the contract."
            ).is_empty()

        assert_that(first.get("userId")) \
            .described_as(
                f"GET /posts[0].userId must be an int, got {type(first.get('userId')).__name__!r}."
            ).is_instance_of(int)

        assert_that(first.get("id")) \
            .described_as(
                f"GET /posts[0].id must be an int, got {type(first.get('id')).__name__!r}."
            ).is_instance_of(int)

        assert_that(first.get("title")) \
            .described_as(
                "GET /posts[0].title must be a non-empty string — "
                f"got {first.get('title')!r}."
            ).is_instance_of(str).is_not_empty()

        assert_that(first.get("body")) \
            .described_as(
                "GET /posts[0].body must be a non-empty string — "
                f"got {first.get('body')!r}."
            ).is_instance_of(str).is_not_empty()

    logger.info("[api_flow] GET /posts assertions passed")


def assert_get_single_post(response: Response, expected_id: int) -> None:
    """Soft-assert a GET /posts/{id} response for a known-good id.

    Checks:
        • HTTP 200.
        • Response ``id`` field equals ``expected_id``.
    """
    logger.info("[api_flow] Asserting GET /posts/%d response", expected_id)
    data = response.json() if response.status_code == 200 else {}

    with soft_assertions():
        assert_that(response.status_code) \
            .described_as(
                f"GET /posts/{expected_id} — expected 200, got {response.status_code}. "
                "The resource may not exist or the server returned an error."
            ).is_equal_to(200)

        assert_that(data.get("id")) \
            .described_as(
                f"GET /posts/{expected_id} — response 'id' field mismatch.\n"
                f"  Expected : {expected_id}\n"
                f"  Actual   : {data.get('id')}\n"
                "The server may have returned a different resource."
            ).is_equal_to(expected_id)

    logger.info("[api_flow] GET /posts/%d assertions passed", expected_id)


def assert_not_found(response: Response, post_id: int) -> None:
    """Soft-assert a 404 response for a non-existent post id.

    Checks:
        • HTTP 404 (anything else means the API is not guarding unknown ids).
    """
    logger.info("[api_flow] Asserting 404 for non-existent id %d", post_id)

    with soft_assertions():
        assert_that(response.status_code) \
            .described_as(
                f"GET /posts/{post_id} — expected 404 for a non-existent id.\n"
                f"  Actual : {response.status_code}\n"
                "The API should return 404 for unknown resource ids. "
                "If it returned 200, the endpoint is not guarding against invalid ids."
            ).is_equal_to(404)

    logger.info("[api_flow] 404 assertion for id %d passed", post_id)


def assert_create_post(response: Response, payload: dict) -> None:
    """Soft-assert a POST /posts response echoes the payload and includes a new id.

    Checks:
        • HTTP 201.
        • Response contains an ``id`` field that is an integer.
        • ``userId``, ``title``, and ``body`` are echoed back verbatim.
    """
    logger.info("[api_flow] Asserting POST /posts response")
    data = response.json() if response.status_code == 201 else {}

    with soft_assertions():
        assert_that(response.status_code) \
            .described_as(
                f"POST /posts — expected 201 Created, got {response.status_code}. "
                "The server did not acknowledge the resource creation."
            ).is_equal_to(201)

        assert_that(data.get("id")) \
            .described_as(
                "POST /posts — response must include a generated integer 'id'.\n"
                f"  Got: {data.get('id')!r}\n"
                "JSONPlaceholder should assign and echo back a new id."
            ).is_instance_of(int)

        assert_that(data.get("userId")) \
            .described_as(
                f"POST /posts — 'userId' was not echoed correctly.\n"
                f"  Sent   : {payload['userId']}\n"
                f"  Echoed : {data.get('userId')}"
            ).is_equal_to(payload["userId"])

        assert_that(data.get("title")) \
            .described_as(
                f"POST /posts — 'title' was not echoed correctly.\n"
                f"  Sent   : {payload['title']!r}\n"
                f"  Echoed : {data.get('title')!r}"
            ).is_equal_to(payload["title"])

        assert_that(data.get("body")) \
            .described_as(
                f"POST /posts — 'body' was not echoed correctly.\n"
                f"  Sent   : {payload['body']!r}\n"
                f"  Echoed : {data.get('body')!r}"
            ).is_equal_to(payload["body"])

    logger.info("[api_flow] POST /posts assertions passed")


def assert_update_post(response: Response, payload: dict, target_id: int) -> None:
    """Soft-assert a PUT /posts/{id} response reflects the updated fields.

    Checks:
        • HTTP 200.
        • ``id`` matches ``target_id``.
        • ``title`` and ``body`` reflect the updated values from ``payload``.
    """
    logger.info("[api_flow] Asserting PUT /posts/%d response", target_id)
    data = response.json() if response.status_code == 200 else {}

    with soft_assertions():
        assert_that(response.status_code) \
            .described_as(
                f"PUT /posts/{target_id} — expected 200, got {response.status_code}. "
                "The update request was not accepted."
            ).is_equal_to(200)

        assert_that(data.get("id")) \
            .described_as(
                f"PUT /posts/{target_id} — response 'id' must match the target.\n"
                f"  Expected : {target_id}\n"
                f"  Actual   : {data.get('id')}"
            ).is_equal_to(target_id)

        assert_that(data.get("title")) \
            .described_as(
                f"PUT /posts/{target_id} — 'title' was not updated correctly.\n"
                f"  Sent   : {payload['title']!r}\n"
                f"  Echoed : {data.get('title')!r}"
            ).is_equal_to(payload["title"])

        assert_that(data.get("body")) \
            .described_as(
                f"PUT /posts/{target_id} — 'body' was not updated correctly.\n"
                f"  Sent   : {payload['body']!r}\n"
                f"  Echoed : {data.get('body')!r}"
            ).is_equal_to(payload["body"])

    logger.info("[api_flow] PUT /posts/%d assertions passed", target_id)


def assert_delete_post(response: Response) -> None:
    """Soft-assert a DELETE /posts/{id} response indicates success.

    Checks:
        • HTTP 200 or 204.
        • If 200, body is an empty JSON object ``{}``.
    """
    logger.info("[api_flow] Asserting DELETE /posts response")

    with soft_assertions():
        assert_that(response.status_code) \
            .described_as(
                f"DELETE /posts — expected 200 or 204, got {response.status_code}. "
                "The server did not confirm deletion."
            ).is_in(200, 204)

        if response.status_code == 200:
            body = response.json()
            assert_that(body) \
                .described_as(
                    f"DELETE /posts with 200 — body should be an empty object {{}}.\n"
                    f"  Got: {body!r}\n"
                    "JSONPlaceholder returns an empty object on simulated delete."
                ).is_equal_to({})

    logger.info("[api_flow] DELETE /posts assertions passed")
