import csv
from datetime import date, datetime, timezone

from .cache import get_cache_guess_file
from .constants import AOC_TZ
from .models import Guess, SubmissionStatus, UnlockStatus

CURRENT_YEAR = date.today().year


def read_guesses(year: int, day: int) -> list[Guess]:
    cache_file = get_cache_guess_file(year, day)
    if not cache_file.exists():
        return []

    guesses: list[Guess] = []

    try:
        with cache_file.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                status = SubmissionStatus[row.get("status", "UNKNOWN")]
                guess_raw = row.get("guess", "")

                try:
                    guess_val: int | str = int(guess_raw)
                except ValueError:
                    guess_val = guess_raw

                try:
                    timestamp = datetime.fromisoformat(row["timestamp"])
                except Exception:
                    timestamp = datetime.now(timezone.utc)

                guesses.append(
                    Guess(
                        timestamp=timestamp,
                        part=int(row["part"]),
                        guess=guess_val,
                        status=status,
                    )
                )
    except Exception as exc:
        raise RuntimeError(f"Failed reading guess cache {cache_file}: {exc}") from exc

    return guesses


def get_unlock_status(year: int, day: int) -> UnlockStatus:
    """
    Return whether the given AoC puzzle is unlocked yet, based on America/New_York.

    AoC unlocks each day at midnight local time (Y-12-D 00:00 in America/New_York).
    """
    if not 1 <= day <= 25:
        # Let existing validation handle out-of-range days elsewhere
        raise ValueError(f"Invalid day {day!r}. Advent of Code days are 1–25.")

    # Current time in AoC timezone
    now = datetime.now(tz=AOC_TZ)

    # Official unlock moment for this puzzle (AoC uses December only)
    unlock_time = datetime(year=year, month=12, day=day, tzinfo=AOC_TZ)

    return UnlockStatus(
        unlocked=now >= unlock_time,
        now=now,
        unlock_time=unlock_time,
    )
