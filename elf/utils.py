import csv
import warnings
from datetime import datetime, timezone

from .cache import get_cache_guess_file
from .constants import AOC_TZ
from .models import Guess, SubmissionStatus, UnlockStatus

CURRENT_YEAR = datetime.now(tz=AOC_TZ).year


def read_guesses(year: int, day: int) -> list[Guess]:
    cache_file = get_cache_guess_file(year, day)
    if not cache_file.exists():
        return []

    guesses: list[Guess] = []
    skipped_rows = 0

    try:
        with cache_file.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    status_raw = (row.get("status") or "UNKNOWN").upper()
                    status = SubmissionStatus.__members__.get(
                        status_raw, SubmissionStatus.UNKNOWN
                    )

                    guess_raw = row.get("guess", "")
                    if isinstance(guess_raw, str) and guess_raw.lstrip("+-").isdigit():
                        guess_val: int | str = int(guess_raw)
                    else:
                        guess_val = guess_raw

                    timestamp_raw = row.get("timestamp", "") or ""
                    try:
                        if timestamp_raw:
                            timestamp = datetime.fromisoformat(timestamp_raw)
                            # Normalize to tz-aware (assume UTC if missing)
                            if timestamp.tzinfo is None:
                                timestamp = timestamp.replace(tzinfo=timezone.utc)
                        else:
                            timestamp = datetime.now(timezone.utc)
                    except Exception:
                        timestamp = datetime.now(timezone.utc)

                    part_raw = row.get("part")
                    if part_raw is None:
                        raise ValueError("Missing part column")

                    guesses.append(
                        Guess(
                            timestamp=timestamp,
                            part=int(part_raw),
                            guess=guess_val,
                            status=status,
                        )
                    )
                except Exception:
                    skipped_rows += 1
                    continue
    except Exception as exc:
        raise RuntimeError(f"Failed reading guess cache {cache_file}: {exc}") from exc

    if skipped_rows:
        warnings.warn(
            f"Skipped {skipped_rows} malformed guess cache rows in {cache_file}.",
            RuntimeWarning,
            stacklevel=1,
        )

    sorted_guesses = sorted(
        guesses,
        key=lambda g: (g.timestamp, g.part, str(g.guess)),
    )

    return sorted_guesses


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
