from datetime import timezone

from rich.console import Group
from rich.table import Table
from rich.text import Text

from .config import get_cache_guess_file
from .models import Guess
from .utils import read_guesses


def get_guesses(year: int, day: int) -> Group:
    cache_file = get_cache_guess_file(year, day)
    if not cache_file.exists():
        raise FileNotFoundError(f"No cached guesses found at {cache_file}")
    cached_guesses = read_guesses(year, day)

    return render_guess_tables(cached_guesses)


def render_guess_tables(guesses: list[Guess]):
    # normalize datetimes
    guesses = sorted(guesses, key=lambda g: _ensure_aware(g.timestamp))

    # split
    part1 = [g for g in guesses if g.part == 1]
    part2 = [g for g in guesses if g.part == 2]

    table1 = _render_single_table(part1, title="Guess History – Part 1")
    table2 = _render_single_table(part2, title="Guess History – Part 2")

    # Rich will print these back-to-back in order
    return Group(table1, table2)


def _render_single_table(guesses: list[Guess], title: str) -> Table:
    table = Table(title=title)

    table.add_column("Time (UTC)", style="cyan")
    table.add_column("Guess", justify="right", style="yellow")
    table.add_column("Status", style="green")

    for g in guesses:
        ts = _ensure_aware(g.timestamp).strftime("%Y-%m-%d %H:%M:%S")

        if g.status.value == "completed":
            status_text = Text("Completed", style="bold green")
        elif g.status.value == "unknown":
            status_text = Text("Unknown", style="yellow")
        else:
            status_text = Text(g.status.value)

        table.add_row(ts, str(g.guess), status_text)

    return table


def _ensure_aware(dt):
    """Make any datetime UTC-aware."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
