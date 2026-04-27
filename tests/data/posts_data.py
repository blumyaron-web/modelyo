"""Posts API test data."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PostsData:
    # ID of a post known to exist in JSONPlaceholder (used for GET, PUT, DELETE).
    valid_id: int = 1

    # Non-existent ID that must trigger a 404 response.
    non_existent_id: int = 99_999

    # Payload for POST /posts (Scenario 3).
    create_payload: dict = field(default_factory=lambda: {
        "userId": 42,
        "title": "automation test post",
        "body": "created by qa automation suite",
    })

    # Payload for PUT /posts/{id} (Scenario 4a).
    update_payload: dict = field(default_factory=lambda: {
        "id": 1,
        "userId": 1,
        "title": "updated title",
        "body": "updated body content",
    })


# ── Module-level constants (kept for backward compatibility) ───────────────
_defaults = PostsData()
VALID_POST_ID: int = _defaults.valid_id
NON_EXISTENT_POST_ID: int = _defaults.non_existent_id
CREATE_POST_PAYLOAD: dict = _defaults.create_payload
UPDATE_POST_PAYLOAD: dict = _defaults.update_payload
