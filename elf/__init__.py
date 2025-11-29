"""
Elf: a small Advent of Code helper library.

Public API:

- get_puzzle_input(year, day, session=None) -> str
- submit_puzzle_answer(year, day, part, answer, session=None) -> SubmissionResult
- get_private_leaderboard(year, session, board_id, view_key, fmt=OutputFormat.MODEL)
- get_user_status(year, session=None, fmt=OutputFormat.MODEL)

The session token can be passed explicitly or via the AOC_SESSION environment variable.
"""

from ._version import get_package_version

__version__ = get_package_version()

from .client import (
    get_private_leaderboard,
    get_puzzle_input,
    get_user_status,
    submit_puzzle_answer,
)
from .models import (
    DayStatus,
    Leaderboard,
    OutputFormat,
    SubmissionResult,
    YearStatus,
)

__all__ = [
    "get_puzzle_input",
    "submit_puzzle_answer",
    "get_private_leaderboard",
    "get_user_status",
    "OutputFormat",
    "SubmissionResult",
    "DayStatus",
    "YearStatus",
    "Leaderboard",
]
