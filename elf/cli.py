from datetime import date
from enum import Enum
from typing import Annotated

import typer
from rich.console import Console

from .answer import submit_answer
from .exceptions import ElfError
from .guesses import get_guesses
from .input import get_input
from .leaderboard import get_leaderboard

app = typer.Typer(
    help="Advent of Code CLI", no_args_is_help=True, rich_markup_mode="rich"
)

console = Console()
error_console = Console(stderr=True)


class OutputFormat(str, Enum):
    TABLE = "table"
    JSON = "json"


_today = date.today()
THIS_YEAR = _today.year
THIS_DAY = _today.day

YearArg = Annotated[
    int,
    typer.Argument(
        help="Year of the event",
        min=2015,
        max=THIS_YEAR,
    ),
]
DayArg = Annotated[
    int,
    typer.Argument(
        help="Day of the event (1–25)",
        min=1,
        max=25,
    ),
]
LevelArg = Annotated[
    int,
    typer.Argument(
        help="Part of the puzzle (1 or 2)",
        min=1,
        max=2,
    ),
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
    console.print(input_data, end="")  # preserve AoC input as-is


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
        error_console.print("[red]❄️ You must provide an answer to submit.[/red]")
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
    output_format: Annotated[
        OutputFormat,
        typer.Option(
            "--format",
            "-f",
            help="Output format: table, json",
            case_sensitive=False,
        ),
    ] = OutputFormat.TABLE,
) -> None:
    """
    Fetch and display a private leaderboard for a given year.
    """
    leaderboard_data = get_leaderboard(
        year=year,
        session=session,
        board_id=board_id,
        view_key=view_key,
        json_fmt=(output_format is OutputFormat.JSON),
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
    guesses_data = get_guesses(year, day)
    console.print(guesses_data)


def main() -> None:
    try:
        app()
    except ElfError as exc:
        error_console.print(f"[red]❄️ {exc}[/red]")
        raise typer.Exit(1)
    except Exception as exc:
        error_console.print(f"[red]❄️ An unexpected error occurred: {exc}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    main()
