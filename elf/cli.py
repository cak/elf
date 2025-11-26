from __future__ import annotations

from datetime import date
from typing import Annotated

import typer
from rich.console import Console

from .answer import submit_answer
from .exceptions import ElfError
from .guesses import get_guesses
from .input import get_input
from .leaderboard import get_leaderboard

app = typer.Typer(help="Advent of Code CLI")

console = Console()
error_console = Console(stderr=True)

today = date.today()
THIS_YEAR = today.year
THIS_DAY = today.day

YearArg = Annotated[int, typer.Argument(help="Year of the event", min=2015)]
DayArg = Annotated[int, typer.Argument(help="Day of the event (1–25)", min=1, max=25)]
LevelArg = Annotated[
    int, typer.Argument(help="Part of the puzzle (1 or 2)", min=1, max=2)
]
AnswerArg = Annotated[str, typer.Argument(help="Your answer to submit")]

SessionOpt = Annotated[
    str | None,
    typer.Option(
        help="Advent of Code session cookie",
        envvar="AOC_SESSION",
    ),
]

FestiveOpt = Annotated[
    bool,
    typer.Option(
        "--festive",
        help="Enable festive emoji + colored output.",
        show_default=True,
    ),
]


@app.command("input")
def input_cmd(
    year: YearArg = THIS_YEAR,
    day: DayArg = THIS_DAY,
    session: SessionOpt = None,
) -> None:
    """
    Fetch the input for a given year and day.
    """
    input_data = get_input(year, day, session)
    typer.echo(input_data)


@app.command()
def answer(
    year: YearArg = THIS_YEAR,
    day: DayArg = THIS_DAY,
    level: LevelArg = 1,
    answer: AnswerArg = "",
    festive: FestiveOpt = False,
    session: SessionOpt = None,
) -> None:
    """
    Submit an answer for a given year and day.
    """
    if not answer:
        typer.echo("❄️ You must provide an answer to submit.", err=True)
        raise typer.Exit(code=1)

    submit_result = submit_answer(
        year=year,
        day=day,
        level=level,
        answer=answer,
        session=session,
        festive=festive,
    )
    console.print(submit_result.message)


@app.command()
def leaderboard(
    year: YearArg = THIS_YEAR,
    board_id: Annotated[int, typer.Argument(help="Private leaderboard ID")] = 0,
    view_key: Annotated[
        str | None,
        typer.Option(help="View key for the private leaderboard, if required"),
    ] = None,
    session: SessionOpt = None,
    table: Annotated[
        bool,
        typer.Option(
            "--table",
            help="Display leaderboard as a table.",
            show_default=True,
        ),
    ] = False,
) -> None:
    """
    Fetch and display a private leaderboard for a given year.
    """
    leaderboard_data = get_leaderboard(
        year=year,
        session=session,
        board_id=board_id,
        view_key=view_key,
        table=table,
    )

    console.print(leaderboard_data)


@app.command()
def guesses(
    year: YearArg = THIS_YEAR,
    day: DayArg = THIS_DAY,
) -> None:
    """
    Display cached guesses for a given year and day.
    """
    guesses = get_guesses(year, day)
    console.print(guesses)


def main() -> None:
    try:
        app()
    except ElfError as exc:
        error_console.print(f"[red]❄️ {exc}[/red]")
        raise typer.Exit(1)
    except Exception as exc:
        error_console.print(f"[red]❄️ An unexpected error occurred: {exc}[/red]")
        raise typer.Exit(1)
