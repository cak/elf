from datetime import datetime

import typer
from typing_extensions import Annotated

from .exceptions import ElfError
from .input import get_input

app = typer.Typer(help="Advent of Code CLI")


this_year = datetime.now().year
this_day = datetime.now().day


@app.command()
def input(
    year: Annotated[int, typer.Argument(help="Year of the event")] = this_year,
    day: Annotated[int, typer.Argument(help="Day of the event")] = this_day,
    session: str | None = typer.Option(
        None,
        help="Advent of Code session cookie",
        envvar="AOC_SESSION",
    ),
) -> None:
    """
    Fetch the input for a given year and day.
    """
    input_data = get_input(year, day, session)
    typer.echo(input_data)


@app.command()
def solve(
    year: Annotated[int, typer.Argument(help="Year of the event")] = this_year,
    day: Annotated[int, typer.Argument(help="Day of the event")] = this_day,
    session: str | None = typer.Option(
        None,
        help="Advent of Code session cookie",
        envvar="AOC_SESSION",
    ),
) -> None:
    """
    Solve the puzzle for a given year and day.
    """
    # Placeholder implementation
    print(f"Solving puzzle for Year: {year}, Day: {day} with session: {session}")


def main():
    try:
        app()
    except ElfError as exc:
        typer.echo(f"❄️ {exc}", err=True)
        raise SystemExit(1)
