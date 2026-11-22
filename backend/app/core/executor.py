"""Policy gate and test executor for controlled HTTP requests."""

import time
import threading
from typing import Optional

import httpx


class PolicyGate:
    """Enforces target allowlists and rate limits before executing requests."""

    def __init__(self, allowlist: Optional[list[str]] = None, rate_limit: int = 50):
        self._allowlist = allowlist or ["http://localhost", "http://127.0.0.1"]
        self._rate_limit = rate_limit
        self._tokens = float(rate_limit)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def check_target(self, url: str) -> bool:
        """Return True if the URL is in the allowlist."""
        for allowed in self._allowlist:
            if url.startswith(allowed):
                return True
        return False

    def check_rate(self) -> bool:
        """Token bucket rate limiter. Returns True if a request is allowed."""
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_refill
            self._tokens = min(self._rate_limit, self._tokens + elapsed * (self._rate_limit / 60.0))
            self._last_refill = now
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return True
            return False

    @staticmethod
    def is_synthetic(data: Optional[dict]) -> bool:
        """Check whether the data carries a synthetic/demo tag."""
        if data is None:
            return False
        if isinstance(data, dict):
            return data.get("demo_label") == "DEMO / SIMULATED" or data.get("synthetic") is True
        return False


class TestExecutor:
    """Execute HTTP requests through the PolicyGate."""

    def __init__(self, gate: Optional[PolicyGate] = None):
        self._gate = gate or PolicyGate()

    def execute_request(
        self,
        method: str,
        url: str,
        headers: Optional[dict] = None,
        body: Optional[dict] = None,
    ) -> dict:
        """Send an HTTP request if the policy gate allows it."""
        if not self._gate.check_target(url):
            return {"error": "Target not in allowlist", "url": url}
        if not self._gate.check_rate():
            return {"error": "Rate limit exceeded"}

        try:
            with httpx.Client(timeout=30) as client:
                response = client.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    json=body,
                )
                return {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text[:4096],
                }
        except httpx.HTTPError as exc:
            return {"error": str(exc)}
