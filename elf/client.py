import os

from rich.table import Table

from .answer import submit_answer
from .input import get_input
from .leaderboard import get_leaderboard
from .models import Leaderboard, OutputFormat, SubmissionResult
from .status import get_status
from .utils import resolve_session


def get_puzzle_input(year: int, day: int, session: str | None = None) -> str:
    """
    Retrieve the raw puzzle input for a specific Advent of Code puzzle.

    This is equivalent to opening the “Input” page on adventofcode.com and
    copying the contents. The returned string is exactly what the puzzle
    expects you to parse — no transformations are applied.

    Parameters
    ----------
    year:
        The Advent of Code event year (e.g., ``2024``).
    day:
        The puzzle day number (``1``–``25``).
    session:
        An Advent of Code session token. If omitted, the value of the
        ``AOC_SESSION`` environment variable will be used instead.

    Returns
    -------
    str
        The puzzle input as provided by Advent of Code.

    Raises
    ------
    MissingSessionTokenError
        If no session token is supplied and ``AOC_SESSION`` is not set.
    InputFetchError
        If the request fails or the page cannot be retrieved.

    Notes
    -----
    - This function performs an authenticated HTTP request.
    - Advent of Code input pages are personalized per user.
    """
    session_token = resolve_session(session)
    return get_input(year, day, session_token)


def submit_puzzle_answer(
    year: int,
    day: int,
    part: int,
    answer: str,
    session: str | None = None,
) -> SubmissionResult:
    """
    Submit an answer for a specific puzzle part.

    This mirrors pressing the “Submit” button on the Advent of Code website.
    The response indicates whether the answer was correct, incorrect, already
    solved, or rate-limited.

    Parameters
    ----------
    year:
        The event year (e.g., ``2024``).
    day:
        The puzzle day number.
    part:
        The puzzle part (``1`` or ``2``).
    answer:
        The answer to submit, as a string.
    session:
        An Advent of Code session token. If omitted, ``AOC_SESSION`` is used.

    Returns
    -------
    SubmissionResult
        A structured result describing the outcome of the submission.

    Raises
    ------
    MissingSessionTokenError
        If no valid session token is available.
    ValueError
        If the submission parameters are invalid.

    Notes
    -----
    - Advent of Code enforces a submission cooldown after incorrect answers.
    - This function does **not** retry automatically.
    """
    session_token = resolve_session(session)
    return submit_answer(year, day, part, answer, session_token)


def get_private_leaderboard(
    year: int,
    board_id: int,
    session: str | None = None,
    view_key: str | None = None,
    fmt: OutputFormat = OutputFormat.MODEL,
) -> Leaderboard | str | Table:
    """
    Retrieve a private leaderboard for a given year.

    Private leaderboards allow groups to track each other's progress. This
    function fetches the leaderboard’s current state and optionally formats it
    as a Python object, JSON string, or a human-readable representation. You
    can provide either a session token (full access) or just a view key
    (read-only share link).

    Parameters
    ----------
    year:
        The event year.
    session:
        A session token. Required only when ``view_key`` is not provided.
    board_id:
        The numeric ID of the private leaderboard.
    view_key:
        The read-only “share code” for the leaderboard. When present, a session
        token is optional.
    fmt:
        The desired output format (``MODEL`` | ``JSON`` | ``TABLE``).

    Returns
    -------
    Any
        A structured leaderboard model, a JSON string, or a formatted
        table representation, depending on ``fmt``.

    Raises
    ------
    MissingSessionTokenError
        If no session token is available and no view key is provided.
    LeaderboardFetchError
        If the leaderboard cannot be retrieved.

    Notes
    -----
    - The returned structure depends on ``OutputFormat``.
    """
    if year < 2015:
        raise ValueError(f"Invalid year {year!r}. Advent of Code started in 2015.")

    if board_id <= 0:
        raise ValueError("Board ID must be a positive integer.")

    session_token = (
        resolve_session(session)
        if view_key is None
        else session or os.getenv("AOC_SESSION")
    )
    return get_leaderboard(year, session_token, board_id, view_key, fmt)


def get_user_status(
    year: int,
    session: str | None = None,
    fmt: OutputFormat = OutputFormat.MODEL,
):
    """
    Retrieve the user's Advent of Code progress for the specified year.

    This includes the star count for each puzzle day, the total stars earned,
    and whether the user is an Advent of Code supporter (AoC++).

    Parameters
    ----------
    year:
        The event year.
    session:
        A session token. If omitted, ``AOC_SESSION`` will be used.
    fmt:
        Output format: ``MODEL`` for Pydantic models, ``JSON`` for a JSON
        string, or ``TABLE`` for a Rich-rendered status table.

    Returns
    -------
    Any
        A ``YearStatus`` model, JSON string, or Rich table depending on
        ``fmt``.

    Raises
    ------
    MissingSessionTokenError
        If no session token can be resolved.

    Notes
    -----
    - Status is parsed directly from the calendar HTML on the event page.
    - Some features (e.g., star colors) may vary between years.
    """
    session_token = resolve_session(session)
    return get_status(year, session_token, fmt)
