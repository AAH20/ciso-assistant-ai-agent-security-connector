"""Minimal standard-library API client with dry-run-first safety."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


DEFAULT_ENDPOINTS = {
    "asset": "assets/",
    "evidence": "evidences/",
    "finding": "findings/",
    "metric_definition": "metrics/",
    "metric_sample": "metric-samples/",
}


class CisoAssistantClient:
    def __init__(self, base_url: str, token: str, timeout_seconds: float = 10.0):
        if not base_url.startswith("https://"):
            raise ValueError("Apply mode requires an HTTPS CISO Assistant API URL")
        if not token:
            raise ValueError("Apply mode requires a Personal Access Token")
        self.base_url = base_url.rstrip("/") + "/"
        self.token = token
        self.timeout_seconds = timeout_seconds

    def create(self, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        endpoint = DEFAULT_ENDPOINTS.get(kind)
        if not endpoint:
            raise ValueError(f"No endpoint mapping for object kind: {kind}")
        request = Request(
            urljoin(self.base_url, endpoint),
            data=json.dumps(payload).encode(),
            method="POST",
            headers={"Authorization": f"Token {self.token}", "Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode())
        except HTTPError as error:
            detail = error.read().decode(errors="replace")[:1000]
            raise RuntimeError(f"CISO Assistant API returned HTTP {error.code}: {detail}") from error
        except URLError as error:
            raise RuntimeError(f"CISO Assistant API connection failed: {error.reason}") from error
