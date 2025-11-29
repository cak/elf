import csv
from datetime import datetime, timedelta, timezone

from elf.answer import check_cached_guesses
from elf.cache import get_cache_guess_file
from elf.models import SubmissionStatus


def _write_guess_csv(cache_file, rows):
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with cache_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "part", "guess", "status"])
        writer.writerows(rows)


def test_check_cached_guesses_respects_wait_ttl(monkeypatch, tmp_path):
    monkeypatch.setenv("ELF_CACHE_DIR", str(tmp_path / "cache"))
    cache_file = get_cache_guess_file(2025, 1)

    wait_timestamp = (datetime.now(timezone.utc) - timedelta(seconds=30)).isoformat()
    _write_guess_csv(
        cache_file,
        [
            (
                wait_timestamp,
                "1",
                "500",
                "WAIT",
            ),
        ],
    )

    result = check_cached_guesses(
        year=2025,
        day=1,
        level=1,
        answer="600",
        numeric_answer=600,
    )

    assert result.status == SubmissionStatus.WAIT
    assert "Cached locally" in result.message


def test_check_cached_guesses_short_circuits_completed(monkeypatch, tmp_path):
    monkeypatch.setenv("ELF_CACHE_DIR", str(tmp_path / "cache"))
    cache_file = get_cache_guess_file(2025, 2)

    _write_guess_csv(
        cache_file,
        [
            (
                datetime.now(timezone.utc).isoformat(),
                "1",
                "123",
                "COMPLETED",
            ),
        ],
    )

    result = check_cached_guesses(
        year=2025,
        day=2,
        level=1,
        answer="999",
        numeric_answer=999,
    )

    assert result.status == SubmissionStatus.COMPLETED


def test_check_cached_guesses_infers_bounds(monkeypatch, tmp_path):
    monkeypatch.setenv("ELF_CACHE_DIR", str(tmp_path / "cache"))
    cache_file = get_cache_guess_file(2025, 3)

    _write_guess_csv(
        cache_file,
        [
            (
                datetime.now(timezone.utc).isoformat(),
                "1",
                "40",
                "TOO_LOW",
            ),
            (
                (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
                "1",
                "100",
                "TOO_HIGH",
            ),
        ],
    )

    low_result = check_cached_guesses(
        year=2025,
        day=3,
        level=1,
        answer="20",
        numeric_answer=20,
    )
    assert low_result.status == SubmissionStatus.TOO_LOW
    assert low_result.previous_guess == 40

    high_result = check_cached_guesses(
        year=2025,
        day=3,
        level=1,
        answer="250",
        numeric_answer=250,
    )
    assert high_result.status == SubmissionStatus.TOO_HIGH
    assert high_result.previous_guess == 100
