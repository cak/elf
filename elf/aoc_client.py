from __future__ import annotations

from types import TracebackType

import httpx


class AOCClient:
    def __init__(self, session_token: str | None) -> None:
        self.base_url = "https://adventofcode.com"
        self.session_token = session_token
        self._client = httpx.Client(
            headers={"User-Agent": "elf (+https://github.com/cak/elf)"},
            follow_redirects=True,
            timeout=10.0,
        )

    def _get(self, path: str) -> httpx.Response:
        cookies = {"session": self.session_token} if self.session_token else None
        return self._client.get(f"{self.base_url}{path}", cookies=cookies)

    def _post(self, path: str, data: dict[str, str]) -> httpx.Response:
        cookies = {"session": self.session_token} if self.session_token else None
        return self._client.post(f"{self.base_url}{path}", data=data, cookies=cookies)

    def _close(self) -> None:
        self._client.close()

    def __enter__(self) -> "AOCClient":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._close()

    def fetch_input(self, year: int, day: int) -> httpx.Response:
        """
        Fetch the puzzle input for a specific year and day.
        """
        response = self._get(f"/{year}/day/{day}/input")
        return response

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
            response = self._get(
                f"/{year}/leaderboard/private/view/{board_id}.json?view_key={view_key}"
            )
        else:
            response = self._get(f"/{year}/leaderboard/private/view/{board_id}.json")
        return response

    def fetch_event(self, year: int) -> httpx.Response:
        """
        Fetch general event information for a specific year (html).
        """
        response = self._get(f"/{year}")
        return response
