"""
Thin HTTP client wrapper around httpx.
One place to change: base URL, headers, timeouts, retry policy.
All tests consume this; never call httpx directly in a test file.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx
from httpx import Response

from config.config import cfg

logger = logging.getLogger(__name__)


class APIClient:
    """Synchronous REST client with centralised config and structured logging."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: int | None = None,
    ) -> None:
        self._base_url = (base_url or cfg.API_BASE_URL).rstrip("/")
        self._timeout = timeout or cfg.API_TIMEOUT
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=self._timeout,
            headers={"Content-Type": "application/json"},
            follow_redirects=True,
        )

    # ── Core request helper ───────────────────────────────────────────────

    def _request(
        self, method: str, path: str, **kwargs: Any
    ) -> Response:
        url = f"{self._base_url}{path}"
        logger.info("→ %s %s  kwargs=%s", method.upper(), url, kwargs)
        response = self._client.request(method, path, **kwargs)
        logger.info(
            "← %s %s  status=%d  body_len=%d",
            method.upper(),
            url,
            response.status_code,
            len(response.content),
        )
        logger.debug("Response body: %s", response.text[:500])
        return response

    # ── HTTP verbs ────────────────────────────────────────────────────────

    def get(self, path: str, **kwargs: Any) -> Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, json: Any = None, **kwargs: Any) -> Response:
        return self._request("POST", path, json=json, **kwargs)

    def put(self, path: str, json: Any = None, **kwargs: Any) -> Response:
        return self._request("PUT", path, json=json, **kwargs)

    def patch(self, path: str, json: Any = None, **kwargs: Any) -> Response:
        return self._request("PATCH", path, json=json, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Response:
        return self._request("DELETE", path, **kwargs)

    # ── Lifecycle ─────────────────────────────────────────────────────────

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "APIClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
