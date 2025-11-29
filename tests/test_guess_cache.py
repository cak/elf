import csv

from elf.answer import check_cached_guesses, write_guess_cache
from elf.cache import get_cache_guess_file
from elf.models import SubmissionStatus
from elf.utils import read_guesses


def _write_guess_csv(cache_file, rows):
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with cache_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "part", "guess", "status"])
        writer.writerows(rows)


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
    with cache_file.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert rows == [
        {
            "timestamp": rows[0]["timestamp"],
            "part": "1",
            "guess": "123",
            "status": "INCORRECT",
        }
    ]


def test_read_guesses_strips_guess_whitespace(monkeypatch, tmp_path):
    monkeypatch.setenv("ELF_CACHE_DIR", str(tmp_path / "cache"))

    cache_file = get_cache_guess_file(2024, 6)
    _write_guess_csv(
        cache_file,
        [
            (
                "2024-12-05T00:00:00+00:00",
                "1",
                "  045 ",
                "TOO_LOW",
            ),
        ],
    )

    guesses = read_guesses(2024, 6)

    assert len(guesses) == 1
    assert guesses[0].guess == 45
    assert guesses[0].status == SubmissionStatus.TOO_LOW


def test_check_cached_guesses_detects_duplicate_with_whitespace(monkeypatch, tmp_path):
    monkeypatch.setenv("ELF_CACHE_DIR", str(tmp_path / "cache"))

    cache_file = get_cache_guess_file(2024, 7)
    _write_guess_csv(
        cache_file,
        [
            (
                "2024-12-05T00:00:00+00:00",
                "1",
                "  045 ",
                "CORRECT",
            ),
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
