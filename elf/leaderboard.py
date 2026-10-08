import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from pydantic import ValidationError
from rich.table import Table

from .aoc_client import AOCClient
from .cache import (
    get_cache_leaderboard_file,
    get_leaderboard_cache_scope,
    write_cache_text,
)
from .exceptions import LeaderboardFetchError, MissingSessionTokenError
from .models import Leaderboard, OutputFormat
from .utils import handle_http_errors, resolve_session

LEADERBOARD_CACHE_TTL_SECONDS = 900


def get_leaderboard(
    year: int,
    session: str | None,
    board_id: int,
    view_key: str | None,
    fmt: OutputFormat = OutputFormat.MODEL,
    refresh: bool = False,
) -> Leaderboard | str | Table:
    """
    Fetch a private leaderboard for a specific year.

    Args:
        year: The year of the Advent of Code challenge.
        session: Your Advent of Code session token (optional if view_key is supplied).
        board_id: The ID of the private leaderboard.
        view_key: The view key for the private leaderboard, if required.
    """

    if year < 2015:
        raise ValueError(f"Invalid year {year!r}. Advent of Code started in 2015.")

    if board_id <= 0:
        raise ValueError("Board ID must be a positive integer.")

    # Resolve session token from explicit arg or environment for consistency with other APIs.
    session_token = (
        resolve_session(session)
        if view_key is None
        else session or os.getenv("AOC_SESSION")
    )
    if not session_token and not view_key:
        raise MissingSessionTokenError(env_var="AOC_SESSION")

    scope = get_leaderboard_cache_scope(session_token, view_key)
    cache_file = get_cache_leaderboard_file(year, board_id, scope)
    payload = None
    leaderboard = None

    if not refresh and _is_fresh(cache_file):
        try:
            payload = json.loads(cache_file.read_text(encoding="utf-8"))
            leaderboard = Leaderboard.model_validate(payload)
        except (OSError, ValueError, ValidationError):
            payload = None
            leaderboard = None

    if leaderboard is None:
        try:
            with AOCClient(session_token=session_token) as client:
                response = client.fetch_leaderboard(year, board_id, view_key)
        except httpx.TimeoutException as exc:
            raise LeaderboardFetchError(
                "Timed out while fetching leaderboard. Try again or check your network."
            ) from exc
        except httpx.RequestError as exc:
            raise LeaderboardFetchError(
                f"Network error while connecting to Advent of Code: {exc}"
            ) from exc

        handle_http_errors(
            response,
            exc_cls=LeaderboardFetchError,
            not_found_message=f"Leaderboard not found for year={year}, board_id={board_id} (HTTP 404).",
            bad_request_message="Bad request (HTTP 400). Your session token or view key may be invalid.",
            server_error_message="Server error from Advent of Code (HTTP {status_code}). Your session token may be invalid.",
            unexpected_status_message="Unexpected HTTP error: {status_code}.",
        )

        try:
            payload = response.json()
        except ValueError as exc:
            raise LeaderboardFetchError(
                "Failed to decode leaderboard JSON. Your session/view key may be invalid."
            ) from exc

        try:
            leaderboard = Leaderboard.model_validate(payload)
        except ValidationError as exc:
            raise LeaderboardFetchError(
                "Unexpected leaderboard schema from Advent of Code."
            ) from exc

        write_cache_text(cache_file, json.dumps(payload, separators=(",", ":")))

    assert payload is not None
    assert leaderboard is not None

    match fmt:
        case OutputFormat.MODEL:
            return leaderboard
        case OutputFormat.JSON:
            return json.dumps(payload, indent=2)
        case OutputFormat.TABLE:
            return format_leaderboard_as_table(leaderboard)
        case _:
            raise ValueError(f"Unsupported output format: {fmt}")


def _is_fresh(
    cache_file: Path, ttl_seconds: int = LEADERBOARD_CACHE_TTL_SECONDS
) -> bool:
    try:
        age = time.time() - cache_file.stat().st_mtime
    except OSError:
        return False
    return 0 <= age < ttl_seconds


def format_leaderboard_as_table(leaderboard: Leaderboard) -> Table:
    table = Table(title=f"Advent of Code {leaderboard.event} – Private Leaderboard")

    table.add_column("Rank", justify="right", style="bold")
    table.add_column("Name", style="cyan")
    table.add_column("Stars", justify="right", style="yellow")
    table.add_column("Local Score", justify="right", style="green")
    table.add_column("Last Star (UTC)", style="magenta")

    # sort: highest local_score, then highest stars
    members = sorted(
        leaderboard.members.values(),
        key=lambda m: (-m.local_score, -m.stars, m.id),
    )

    for rank, member in enumerate(members, start=1):
        last_star = (
            datetime.fromtimestamp(member.last_star_ts, tz=timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            if member.last_star_ts
            else "-"
        )

        table.add_row(
            str(rank),
            member.name or "<anonymous>",
            str(member.stars),
            str(member.local_score),
            last_star,
        )

    return table
