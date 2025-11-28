from datetime import datetime
from functools import wraps
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version
from typing import Annotated

import typer
from rich.console import Console

from .answer import submit_answer
from .cache import get_cache_dir
from .constants import AOC_TZ
from .exceptions import ElfError
from .guesses import get_guesses
from .input import get_input
from .leaderboard import get_leaderboard
from .models import OpenKind, OutputFormat
from .open import open_page
from .status import get_status

app = typer.Typer(
    help="Advent of Code CLI",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()
error_console = Console(stderr=True)
_DEBUG = False


def _current_year() -> int:
    return datetime.now(tz=AOC_TZ).year


def _current_day() -> int:
    today = datetime.now(tz=AOC_TZ)
    return min(today.day, 25) if today.month == 12 else 1


YearArg = Annotated[
    int | None,
    typer.Argument(
        help="Year of the event",
        min=2015,
    ),
]
DayArg = Annotated[
    int | None,
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


def handle_cli_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ElfError as exc:
            if _DEBUG:
                raise
            error_console.print(f"[red]❄️ {exc}[/red]")
        except (ValueError, RuntimeError) as exc:
            if _DEBUG:
                raise
            error_console.print(f"[red]❄️ {exc}[/red]")
        raise typer.Exit(code=1)

    return wrapper


def version_callback(value: bool) -> None:
    if not value:
        return

    try:
        v = pkg_version("elf")
    except PackageNotFoundError:
        from . import __version__

        v = f"{__version__} (local)"

    console.print(f"Advent of Code CLI {v}")
    raise typer.Exit()


@app.callback(invoke_without_command=True)
def cli_root(
    _version: bool | None = typer.Option(
        None,
        "--version",
        "-V",
        help="Show the CLI version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Raise errors with tracebacks (also via ELF_DEBUG=1).",
        envvar="ELF_DEBUG",
    ),
) -> None:
    """
    Global options for the Advent of Code CLI.
    """
    global _DEBUG
    _DEBUG = debug


@app.command("input")
@handle_cli_errors
def input_cmd(
    year: YearArg = None,
    day: DayArg = None,
    session: SessionOpt = None,
) -> None:
    """
    Fetch the input for a given year and day.
    """
    year = year or _current_year()
    day = day or _current_day()
    input_data = get_input(year, day, session)
    typer.echo(input_data, nl=False)


@app.command("answer")
@handle_cli_errors
def answer_cmd(
    year: YearArg,
    day: DayArg,
    level: LevelArg,
    answer: AnswerArg,
    session: SessionOpt = None,
) -> None:
    """
    Submit an answer for a given year and day.
    """
    year = year or _current_year()
    day = day or _current_day()
    level = level or 1

    submit_result = submit_answer(
        year=year,
        day=day,
        level=level,
        answer=answer,
        session=session,
    )
    console.print(submit_result.message)


@app.command("leaderboard")
@handle_cli_errors
def leaderboard_cmd(
    year: YearArg,
    board_id: Annotated[int, typer.Argument(help="Private leaderboard ID")],
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
            help="Output format: table, json, model",
            case_sensitive=False,
        ),
    ] = OutputFormat.TABLE,
) -> None:
    """
    Fetch and display a private leaderboard for a given year.
    """
    year = year or _current_year()

    leaderboard_data = get_leaderboard(
        year=year,
        session=session,
        board_id=board_id,
        view_key=view_key,
        fmt=output_format,
    )

    console.print(leaderboard_data)


@app.command("guesses")
@handle_cli_errors
def guesses_cmd(
    year: YearArg = None,
    day: DayArg = None,
) -> None:
    """
    Display cached guesses for a given year and day.
    """
    year = year or _current_year()
    day = day or _current_day()
    guesses_data = get_guesses(year, day)
    console.print(guesses_data)


@app.command("status")
@handle_cli_errors
def status_cmd(
    year: YearArg = None,
    session: SessionOpt = None,
    output_format: Annotated[
        OutputFormat,
        typer.Option(
            "--format",
            "-f",
            help="Output format: table, json, model",
            case_sensitive=False,
        ),
    ] = OutputFormat.TABLE,
) -> None:
    """
    Fetch and display your Advent of Code status for a given year.
    """
    year = year or _current_year()
    status_data = get_status(
        year=year,
        session=session,
        fmt=output_format,
    )

    console.print(status_data)


@app.command("open")
@handle_cli_errors
def open_cmd(
    year: YearArg = None,
    day: DayArg = None,
    kind: Annotated[
        OpenKind,
        typer.Option(
            "--kind",
            "-k",
            help="Kind of page to open: puzzle, input, website",
            case_sensitive=False,
        ),
    ] = OpenKind.PUZZLE,
) -> None:
    """
    Open the puzzle page for a given year and day in the default web browser.
    """
    year = year or _current_year()
    day = day or _current_day()
    open_msg = open_page(year, day, kind)
    console.print(open_msg)


@app.command("cache")
@handle_cli_errors
def cache_cmd() -> None:
    """
    Show information about the local cache.
    """
    cache_dir = get_cache_dir()
    if not cache_dir.exists():
        console.print("[dim]No cache directory found yet.[/dim]")
        console.print(f"[dim]Expected location: {cache_dir}[/dim]")
        return

    files = [p for p in cache_dir.rglob("*") if p.is_file()]
    console.print(f"[green]Cache directory:[/green] {cache_dir}")
    console.print(f"[green]Cached files:[/green] {len(files)}")
    console.print("[dim]To clear the cache, delete this directory manually.[/dim]")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
