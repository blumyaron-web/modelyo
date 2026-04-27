"""
API — POST / PUT / DELETE /posts tests
Scenario 3: POST /posts → 201, response echoes payload, includes generated id.
Scenario 4: PUT /posts/{id} → 200 with updated body; DELETE /posts/{id} → 200/204.
Note: JSONPlaceholder simulates writes; we assert response shape, not persistence.
"""
from __future__ import annotations

import pytest

from flows.flows import Flows
from tests.data.test_run_data import TestRunData

pytestmark = [
    pytest.mark.api,
    pytest.mark.rest,
    pytest.mark.posts,
    pytest.mark.crud,
]


class TestPostsCrud:
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_create_post_returns_201_with_echoed_payload(
        self, flows: Flows, test_run_data: TestRunData
    ) -> None:
        """Scenario 3 — POST /posts → 201 with generated id and echoed fields."""
        flows.assert_create_post(payload=test_run_data.posts.create_payload)

    @pytest.mark.regression
    def test_update_post_returns_200_with_updated_body(
        self, flows: Flows, test_run_data: TestRunData
    ) -> None:
        """Scenario 4a — PUT /posts/{id} → 200 with the updated fields."""
        flows.assert_update_post(payload=test_run_data.posts.update_payload, target_id=test_run_data.posts.valid_id)

    @pytest.mark.regression
    def test_delete_post_returns_success(self, flows: Flows, test_run_data: TestRunData) -> None:
        """Scenario 4b — DELETE /posts/{id} → 200 or 204."""
        flows.assert_delete_post(post_id=test_run_data.posts.valid_id)
