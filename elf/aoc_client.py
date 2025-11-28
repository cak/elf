from __future__ import annotations

import atexit
import time
from types import TracebackType

import httpx

from .constants import VERSION

_shared_client: httpx.Client | None = None


def _get_http_client() -> httpx.Client:
    """Return a shared httpx.Client with sane limits and timeouts."""
    global _shared_client
    if _shared_client is None:
        _shared_client = httpx.Client(
            headers={"User-Agent": f"elf/{VERSION} (+https://github.com/cak/elf)"},
            follow_redirects=True,
            timeout=httpx.Timeout(connect=5.0, read=15.0, write=10.0, pool=20.0),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        )
    return _shared_client


def _close_http_client() -> None:
    if _shared_client is not None:
        _shared_client.close()


atexit.register(_close_http_client)


class AOCClient:
    def __init__(self, session_token: str | None) -> None:
        self.base_url = "https://adventofcode.com"
        self.session_token = session_token
        self._client = _get_http_client()

    def _get(self, path: str) -> httpx.Response:
        cookies = {"session": self.session_token} if self.session_token else None
        return self._client.get(f"{self.base_url}{path}", cookies=cookies)

    def _post(self, path: str, data: dict[str, str]) -> httpx.Response:
        cookies = {"session": self.session_token} if self.session_token else None
        return self._client.post(f"{self.base_url}{path}", data=data, cookies=cookies)

    def _get_with_retries(
        self, path: str, *, retries: int = 2, backoff: float = 0.5
    ) -> httpx.Response:
        """
        Basic retry wrapper for idempotent GETs to smooth over transient network hiccups.
        """
        attempt = 0
        while True:
            try:
                return self._get(path)
            except (httpx.TimeoutException, httpx.TransportError):
                if attempt >= retries:
                    raise
                time.sleep(backoff * (2**attempt))
                attempt += 1

    def __enter__(self) -> "AOCClient":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        # Shared client is closed via atexit; no-op here to keep connections warm.
        return None

    def fetch_input(self, year: int, day: int) -> httpx.Response:
        """
        Fetch the puzzle input for a specific year and day.
        """
        return self._get_with_retries(f"/{year}/day/{day}/input")

    def submit_answer(
        self, year: int, day: int, answer: str, part: int
    ) -> httpx.Response:
        """
        Submit an answer for a specific year, day, and part.
        """
        data = {"level": str(part), "answer": answer}
        response = self._post(f"/{year}/day/{day}/answer", data=data)
        return response

    def fetch_leaderboard(
        self, year: int, board_id: int, view_key: str | None = None
    ) -> httpx.Response:
        """
        Fetch a private leaderboard for a specific year.
        If a view_key is provided, it will be included in the request.
        """
        if view_key:
            response = self._get_with_retries(
                f"/{year}/leaderboard/private/view/{board_id}.json?view_key={view_key}"
            )
        else:
            response = self._get_with_retries(
                f"/{year}/leaderboard/private/view/{board_id}.json"
            )
        return response

    def fetch_event(self, year: int) -> httpx.Response:
        """
        Fetch general event information for a specific year (html).
        """
        return self._get_with_retries(f"/{year}")
