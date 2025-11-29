import csv

import pytest

from elf.answer import check_cached_guesses, write_guess_cache
from elf.cache import get_cache_guess_file
from elf.models import SubmissionStatus
from elf.utils import read_guesses


@pytest.fixture
def guess_file_factory(tmp_path, monkeypatch):
    """
    Factory for creating guess CSVs in the real cache path
    used by get_cache_guess_file.
    """
    # Ensure ELF_CACHE_DIR points under tmp_path so the
    # production helper uses a throwaway directory.
    monkeypatch.setenv("ELF_CACHE_DIR", str(tmp_path / "cache"))

    def _create(year: int, day: int, rows: list[tuple[str, str, str, str]]):
        cache_file = get_cache_guess_file(year, day)
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with cache_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "part", "guess", "status"])
            writer.writerows(rows)
        return cache_file

    return _create


def test_write_guess_cache_normalizes_guess(monkeypatch, tmp_path):
    monkeypatch.setenv("ELF_CACHE_DIR", str(tmp_path / "cache"))

    write_guess_cache(
        year=2024,
        day=5,
        part=1,
        guess="  123  ",
        status=SubmissionStatus.INCORRECT,
    )

    cache_file = get_cache_guess_file(2024, 5)
    with cache_file.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # We only care that:
    #   - a row was written
    #   - guess whitespace was trimmed
    #   - status is stored consistently
    assert len(rows) == 1
    assert rows == [
        {
            "timestamp": rows[0]["timestamp"],
            "part": "1",
            "guess": "123",
            "status": "INCORRECT",
        }
    ]


def test_read_guesses_strips_guess_whitespace(guess_file_factory):
    guess_file_factory(
        2024,
        6,
        [
            (
                "2024-12-05T00:00:00+00:00",
                "1",
                "  045 ",
                "TOO_LOW",
            )
        ],
    )

    # The function under test reads from the generated CSV
    guesses = read_guesses(2024, 6)

    assert len(guesses) == 1
    # Normalized string / numeric representation is handled in read_guesses;
    # we only assert that whitespace from the raw CSV is stripped.
    assert str(guesses[0].guess) == "45"
    assert guesses[0].status == SubmissionStatus.TOO_LOW


def test_read_guesses_handles_invalid_timestamp_gracefully(guess_file_factory):
    """
    If a timestamp cannot be parsed, read_guesses should not crash.
    It should still return the guess with normalized value and status.
    """
    guess_file_factory(
        2024,
        8,
        [
            (
                "not-a-timestamp",
                "1",
                "  999 ",
                "INCORRECT",
            )
        ],
    )

    guesses = read_guesses(2024, 8)

    assert len(guesses) == 1
    # Even with a bad timestamp, guess normalization should still occur.
    assert str(guesses[0].guess) == "999"
    assert guesses[0].status == SubmissionStatus.INCORRECT
    # We intentionally do NOT assert on the timestamp value, only that
    # the function did not raise and returned coherent guess data.


def test_check_cached_guesses_detects_duplicate_with_whitespace(
    guess_file_factory,
):
    """
    If a previous CORRECT guess exists, even with whitespace, check_cached_guesses
    should treat the new answer as already-correct and not trigger a new submission.
    """
    guess_file_factory(
        2024,
        7,
        [
            (
                "2024-12-05T00:00:00+00:00",
                "1",
                "  045 ",
                "CORRECT",
            )
        ],
    )

    result = check_cached_guesses(
        year=2024,
        day=7,
        level=1,
        answer="45",
        numeric_answer=45,
    )

    assert result.status == SubmissionStatus.CORRECT
