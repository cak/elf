from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, auto


@dataclass(frozen=True, slots=True)
class TestResult:
    part: int
    passed: bool
    expected: str
    actual: str
    message: str

    def __repr__(self):
        return (
            f"TestResult(\n"
            f"  part={self.part},\n"
            f"  passed={self.passed},\n"
            f"  expected='{self.expected}',\n"
            f"  actual='{self.actual}',\n"
            f"  message='{self.message}'\n"
            f")"
        )


class SubmissionStatus(StrEnum):
    CORRECT = auto()
    INCORRECT = auto()
    TOO_HIGH = auto()
    TOO_LOW = auto()
    WAIT = auto()
    COMPLETED = auto()
    UNKNOWN = auto()


@dataclass(frozen=True, slots=True)
class SubmissionResult:
    guess: int | str
    result: SubmissionStatus
    message: str
    is_correct: bool
    is_cached: bool

    def __repr__(self):
        return (
            f"SubmissionResult(\n"
            f"  guess={self.guess},\n"
            f"  result={self.result.name},\n"
            f"  is_correct={self.is_correct},\n"
            f"  is_cached={self.is_cached},\n"
            f"  message='{self.message}'\n"
            f")"
        )


@dataclass(slots=True)
class Guess:
    timestamp: datetime
    part: int
    guess: int | str
    status: SubmissionStatus

    def is_too_low(self, answer: int | str) -> bool:
        if isinstance(self.guess, int) and isinstance(answer, int):
            return self.guess < answer and self.status == SubmissionStatus.TOO_LOW
        return False

    def is_too_high(self, answer: int | str) -> bool:
        if isinstance(self.guess, int) and isinstance(answer, int):
            return self.guess > answer and self.status == SubmissionStatus.TOO_HIGH
        return False


@dataclass(frozen=True, slots=True)
class CachedGuessCheck:
    guess: int | str
    previous_guess: int | str | None
    previous_timestamp: datetime | None
    status: SubmissionStatus
    message: str
