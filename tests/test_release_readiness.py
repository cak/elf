import json
import tomllib
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

from elf.cache import (
    get_cache_input_file,
    get_cache_scope,
    get_cache_guess_file,
    get_session_cache_scope,
)
from elf.cli import app
from elf.input import get_input
from elf.leaderboard import get_leaderboard
from elf.models import OutputFormat
from elf.utils import event_last_day, validate_event_day


def _leaderboard_payload() -> dict:
    return {
        "num_days": 12,
        "event": "2025",
        "day1_ts": 1764565200,
        "owner_id": 1,
        "members": {},
    }


def test_event_day_ranges_follow_legacy_and_modern_schedules():
    assert event_last_day(2024) == 25
    assert event_last_day(2025) == 12
    assert event_last_day(2026) == 12
    validate_event_day(2024, 25)
    validate_event_day(2025, 12)

    with pytest.raises(ValueError, match="Valid days are 1–12"):
        validate_event_day(2025, 13)


def test_cache_scopes_are_distinct_and_do_not_expose_tokens(monkeypatch, tmp_path):
    monkeypatch.setenv("ELF_CACHE_DIR", str(tmp_path / "cache"))
    first_token = "first-secret-session"
    second_token = "second-secret-session"
    first = get_cache_guess_file(2025, 1, get_cache_scope(first_token))
    second = get_cache_guess_file(2025, 1, get_cache_scope(second_token))

    assert first != second
    assert first_token not in str(first)
    assert second_token not in str(second)


def test_input_cache_is_scoped_by_session(monkeypatch, tmp_path):
    monkeypatch.setenv("ELF_CACHE_DIR", str(tmp_path / "cache"))
    calls: list[str] = []

    class FakeClient:
        def __init__(self, session_token):
            self.session_token = session_token

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def fetch_input(self, year, day):
            calls.append(self.session_token)
            return httpx.Response(
                200,
                text=f"input-for-{self.session_token}",
                headers={"Content-Type": "text/plain"},
                request=httpx.Request("GET", f"https://adventofcode.com/{year}/day/{day}/input"),
            )

    monkeypatch.setattr("elf.input.AOCClient", FakeClient)

    assert get_input(2024, 1, "account-a") == "input-for-account-a"
    assert get_input(2024, 1, "account-b") == "input-for-account-b"
    assert get_input(2024, 1, "account-a") == "input-for-account-a"
    assert calls == ["account-a", "account-b"]
    assert get_cache_input_file(
        2024, 1, get_session_cache_scope("account-a")
    ).exists()


def test_leaderboard_cache_and_refresh(monkeypatch, tmp_path):
    monkeypatch.setenv("ELF_CACHE_DIR", str(tmp_path / "cache"))
    calls = 0

    class FakeClient:
        def __init__(self, session_token):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def fetch_leaderboard(self, year, board_id, view_key):
            nonlocal calls
            calls += 1
            return httpx.Response(
                200,
                json=_leaderboard_payload(),
                request=httpx.Request("GET", "https://adventofcode.com/leaderboard.json"),
            )

    monkeypatch.setattr("elf.leaderboard.AOCClient", FakeClient)

    first = get_leaderboard(
        2025, None, 123, "view-key", OutputFormat.MODEL
    )
    second = get_leaderboard(
        2025, None, 123, "view-key", OutputFormat.MODEL
    )
    refreshed = get_leaderboard(
        2025, None, 123, "view-key", OutputFormat.MODEL, refresh=True
    )

    assert first == second == refreshed
    assert calls == 2


def test_cli_json_output_is_not_processed_by_rich(monkeypatch):
    value = "[bold]" + "a" * 200 + "[/bold]"
    payload = json.dumps({"name": value})

    def fake_get_leaderboard(*args, **kwargs):
        return payload

    monkeypatch.setattr("elf.cli.get_leaderboard", fake_get_leaderboard)
    result = CliRunner().invoke(
        app,
        ["leaderboard", "2025", "123", "--view-key", "key", "--format", "json"],
    )

    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"name": value}


def test_windows_timezone_fallback_is_declared():
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    dependencies = project["project"]["dependencies"]
    assert any(dependency.startswith("tzdata") for dependency in dependencies)
