import csv
from datetime import datetime, timedelta, timezone
from enum import Enum, auto
from html.parser import HTMLParser

import httpx

from .aoc_client import AOCClient
from .cache import get_cache_guess_file
from .exceptions import PuzzleLockedError, SubmissionError
from .messages import (
    get_already_completed_message,
    get_answer_too_high_message,
    get_answer_too_low_message,
    get_cached_duplicate_message,
    get_cached_high_message,
    get_cached_low_message,
    get_correct_answer_message,
    get_incorrect_answer_message,
    get_recent_submission_message,
    get_unexpected_response_message,
    get_wrong_level_message,
)
from .models import CachedGuessCheck, Guess, SubmissionResult, SubmissionStatus
from .utils import current_aoc_year, get_unlock_status, read_guesses, resolve_session

WAIT_CACHE_TTL = timedelta(minutes=1)


class AocResponseParser(HTMLParser):
    """Extract text inside the <article> tag."""

    def __init__(self) -> None:
        super().__init__()
        self.in_article: bool = False
        self.content: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "article":
            self.in_article = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "article":
            self.in_article = False

    def handle_data(self, data: str) -> None:
        if self.in_article:
            self.content.append(data)

    def text(self) -> str:
        return "".join(self.content).strip()


class AocMessageType(Enum):
    EMPTY = auto()
    CORRECT = auto()
    TOO_HIGH = auto()
    TOO_LOW = auto()
    RECENT_SUBMISSION = auto()
    ALREADY_COMPLETED = auto()
    INCORRECT = auto()
    WRONG_LEVEL = auto()
    UNEXPECTED = auto()


def classify_message(content: str) -> AocMessageType:
    if not content:
        return AocMessageType.EMPTY

    checks: list[tuple[str, AocMessageType]] = [
        ("That's the right answer", AocMessageType.CORRECT),
        ("too high", AocMessageType.TOO_HIGH),
        ("too low", AocMessageType.TOO_LOW),
        ("You gave an answer too recently", AocMessageType.RECENT_SUBMISSION),
        ("Did you already complete it", AocMessageType.ALREADY_COMPLETED),
        ("You don't seem to be solving the right level", AocMessageType.WRONG_LEVEL),
        ("That's not the right answer", AocMessageType.INCORRECT),
    ]

    for needle, msg_type in checks:
        if needle in content:
            return msg_type

    return AocMessageType.UNEXPECTED


def submit_answer(
    year: int,
    day: int,
    level: int,
    answer: int | str,
    session: str | None,
) -> SubmissionResult:
    """
    Submit an answer for a specific Advent of Code day/part, with guess caching.

    Args:
        year: The year of the Advent of Code challenge.
        day: The day of the Advent of Code challenge.
        level: Puzzle part (1 or 2).
        answer: The answer to submit (int or string).
        session: Your Advent of Code session token, or None to signal missing.

    Returns:
        A SubmissionResult describing the outcome, including whether it was
        served from the local guess cache or from Advent of Code.

    Raises:
        MissingSessionTokenError: If no session token was provided.
        SubmissionError: If there is an issue submitting the answer.
    """
    submission_answer, numeric_answer = _normalize_answer(answer)

    if not 1 <= day <= 25:
        raise ValueError(f"Invalid day {day!r}. Advent of Code days are 1–25.")

    if year < 2015:
        raise ValueError(f"Invalid year {year!r}. Advent of Code started in 2015.")

    if level not in (1, 2):
        raise ValueError(f"Invalid level {level!r}. Puzzle parts are 1 or 2.")

    if isinstance(answer, str) and not answer.strip():
        raise ValueError("Answer cannot be empty.")

    if year >= current_aoc_year():
        status = get_unlock_status(year, day)
        if not status.unlocked:
            raise PuzzleLockedError(
                year=year,
                day=day,
                now=status.now,
                unlock_time=status.unlock_time,
            )

    session_token = resolve_session(session)

    cache_file = get_cache_guess_file(year, day)
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    # Check cached guesses before hitting network
    if cache_file.exists():
        cached = check_cached_guesses(
            year=year,
            day=day,
            level=level,
            answer=submission_answer,
            numeric_answer=numeric_answer,
        )

        if cached.status != SubmissionStatus.UNKNOWN:
            return SubmissionResult(
                guess=submission_answer,
                result=cached.status,
                message=cached.message,
                is_correct=cached.status == SubmissionStatus.CORRECT,
                is_cached=True,
            )

    return submit_to_aoc(year, day, level, submission_answer, session_token)


def submit_to_aoc(
    year: int,
    day: int,
    level: int,
    answer: int | str,
    session_token: str,
) -> SubmissionResult:
    # --- Network layer --------------------------------------------------------

    try:
        with AOCClient(session_token=session_token) as client:
            response = client.submit_answer(year, day, str(answer), level)
    except httpx.TimeoutException as exc:
        raise SubmissionError(
            "Timed out while submitting answer. Try again or check your network."
        ) from exc

    except httpx.RequestError as exc:
        raise SubmissionError(
            f"Network error while connecting to Advent of Code: {exc}"
        ) from exc

    # --- HTTP status handling -------------------------------------------------

    if response.status_code == 404:
        if "unlocks it for you" in response.text:
            raise SubmissionError("Puzzle not yet unlocked.")
        elif "Please don't repeatedly request this endpoint" in response.text:
            raise SubmissionError(
                "Submitting answers too quickly. Please wait before trying again."
            )

        else:
            raise SubmissionError(
                f"Input not found for year={year}, day={day} (HTTP 404)."
            )

    if response.status_code == 400:
        raise SubmissionError(
            "Bad request (HTTP 400). Your session token may be invalid."
        )

    if 500 <= response.status_code < 600:
        raise SubmissionError(
            f"Server error from Advent of Code (HTTP {response.status_code}). Your session token may be invalid."
        )

    if response.status_code != 200:
        raise SubmissionError(
            f"Unexpected HTTP status {response.status_code} from Advent of Code."
        )

    if "To play, please identify yourself" in response.text:
        raise SubmissionError(
            "Session cookie invalid or expired. "
            "Update AOC_SESSION with a valid 'session' cookie from your browser."
        )

    # Extract <article> content
    parser = AocResponseParser()
    parser.feed(response.text)
    content = parser.text()

    # Determine result type
    message_type = classify_message(content)
    match message_type:
        case AocMessageType.EMPTY:
            message = "Answer submitted, but no response message found."
            status = SubmissionStatus.UNKNOWN
        case AocMessageType.CORRECT:
            message = get_correct_answer_message(answer)
            status = SubmissionStatus.CORRECT
        case AocMessageType.TOO_HIGH:
            message = get_answer_too_high_message(answer)
            status = SubmissionStatus.TOO_HIGH
        case AocMessageType.TOO_LOW:
            message = get_answer_too_low_message(answer)
            status = SubmissionStatus.TOO_LOW
        case AocMessageType.RECENT_SUBMISSION:
            message = get_recent_submission_message()
            status = SubmissionStatus.WAIT
        case AocMessageType.ALREADY_COMPLETED:
            message = get_already_completed_message()
            status = SubmissionStatus.COMPLETED
        case AocMessageType.WRONG_LEVEL:
            message = get_wrong_level_message()
            status = SubmissionStatus.INCORRECT
        case AocMessageType.INCORRECT:
            message = get_incorrect_answer_message(answer)
            status = SubmissionStatus.INCORRECT
        case _:
            message = get_unexpected_response_message()
            status = SubmissionStatus.UNKNOWN

    # Cache the guess (including WAIT, with TTL handling on read)
    write_guess_cache(year, day, level, answer, status)

    return SubmissionResult(
        guess=answer,
        result=status,
        message=message,
        is_correct=status == SubmissionStatus.CORRECT,
        is_cached=False,
    )


def write_guess_cache(
    year: int,
    day: int,
    part: int,
    guess: int | str,
    status: SubmissionStatus,
) -> None:
    cache_file = get_cache_guess_file(year, day)

    timestamp = datetime.now(timezone.utc).isoformat()

    canonical_guess, _ = _normalize_answer(guess)
    row = {
        "timestamp": timestamp,
        "part": part,
        "guess": str(canonical_guess),
        "status": status.name,
    }

    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        file_exists = cache_file.exists()
        with cache_file.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    except Exception as exc:
        raise RuntimeError(f"Failed to write guess cache {cache_file}: {exc}") from exc


def check_cached_guesses(
    year: int,
    day: int,
    level: int,
    answer: int | str,
    numeric_answer: int | None,
) -> CachedGuessCheck:
    guesses = read_guesses(year, day)
    now = datetime.now(timezone.utc)

    highest_low: Guess | None = None
    lowest_high: Guess | None = None
    completed_guess: Guess | None = None  # NEW
    wait_guess: Guess | None = None

    for g in guesses:
        if g.part != level:
            continue

        # Honor recent WAIT responses for this part
        if g.status is SubmissionStatus.WAIT and _within_wait_ttl(g.timestamp, now):
            wait_guess = g
            break

        is_same_guess = g.guess == answer or (
            numeric_answer is not None
            and isinstance(g.guess, int)
            and g.guess == numeric_answer
        )

        # Prevent repeating guess unless guess response was WAIT
        if is_same_guess and g.status != SubmissionStatus.WAIT:
            return CachedGuessCheck(
                guess=answer,
                previous_guess=g.guess,
                previous_timestamp=g.timestamp,
                status=g.status,
                message=get_cached_duplicate_message(answer, g),
            )

        match g:
            # Mark that this part is completed (any previous guess)
            case Guess(status=SubmissionStatus.COMPLETED):
                completed_guess = g

            # Bounds checking (int only)
            case Guess(guess=ans, status=SubmissionStatus.TOO_LOW) if (
                numeric_answer is not None and isinstance(ans, int)
            ):
                if highest_low is None or (
                    isinstance(highest_low.guess, int) and ans > highest_low.guess
                ):
                    highest_low = g
            case Guess(guess=ans, status=SubmissionStatus.TOO_HIGH) if (
                numeric_answer is not None and isinstance(ans, int)
            ):
                if lowest_high is None or (
                    isinstance(lowest_high.guess, int) and ans < lowest_high.guess
                ):
                    lowest_high = g

    # Short-circuit on active cooldown
    if wait_guess is not None:
        retry_at = _retry_at(wait_guess.timestamp)
        return CachedGuessCheck(
            guess=answer,
            previous_guess=None,
            previous_timestamp=wait_guess.timestamp,
            status=SubmissionStatus.WAIT,
            message=_wait_cache_message(retry_at),
        )

    # If we know this part is completed, short-circuit before bounds logic
    if completed_guess is not None:
        return CachedGuessCheck(
            guess=answer,
            previous_guess=None,
            previous_timestamp=completed_guess.timestamp,
            status=SubmissionStatus.COMPLETED,
            message=get_already_completed_message(),
        )

    # Infer bounds
    if numeric_answer is not None:
        match (highest_low, lowest_high):
            case (h_low, _) if (
                h_low and isinstance(h_low.guess, int) and numeric_answer <= h_low.guess
            ):
                return CachedGuessCheck(
                    guess=answer,
                    previous_guess=h_low.guess,
                    previous_timestamp=h_low.timestamp,
                    status=SubmissionStatus.TOO_LOW,
                    message=get_cached_low_message(answer, h_low),
                )
            case (_, l_high) if (
                l_high
                and isinstance(l_high.guess, int)
                and numeric_answer >= l_high.guess
            ):
                return CachedGuessCheck(
                    guess=answer,
                    previous_guess=l_high.guess,
                    previous_timestamp=l_high.timestamp,
                    status=SubmissionStatus.TOO_HIGH,
                    message=get_cached_high_message(answer, l_high),
                )

    # No bounds found
    return CachedGuessCheck(
        guess=answer,
        previous_guess=None,
        previous_timestamp=None,
        status=SubmissionStatus.UNKNOWN,
        message="This is a unique guess.",
    )


def _retry_at(ts: datetime) -> datetime:
    ts_aware = ts if ts.tzinfo is not None else ts.replace(tzinfo=timezone.utc)
    return ts_aware + WAIT_CACHE_TTL


def _within_wait_ttl(ts: datetime, now: datetime) -> bool:
    return _retry_at(ts) > now


def _wait_cache_message(retry_at: datetime) -> str:
    retry_str = retry_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"{get_recent_submission_message()} Cached locally; try again after {retry_str}."


def _normalize_answer(answer: int | str) -> tuple[int | str, int | None]:
    """
    Preserve the user's answer text but still provide a numeric variant for bounds/duplicate guardrails.
    Returns (submission_answer, numeric_answer).
    """
    if isinstance(answer, str):
        stripped = answer.strip()
        if not stripped:
            raise ValueError("Answer cannot be empty.")

        numeric_value: int | None = None
        if stripped.lstrip("+-").isdigit():
            try:
                numeric_value = int(stripped)
            except ValueError:
                numeric_value = None

        return stripped, numeric_value

    return answer, int(answer)
