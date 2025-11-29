import csv
import os
import warnings
from datetime import datetime, timezone

import httpx

from .cache import get_cache_guess_file
from .constants import AOC_TZ
from .exceptions import ElfError, MissingSessionTokenError
from .models import Guess, SubmissionStatus, UnlockStatus


def read_guesses(year: int, day: int) -> list[Guess]:
    cache_file = get_cache_guess_file(year, day)
    if not cache_file.exists():
        return []

    guesses: list[Guess] = []
    skipped_rows = 0

    try:
        with cache_file.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    status_raw = (row.get("status") or "UNKNOWN").upper()
                    status = SubmissionStatus.__members__.get(
                        status_raw, SubmissionStatus.UNKNOWN
                    )

                    guess_raw = row.get("guess", "")
                    if isinstance(guess_raw, str):
                        guess_str = guess_raw.strip()
                    else:
                        guess_str = str(guess_raw)

                    if guess_str.lstrip("+-").isdigit():
                        guess_val: int | str = int(guess_str)
                    else:
                        guess_val = guess_str

                    timestamp_raw = row.get("timestamp", "") or ""
                    try:
                        if timestamp_raw:
                            timestamp = datetime.fromisoformat(timestamp_raw)
                            # Normalize to tz-aware (assume UTC if missing)
                            if timestamp.tzinfo is None:
                                timestamp = timestamp.replace(tzinfo=timezone.utc)
                        else:
                            timestamp = datetime.now(timezone.utc)
                    except Exception:
                        timestamp = datetime.now(timezone.utc)

                    part_raw = row.get("part")
                    if part_raw is None:
                        raise ValueError("Missing part column")

                    guesses.append(
                        Guess(
                            timestamp=timestamp,
                            part=int(part_raw),
                            guess=guess_val,
                            status=status,
                        )
                    )
                except Exception:
                    skipped_rows += 1
                    continue
    except Exception as exc:
        raise ElfError(f"Failed reading guess cache {cache_file}: {exc}") from exc

    if skipped_rows:
        warnings.warn(
            f"Skipped {skipped_rows} malformed guess cache rows in {cache_file}.",
            RuntimeWarning,
            stacklevel=1,
        )

    sorted_guesses = sorted(
        guesses,
        key=lambda g: (g.timestamp, g.part, str(g.guess)),
    )

    return sorted_guesses


def current_aoc_year() -> int:
    """Return the current year in the AoC timezone."""
    return datetime.now(tz=AOC_TZ).year


def get_unlock_status(year: int, day: int) -> UnlockStatus:
    """
    Return whether the given AoC puzzle is unlocked yet, based on America/New_York.

    AoC unlocks each day at midnight local time (Y-12-D 00:00 in America/New_York).
    """
    if not 1 <= day <= 25:
        # Let existing validation handle out-of-range days elsewhere
        raise ValueError(f"Invalid day {day!r}. Advent of Code days are 1–25.")

    # Current time in AoC timezone
    now = datetime.now(tz=AOC_TZ)

    # Official unlock moment for this puzzle (AoC uses December only)
    unlock_time = datetime(year=year, month=12, day=day, tzinfo=AOC_TZ)

    return UnlockStatus(
        unlocked=now >= unlock_time,
        now=now,
        unlock_time=unlock_time,
    )


def resolve_session(session: str | None, env_var: str = "AOC_SESSION") -> str:
    """Resolve a session token from an explicit arg or environment variable."""
    if session:
        return session
    env_session = os.getenv(env_var)
    if env_session:
        return env_session

    raise MissingSessionTokenError(env_var=env_var)


def handle_http_errors(
    response: httpx.Response,
    *,
    exc_cls: type[ElfError],
    not_found_message: str,
    bad_request_message: str,
    server_error_message: str,
    unexpected_status_message: str = "Unexpected HTTP error: {status_code}.",
) -> None:
    """
    Centralized HTTP status handling for AoC endpoints.
    """

    def _fmt(msg: str) -> str:
        return msg.format(status_code=response.status_code)

    if response.status_code == 404:
        raise exc_cls(_fmt(not_found_message))

    if response.status_code == 400:
        raise exc_cls(_fmt(bad_request_message))

    if 500 <= response.status_code < 600:
        raise exc_cls(_fmt(server_error_message))

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise exc_cls(_fmt(unexpected_status_message)) from exc


def looks_like_login_page(response: httpx.Response) -> bool:
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
