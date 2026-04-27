"""
API — POST / PUT / DELETE /posts tests
Scenario 3: POST /posts → 201, response echoes payload, includes generated id.
Scenario 4: PUT /posts/{id} → 200 with updated body; DELETE /posts/{id} → 200/204.
Note: JSONPlaceholder simulates writes; we assert response shape, not persistence.
"""
from __future__ import annotations

import pytest

from clients.api_client import APIClient

TARGET_POST_ID = 1


class TestPostsCrud:
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

        assert response.status_code == 201, f"Expected 201, got {response.status_code}"

        data = response.json()
        assert "id" in data and isinstance(data["id"], int), "Response must include a generated int id"
        assert data["userId"] == payload["userId"], "userId should be echoed back"
        assert data["title"] == payload["title"], "title should be echoed back"
        assert data["body"] == payload["body"], "body should be echoed back"

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

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert data["id"] == TARGET_POST_ID
        assert data["title"] == payload["title"], "PUT should return the updated title"
        assert data["body"] == payload["body"], "PUT should return the updated body"

    def test_delete_post_returns_success(self, api_client: APIClient) -> None:
        """Scenario 4b — DELETE /posts/{id} → 200 or 204."""
        response = api_client.delete(f"/posts/{TARGET_POST_ID}")

        assert response.status_code in (200, 204), (
            f"Expected 200 or 204, got {response.status_code}"
        )
        # For 200, body should be an empty object {}
        if response.status_code == 200:
            assert response.json() == {}, "DELETE 200 body should be an empty object"
