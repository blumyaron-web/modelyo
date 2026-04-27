"""
API — POST / PUT / DELETE /posts tests
Scenario 3: POST /posts → 201, response echoes payload, includes generated id.
Scenario 4: PUT /posts/{id} → 200 with updated body; DELETE /posts/{id} → 200/204.
Note: JSONPlaceholder simulates writes; we assert response shape, not persistence.
"""
from __future__ import annotations

import pytest

from clients.api_client import APIClient
from flows.api_flow import assert_create_post, assert_delete_post, assert_update_post

pytestmark = [
    pytest.mark.api,
    pytest.mark.rest,
    pytest.mark.posts,
    pytest.mark.crud,
]

TARGET_POST_ID = 1


class TestPostsCrud:
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_create_post_returns_201_with_echoed_payload(
        self, api_client: APIClient
    ) -> None:
        """Scenario 3 — POST /posts → 201 with generated id and echoed fields."""
        payload = {
            "userId": 42,
            "title": "automation test post",
            "body": "created by qa automation suite",
        }
        response = api_client.post("/posts", json=payload)
        assert_create_post(response, payload=payload)

    @pytest.mark.regression
    def test_update_post_returns_200_with_updated_body(
        self, api_client: APIClient
    ) -> None:
        """Scenario 4a — PUT /posts/{id} → 200 with the updated fields."""
        payload = {
            "id": TARGET_POST_ID,
            "userId": 1,
            "title": "updated title",
            "body": "updated body content",
        }
        response = api_client.put(f"/posts/{TARGET_POST_ID}", json=payload)
        assert_update_post(response, payload=payload, target_id=TARGET_POST_ID)

    @pytest.mark.regression
    def test_delete_post_returns_success(self, api_client: APIClient) -> None:
        """Scenario 4b — DELETE /posts/{id} → 200 or 204."""
        response = api_client.delete(f"/posts/{TARGET_POST_ID}")
        assert_delete_post(response)
