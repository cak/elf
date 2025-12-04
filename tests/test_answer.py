import pytest

from elf.answer import check_cached_guesses, write_guess_cache
from elf.models import SubmissionStatus


@pytest.fixture
def cache_dir(monkeypatch, tmp_path):
    path = tmp_path / "cache"
    monkeypatch.setenv("ELF_CACHE_DIR", str(path))
    return path


def test_duplicate_guess_short_circuits(cache_dir):
    write_guess_cache(2025, 1, 1, 42, SubmissionStatus.INCORRECT)

    result = check_cached_guesses(
        year=2025,
        day=1,
        level=1,
        answer=42,
        numeric_answer=42,
    )

    assert result.status is SubmissionStatus.INCORRECT
    assert result.previous_guess == 42
    assert "You already tried" in result.message


def test_wait_cache_prevents_retry(cache_dir):
    write_guess_cache(2025, 1, 1, 7, SubmissionStatus.WAIT)

    result = check_cached_guesses(
        year=2025,
        day=1,
        level=1,
        answer=7,
        numeric_answer=7,
    )

    assert result.status is SubmissionStatus.WAIT
    assert "try again after" in result.message


def test_bounds_inferred_from_cache(cache_dir):
    write_guess_cache(2025, 1, 1, 10, SubmissionStatus.TOO_LOW)
    write_guess_cache(2025, 1, 1, 20, SubmissionStatus.TOO_HIGH)

    result = check_cached_guesses(
        year=2025,
        day=1,
        level=1,
        answer=9,
        numeric_answer=9,
    )

    assert result.status is SubmissionStatus.TOO_LOW
    assert result.previous_guess == 10
    assert "highest low" in result.message
