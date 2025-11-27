import json
from datetime import datetime, timezone

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
        session: Your Advent of Code session token, or None to signal missing.
        board_id: The ID of the private leaderboard.
        view_key: The view key for the private leaderboard, if required.
    """

    if view_key is not None and not session:
        raise MissingSessionTokenError(env_var="AOC_SESSION")
    else:
        session = session or ""

    with AOCClient(session_token=session) as client:
        response = client.fetch_leaderboard(year, board_id, view_key)

    if response.status_code == 404:
        raise InputFetchError(
            f"Leaderboard not found for year={year}, board_id={board_id} (HTTP 404)."
        )

    if response.status_code == 400:
        raise InputFetchError(
            "Bad request (HTTP 400). Your session token or view key may be invalid."
        )

    match fmt:
        case OutputFormat.MODEL:
            leaderboard = Leaderboard.model_validate(response.json())
            return leaderboard
        case OutputFormat.JSON:
            json_str = json.dumps(response.json(), indent=2)
            return json_str
        case OutputFormat.TABLE:
            return format_leaderboard_as_table(response.json())
        case _:
            raise ValueError(f"Unsupported output format: {fmt}")


def format_leaderboard_as_table(leaderboard_json: dict[str, object]) -> Table:
    leaderboard = Leaderboard.model_validate(leaderboard_json)
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
