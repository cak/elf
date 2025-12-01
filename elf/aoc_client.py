from __future__ import annotations

import atexit
import os
import re
import time
import warnings
from types import TracebackType

import httpx

from .constants import VERSION

_shared_client: httpx.Client | None = None

_user_agent_prefix = f"elf/{VERSION}"
_default_user_agent = "+https://github.com/cak/elf"


def _get_http_client() -> httpx.Client:
    """
    Return a process-global httpx.Client with sane limits/timeouts.

    The shared client keeps connections warm for CLI calls. If you make
    heavy concurrent requests from multiple threads, construct your own
    AOCClient instances to avoid sharing this global session.
    """
    global _shared_client
    if _shared_client is None:
        user_agent = os.getenv("AOC_USER_AGENT")

        # Strip whitespace and control characters if present
        if user_agent is not None:
            user_agent = user_agent.replace("\r", "").replace("\n", "").strip()

        if not _validate_user_agent(user_agent):
            # Missing vs invalid message
            if user_agent is None:
                warnings.warn(
                    "User-Agent should include an email address. "
                    "Please set AOC_USER_AGENT in your environment.",
                    RuntimeWarning,
                )
            else:
                warnings.warn(
                    f"Invalid User-Agent header: {user_agent!r}\n\n"
                    "User-Agent should include an email address. "
                    "Please set AOC_USER_AGENT in your environment.",
                    RuntimeWarning,
                )
            user_agent = _default_user_agent

        # Ensure user_agent is not None at this point
        assert user_agent is not None

        _shared_client = httpx.Client(
            headers={"User-Agent": _construct_user_agent(user_agent)},
            follow_redirects=True,
            timeout=httpx.Timeout(connect=5.0, read=15.0, write=10.0, pool=20.0),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        )
    return _shared_client


def _close_http_client() -> None:
    if _shared_client is not None:
        _shared_client.close()


atexit.register(_close_http_client)


def _construct_user_agent(user_agent: str) -> str:
    return f"{_user_agent_prefix} ({user_agent})"


def _validate_user_agent(user_agent: str | None) -> bool:
    """
    Very minimal check that the user agent string contains something that
    looks like an email address so Eric Wastl can contact the user.
    """
    return (
        user_agent is not None and re.search(r"[^@]+@[^.]+\..+", user_agent) is not None
    )


class AOCClient:
    def __init__(self, session_token: str | None) -> None:
        self.base_url = "https://adventofcode.com"
        self.session_token = session_token
        self._client = _get_http_client()

    def _get(self, path: str, params: dict[str, str] | None = None) -> httpx.Response:
        cookies = {"session": self.session_token} if self.session_token else None
        return self._client.get(
            f"{self.base_url}{path}", params=params, cookies=cookies
        )

    def _post(self, path: str, data: dict[str, str]) -> httpx.Response:
        cookies = {"session": self.session_token} if self.session_token else None
        return self._client.post(f"{self.base_url}{path}", data=data, cookies=cookies)

    def _get_with_retries(
        self,
        path: str,
        *,
        retries: int = 2,
        backoff: float = 0.5,
        params: dict[str, str] | None = None,
    ) -> httpx.Response:
        """
        Basic retry wrapper for idempotent GETs to smooth over transient network hiccups.
        """
        attempt = 0
        while True:
            try:
                return self._get(path, params=params)
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
        params = {"view_key": view_key} if view_key else None
        response = self._get_with_retries(
            f"/{year}/leaderboard/private/view/{board_id}.json",
            params=params,
        )
        return response

    def fetch_event(self, year: int) -> httpx.Response:
        """
        Fetch general event information for a specific year (html).
        """
        return self._get_with_retries(f"/{year}")
