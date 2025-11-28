class ElfError(Exception):
    """Base exception for elf package errors."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "An error occurred")


class InputFetchError(ElfError):
    """Raised when there is an issue fetching the puzzle input."""

    def __init__(self, message: str | None = None) -> None:
        default = "Failed to fetch Advent of Code puzzle input."
        super().__init__(message or default)


class LeaderboardFetchError(ElfError):
    """Raised when there is an issue fetching a private leaderboard."""

    def __init__(self, message: str | None = None) -> None:
        default = "Failed to fetch Advent of Code leaderboard."
        super().__init__(message or default)


class StatusFetchError(ElfError):
    """Raised when there is an issue fetching a user's status page."""

    def __init__(self, message: str | None = None) -> None:
        default = "Failed to fetch Advent of Code status."
        super().__init__(message or default)


class SubmissionError(ElfError):
    """Raised when there is an issue submitting the answer."""

    def __init__(self, message: str | None = None) -> None:
        default = "Failed to submit Advent of Code answer."
        super().__init__(message or default)


class MissingSessionTokenError(ElfError):
    """Raised when the Advent of Code session token is missing."""

    def __init__(self, env_var: str = "AOC_SESSION") -> None:
        default = (
            f"Session token is missing. Set the '{env_var}' environment variable "
            "or pass the session token explicitly."
        )
        super().__init__(default)


class PuzzleLockedError(ElfError):
    """Raised when a puzzle has not yet unlocked in AoC time."""

    def __init__(self, year: int, day: int, now, unlock_time) -> None:
        self.year = year
        self.day = day
        self.now = now
        self.unlock_time = unlock_time
        super().__init__(
            f"Puzzle {year}-12-{day:02d} is not unlocked yet. "
            f"Current AoC time is {now.isoformat()}, unlocks at {unlock_time.isoformat()}."
        )
