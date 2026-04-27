"""
API — GET /posts tests
Scenario 1: 200 OK, array response, schema validation on individual item.
Scenario 2: 200 for valid id, 404 for non-existent id.
"""
from __future__ import annotations

import pytest

from clients.api_client import APIClient
from flows.api_flow import assert_get_all_posts, assert_get_single_post, assert_not_found

pytestmark = [
    pytest.mark.api,
    pytest.mark.rest,
    pytest.mark.posts,
    pytest.mark.smoke,
]

NON_EXISTENT_ID = 99_999


class TestGetPosts:
    @pytest.mark.schema_validation
    @pytest.mark.regression
    def test_get_all_posts_returns_array_with_valid_schema(
        self, api_client: APIClient
    ) -> None:
        """Scenario 1 — GET /posts → 200, array, correct item schema."""
        response = api_client.get("/posts")
        assert_get_all_posts(response)

    @pytest.mark.regression
    def test_get_single_post_valid_id(self, api_client: APIClient) -> None:
        """Scenario 2a — GET /posts/1 → 200 with correct id."""
        response = api_client.get("/posts/1")
        assert_get_single_post(response, expected_id=1)

    @pytest.mark.boundary
    @pytest.mark.regression
    def test_get_single_post_nonexistent_id(self, api_client: APIClient) -> None:
        """Scenario 2b — GET /posts/99999 → 404."""
        response = api_client.get(f"/posts/{NON_EXISTENT_ID}")
        assert_not_found(response, post_id=NON_EXISTENT_ID)
