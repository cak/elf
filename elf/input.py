import os

import httpx

from .aoc_client import AOCClient
from .cache import get_cache_input_file
from .exceptions import InputFetchError, MissingSessionTokenError, PuzzleLockedError
from .utils import CURRENT_YEAR, get_unlock_status


def get_input(year: int, day: int, session: str | None) -> str:
    """
    Fetch and cache the Advent of Code puzzle input for a specific year and day.

    Args:
        year: The year of the Advent of Code challenge.
        day: The day of the Advent of Code challenge.
        session: Your Advent of Code session token, or None to signal missing.

    Returns:
        The puzzle input for the specified day. Uses the cache if available.

    Raises:
        MissingSessionTokenError: If no session token was provided.
        InputFetchError: If there is an issue fetching the puzzle input.
        ValueError: If the year/day are out of range.
    """
    if not 1 <= day <= 25:
        raise ValueError(f"Invalid day {day!r}. Advent of Code days are 1–25.")

    if year < 2015:
        raise ValueError(f"Invalid year {year!r}. Advent of Code started in 2015.")

    cache_file = get_cache_input_file(year, day)
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8")

    if year >= CURRENT_YEAR:
        status = get_unlock_status(year, day)
        if not status.unlocked:
            raise PuzzleLockedError(
                year=year,
                day=day,
                now=status.now,
                unlock_time=status.unlock_time,
            )

    session_token = session or os.getenv("AOC_SESSION")

    if not session_token:
        raise MissingSessionTokenError(env_var="AOC_SESSION")

    # --- Network layer --------------------------------------------------------

    try:
        with AOCClient(session_token=session_token) as client:
            response = client.fetch_input(year, day)

    except httpx.TimeoutException as exc:
        raise InputFetchError(
            "Timed out while fetching puzzle input. Try again or check your network."
        ) from exc

    except httpx.RequestError as exc:
        raise InputFetchError(
            f"Network error while connecting to Advent of Code: {exc}"
        ) from exc

    # --- HTTP status handling -------------------------------------------------
    if response.status_code == 404:
        raise InputFetchError(f"Input not found for year={year}, day={day} (HTTP 404).")

    if response.status_code == 400:
        raise InputFetchError(
            "Bad request (HTTP 400). Your session token may be invalid."
        )

    if 500 <= response.status_code < 600:
        raise InputFetchError(
            f"Server error from Advent of Code (HTTP {response.status_code}). Your session token may be invalid."
        )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise InputFetchError(
            f"Unexpected HTTP error: {exc.response.status_code}."
        ) from exc

    text = response.text

    if _looks_like_login_page(response):
        raise InputFetchError(
            "Session cookie invalid or expired. "
            "Update AOC_SESSION with a valid 'session' cookie from your browser."
        )

    input_data = text

    # Ensure the cache directory exists
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(input_data, encoding="utf-8")

    return input_data


def _looks_like_login_page(response: httpx.Response) -> bool:
    """
    Detect when AoC returns the login page (often HTTP 200 with HTML) instead of input.
    Prevents caching the login HTML as input when the session is missing/invalid.
    """
    content_type = response.headers.get("Content-Type", "").lower()
    if "text/plain" in content_type:
        return False

    html = response.text
    markers = (
        "To play, please identify yourself",
        "/auth/login",
        'name="session"',
    )
    return any(marker in html for marker in markers)
