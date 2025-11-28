import json
from datetime import datetime, timezone

import httpx
from pydantic import ValidationError
from rich.table import Table

from .aoc_client import AOCClient
from .exceptions import InputFetchError, MissingSessionTokenError
from .models import Leaderboard, OutputFormat


def get_leaderboard(
    year: int,
    session: str | None,
    board_id: int,
    view_key: str | None,
    fmt: OutputFormat = OutputFormat.MODEL,
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

    # Require auth only when no view key is supplied.
    if not session and not view_key:
        raise MissingSessionTokenError(env_var="AOC_SESSION")
    session_token = session or None

    try:
        with AOCClient(session_token=session_token) as client:
            response = client.fetch_leaderboard(year, board_id, view_key)
    except httpx.TimeoutException as exc:
        raise InputFetchError(
            "Timed out while fetching leaderboard. Try again or check your network."
        ) from exc
    except httpx.RequestError as exc:
        raise InputFetchError(
            f"Network error while connecting to Advent of Code: {exc}"
        ) from exc

    if response.status_code == 404:
        raise InputFetchError(
            f"Leaderboard not found for year={year}, board_id={board_id} (HTTP 404)."
        )

    if response.status_code == 400:
        raise InputFetchError(
            "Bad request (HTTP 400). Your session token or view key may be invalid."
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

    try:
        payload = response.json()
    except ValueError as exc:
        raise InputFetchError(
            "Failed to decode leaderboard JSON. Your session/view key may be invalid."
        ) from exc

    try:
        leaderboard = Leaderboard.model_validate(payload)
    except ValidationError as exc:
        raise InputFetchError(
            "Unexpected leaderboard schema from Advent of Code."
        ) from exc

    match fmt:
        case OutputFormat.MODEL:
            return leaderboard
        case OutputFormat.JSON:
            return json.dumps(payload, indent=2)
        case OutputFormat.TABLE:
            return format_leaderboard_as_table(leaderboard)
        case _:
            raise ValueError(f"Unsupported output format: {fmt}")


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
