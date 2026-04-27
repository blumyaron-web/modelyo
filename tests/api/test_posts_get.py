"""
API — GET /posts tests
Scenario 1: 200 OK, array response, schema validation on individual item.
Scenario 2: 200 for valid id, 404 for non-existent id.
"""
from __future__ import annotations

import pytest

from clients.api_client import APIClient

POST_SCHEMA_KEYS = {"userId", "id", "title", "body"}
NON_EXISTENT_ID = 99_999


class TestGetPosts:
    def test_get_all_posts_returns_array_with_valid_schema(
        self, api_client: APIClient
    ) -> None:
        """Scenario 1 — GET /posts → 200, array, correct item schema."""
        response = api_client.get("/posts")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert isinstance(data, list), "Response should be a JSON array"
        assert len(data) == 100, f"JSONPlaceholder /posts should return 100 items, got {len(data)}"

        # Validate schema on the first item
        first = data[0]
        missing = POST_SCHEMA_KEYS - first.keys()
        assert not missing, f"Missing keys in post schema: {missing}"

        # Type-level validation
        assert isinstance(first["userId"], int), "userId must be an int"
        assert isinstance(first["id"], int), "id must be an int"
        assert isinstance(first["title"], str) and first["title"], "title must be a non-empty string"
        assert isinstance(first["body"], str) and first["body"], "body must be a non-empty string"

    def test_get_single_post_valid_id(self, api_client: APIClient) -> None:
        """Scenario 2a — GET /posts/1 → 200 with correct id."""
        response = api_client.get("/posts/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1

    def test_get_single_post_nonexistent_id(self, api_client: APIClient) -> None:
        """Scenario 2b — GET /posts/99999 → 404."""
        response = api_client.get(f"/posts/{NON_EXISTENT_ID}")

        assert response.status_code == 404, (
            f"Expected 404 for id={NON_EXISTENT_ID}, got {response.status_code}"
        )
