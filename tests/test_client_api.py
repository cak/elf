import pytest

from elf.client import (
    get_private_leaderboard,
    get_puzzle_input,
    get_user_status,
    submit_puzzle_answer,
)
from elf.models import OutputFormat


def test_get_puzzle_input_forwards_session(monkeypatch):
    resolved = []
    called = []

    def fake_resolve(session):
        resolved.append(session)
        return "resolved-token"

    def fake_get_input(year, day, session):
        called.append((year, day, session))
        return "input-data"

    monkeypatch.setattr("elf.client.resolve_session", fake_resolve)
    monkeypatch.setattr("elf.client.get_input", fake_get_input)

    assert get_puzzle_input(2023, 5, session="manual") == "input-data"
    assert resolved == ["manual"]
    assert called == [(2023, 5, "resolved-token")]


def test_submit_puzzle_answer_forwards_session(monkeypatch):
    resolved = []
    called = []

    def fake_resolve(session):
        resolved.append(session)
        return "resolved-token"

    def fake_submit(year, day, part, answer, session_token):
        called.append((year, day, part, answer, session_token))
        return "submission-result"

    monkeypatch.setattr("elf.client.resolve_session", fake_resolve)
    monkeypatch.setattr("elf.client.submit_answer", fake_submit)

    assert (
        submit_puzzle_answer(2023, 10, 2, answer="12345", session="explicit")
        == "submission-result"
    )
    assert resolved == ["explicit"]
    assert called == [(2023, 10, 2, "12345", "resolved-token")]


def test_get_private_leaderboard_without_view_key(monkeypatch):
    resolved = []
    captured = {}

    def fake_resolve(session):
        resolved.append(session)
        return "resolved-token"

    def fake_get_leaderboard(year, session_token, board_id, view_key, fmt):
        captured.update(
            {
                "year": year,
                "session_token": session_token,
                "board_id": board_id,
                "view_key": view_key,
                "fmt": fmt,
            }
        )
        return "leaderboard-data"

    monkeypatch.setattr("elf.client.resolve_session", fake_resolve)
    monkeypatch.setattr("elf.client.get_leaderboard", fake_get_leaderboard)

    assert (
        get_private_leaderboard(
            2023, board_id=10, session="explicit", fmt=OutputFormat.JSON
        )
        == "leaderboard-data"
    )
    assert resolved == ["explicit"]
    assert captured == {
        "year": 2023,
        "session_token": "resolved-token",
        "board_id": 10,
        "view_key": None,
        "fmt": OutputFormat.JSON,
    }


def test_get_private_leaderboard_with_view_key_prefers_env(monkeypatch):
    captured = {}

    def fake_get_leaderboard(year, session_token, board_id, view_key, fmt):
        captured.update(
            {
                "year": year,
                "session_token": session_token,
                "board_id": board_id,
                "view_key": view_key,
                "fmt": fmt,
            }
        )
        return "view-board"

    monkeypatch.delenv("AOC_SESSION", raising=False)
    monkeypatch.setenv("AOC_SESSION", "env-token")
    monkeypatch.setattr("elf.client.get_leaderboard", fake_get_leaderboard)

    assert (
        get_private_leaderboard(
            2024, board_id=20, view_key="abc", fmt=OutputFormat.MODEL
        )
        == "view-board"
    )
    assert captured == {
        "year": 2024,
        "session_token": "env-token",
        "board_id": 20,
        "view_key": "abc",
        "fmt": OutputFormat.MODEL,
    }


@pytest.mark.parametrize(
    "year,board_id",
    [
        (2014, 10),
        (2024, 0),
    ],
)
def test_get_private_leaderboard_invalid_inputs(year, board_id):
    with pytest.raises(ValueError):
        get_private_leaderboard(year, board_id=board_id)


def test_get_user_status_forwards_session(monkeypatch):
    resolved = []
    captured = {}

    def fake_resolve(session):
        resolved.append(session)
        return "resolved-token"

    def fake_get_status(year, session_token, fmt):
        captured.update({"year": year, "session_token": session_token, "fmt": fmt})
        return "status-data"

    monkeypatch.setattr("elf.client.resolve_session", fake_resolve)
    monkeypatch.setattr("elf.client.get_status", fake_get_status)

    assert (
        get_user_status(2023, session="token", fmt=OutputFormat.TABLE) == "status-data"
    )
    assert resolved == ["token"]
    assert captured == {
        "year": 2023,
        "session_token": "resolved-token",
        "fmt": OutputFormat.TABLE,
    }


def test_get_puzzle_input_uses_env_session(monkeypatch):
    captured = {}

    def fake_resolve(session):
        captured["resolved_from"] = session
        return "env-token"

    def fake_get_input(year, day, session):
        captured.update({"year": year, "day": day, "session": session})
        return "input-data"

    monkeypatch.setenv("AOC_SESSION", "env-token-raw")
    monkeypatch.setattr("elf.client.resolve_session", fake_resolve)
    monkeypatch.setattr("elf.client.get_input", fake_get_input)

    result = get_puzzle_input(2023, 5)
    assert result == "input-data"
    # resolve_session was called with None (no explicit session)
    assert captured["resolved_from"] is None
    # underlying client saw the resolved token
    assert captured["session"] == "env-token"


def test_get_user_status_uses_env_session(monkeypatch):
    captured = {}

    def fake_resolve(session):
        captured["resolved_from"] = session
        return "env-token"

    def fake_get_status(year, session_token, fmt):
        captured.update({"year": year, "session_token": session_token, "fmt": fmt})
        return "status-data"

    monkeypatch.setenv("AOC_SESSION", "env-token-raw")
    monkeypatch.setattr("elf.client.resolve_session", fake_resolve)
    monkeypatch.setattr("elf.client.get_status", fake_get_status)

    result = get_user_status(2023)
    assert result == "status-data"
    assert captured["resolved_from"] is None
    assert captured["session_token"] == "env-token"


def test_get_puzzle_input_raises_without_session(monkeypatch):
    def fake_resolve(session):
        raise RuntimeError("no session available")

    monkeypatch.delenv("AOC_SESSION", raising=False)
    monkeypatch.setattr("elf.client.resolve_session", fake_resolve)

    with pytest.raises(RuntimeError):
        get_puzzle_input(2023, 1)


def test_get_private_leaderboard_default_format_table(monkeypatch):
    captured = {}

    def fake_resolve(session):
        return "resolved-token"

    def fake_get_leaderboard(year, session_token, board_id, view_key, fmt):
        captured.update(
            {
                "year": year,
                "session_token": session_token,
                "board_id": board_id,
                "view_key": view_key,
                "fmt": fmt,
            }
        )
        return "leaderboard-data"

    monkeypatch.setenv("AOC_SESSION", "env-token")
    monkeypatch.setattr("elf.client.resolve_session", fake_resolve)
    monkeypatch.setattr("elf.client.get_leaderboard", fake_get_leaderboard)

    result = get_private_leaderboard(2024, board_id=42)
    assert result == "leaderboard-data"
    assert captured["fmt"] == OutputFormat.MODEL


def test_get_user_status_default_format_table(monkeypatch):
    captured = {}

    def fake_resolve(session):
        return "resolved-token"

    def fake_get_status(year, session_token, fmt):
        captured.update({"year": year, "session_token": session_token, "fmt": fmt})
        return "status-data"

    monkeypatch.setenv("AOC_SESSION", "env-token")
    monkeypatch.setattr("elf.client.resolve_session", fake_resolve)
    monkeypatch.setattr("elf.client.get_status", fake_get_status)

    result = get_user_status(2024)
    assert result == "status-data"
    assert captured["fmt"] == OutputFormat.MODEL


def test_get_private_leaderboard_view_key_without_session(monkeypatch):
    captured = {}

    def fake_get_leaderboard(year, session_token, board_id, view_key, fmt):
        captured.update(
            {
                "year": year,
                "session_token": session_token,
                "board_id": board_id,
                "view_key": view_key,
                "fmt": fmt,
            }
        )
        return "view-board"

    monkeypatch.delenv("AOC_SESSION", raising=False)
    monkeypatch.setattr("elf.client.get_leaderboard", fake_get_leaderboard)

    result = get_private_leaderboard(
        2024, board_id=123, view_key="abc123", fmt=OutputFormat.JSON
    )
    assert result == "view-board"
    # Depending on your design, this might be None or some sentinel
    assert captured["session_token"] is None
    assert captured["view_key"] == "abc123"
