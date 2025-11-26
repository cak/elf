import csv
from datetime import datetime, timezone

from .config import get_cache_guess_file
from .models import Guess, SubmissionStatus


def read_guesses(year: int, day: int) -> list[Guess]:
    cache_file = get_cache_guess_file(year, day)
    if not cache_file.exists():
        return []

    guesses: list[Guess] = []

    try:
        with cache_file.open("r", newline="") as f:
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
        raise RuntimeError(f"Failed reading guess cache {cache_file}: {exc}")

    return guesses
