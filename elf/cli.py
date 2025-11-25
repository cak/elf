from __future__ import annotations

from datetime import date
from typing import Annotated

import typer
from rich.console import Console

from .answer import submit_answer
from .exceptions import ElfError
from .input import get_input

app = typer.Typer(help="Advent of Code CLI")
console = Console()


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
        "--no-festive",
        help="Disable festive / emoji output",
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
    no_festive: FestiveOpt = False,
    session: SessionOpt = None,
) -> None:
    """
    Submit an answer for a given year and day.
    """
    if not answer:
        typer.echo("❄️ You must provide an answer to submit.", err=True)
        raise typer.Exit(code=1)

    festive = not no_festive

    submit_result = submit_answer(year, day, level, answer, session, festive=festive)
    console.print(submit_result.message)


def main() -> None:
    try:
        app()
    except ElfError as exc:
        typer.echo(f"❄️ {exc}", err=True)
        raise SystemExit(1)
    except Exception as exc:
        typer.echo(f"❄️ An unexpected error occurred: {exc}", err=True)
        raise SystemExit(1)
