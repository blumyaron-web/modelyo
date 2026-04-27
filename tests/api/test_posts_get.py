"""
API — GET /posts tests
Scenario 1: 200 OK, array response, schema validation on individual item.
Scenario 2: 200 for valid id, 404 for non-existent id.
"""
from __future__ import annotations

import pytest

from flows.flows import Flows
from tests.data.test_run_data import TestRunData

pytestmark = [
    pytest.mark.api,
    pytest.mark.rest,
    pytest.mark.posts,
    pytest.mark.smoke,
]


class TestGetPosts:
    @pytest.mark.schema_validation
    @pytest.mark.regression
    def test_get_all_posts_returns_array_with_valid_schema(
        self, flows: Flows, test_run_data: TestRunData
    ) -> None:
        """Scenario 1 — GET /posts → 200, array, correct item schema."""
        flows.assert_get_all_posts()

    @pytest.mark.regression
    def test_get_single_post_valid_id(self, flows: Flows, test_run_data: TestRunData) -> None:
        """Scenario 2a — GET /posts/1 → 200 with correct id."""
        flows.assert_get_single_post(post_id=test_run_data.posts.valid_id)

    @pytest.mark.boundary
    @pytest.mark.regression
    def test_get_single_post_nonexistent_id(self, flows: Flows, test_run_data: TestRunData) -> None:
        """Scenario 2b — GET /posts/99999 → 404."""
        flows.assert_not_found(post_id=test_run_data.posts.non_existent_id)
