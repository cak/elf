class ElfError(Exception):
    """Base exception for elf package errors."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message)


class InputFetchError(ElfError):
    """Raised when there is an issue fetching the puzzle input."""

    def __init__(self, message: str | None = None) -> None:
        default = "Failed to fetch Advent of Code puzzle input."
        super().__init__(message or default)


class SubmissionError(ElfError):
    """Raised when there is an issue submitting the answer."""

    def __init__(self, message: str | None = None) -> None:
        default = "Failed to submit Advent of Code answer."
        super().__init__(message or default)


class MissingSessionTokenError(ElfError):
    """Raised when the Advent of Code session token is missing."""

    def __init__(self, env_var: str = "AOC_SESSION_COOKIE") -> None:
        default = (
            f"Session token is missing. Set the '{env_var}' environment variable "
            "or pass the session token explicitly."
        )
        super().__init__(default)
