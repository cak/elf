import pytest

from elf.client import (
    get_private_leaderboard,
    get_puzzle_input,
    get_user_status,
    submit_puzzle_answer,
)
from elf.models import OutputFormat


def test_get_puzzle_input_forwards_explicit_session(monkeypatch):
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

    result = get_puzzle_input(2023, 5, session="manual-session")

    assert result == "input-data"
    assert resolved == ["manual-session"]
    assert called == [(2023, 5, "resolved-token")]


def test_get_puzzle_input_uses_env_session_when_not_provided(monkeypatch):
    captured = {}

    def fake_resolve(session):
        captured["resolved_from"] = session
        return "env-resolved-token"

    def fake_get_input(year, day, session):
        captured.update({"year": year, "day": day, "session": session})
        return "input-data"

    monkeypatch.setenv("AOC_SESSION", "env-token")
    monkeypatch.setattr("elf.client.resolve_session", fake_resolve)
    monkeypatch.setattr("elf.client.get_input", fake_get_input)

    result = get_puzzle_input(2024, 1)

    assert result == "input-data"
    # High-level helper passes None into resolve_session, letting it
    # decide how to use env vars.
    assert captured["resolved_from"] is None
    assert captured["year"] == 2024
    assert captured["day"] == 1
    assert captured["session"] == "env-resolved-token"


def test_get_puzzle_input_raises_without_session(monkeypatch):
    def fake_resolve(session):
        raise RuntimeError("no session available")

    monkeypatch.delenv("AOC_SESSION", raising=False)
    monkeypatch.setattr("elf.client.resolve_session", fake_resolve)

    with pytest.raises(RuntimeError, match="no session available"):
        get_puzzle_input(2023, 1)


def test_submit_puzzle_answer_forwards_session_and_args(monkeypatch):
    resolved = []
    submitted = []

    def fake_resolve(session):
        resolved.append(session)
        return "resolved-token"

    def fake_submit(year, day, level, answer, session_token):
        submitted.append((year, day, level, answer, session_token))
        return "submission-result"

    monkeypatch.setattr("elf.client.resolve_session", fake_resolve)
    monkeypatch.setattr("elf.client.submit_answer", fake_submit)

    result = submit_puzzle_answer(
        year=2023,
        day=2,
        part=1,
        answer="12345",
        session="manual-session",
    )

    assert result == "submission-result"
    assert resolved == ["manual-session"]
    assert submitted == [(2023, 2, 1, "12345", "resolved-token")]


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

    result = get_private_leaderboard(
        2023, board_id=10, session="explicit-session", fmt=OutputFormat.JSON
    )

    assert result == "leaderboard-data"
    assert resolved == ["explicit-session"]
    assert captured == {
        "year": 2023,
        "session_token": "resolved-token",
        "board_id": 10,
        "view_key": None,
        "fmt": OutputFormat.JSON,
    }


def test_get_private_leaderboard_with_view_key_allows_none_session(monkeypatch):
    """
    When a view_key is provided and no session is supplied, the current
    implementation allows session_token to be None and does NOT call
    resolve_session. This test encodes that behavior.
    """
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
        return "leaderboard-data"

    # No env session, no explicit session
    monkeypatch.delenv("AOC_SESSION", raising=False)
    monkeypatch.setattr("elf.client.get_leaderboard", fake_get_leaderboard)

    result = get_private_leaderboard(
        2024,
        board_id=123,
        view_key="view-key-abc",
        fmt=OutputFormat.JSON,
    )

    assert result == "leaderboard-data"
    assert captured["year"] == 2024
    assert captured["board_id"] == 123
    assert captured["view_key"] == "view-key-abc"
    # Key point: session_token is None in this scenario
    assert captured["session_token"] is None
    assert captured["fmt"] == OutputFormat.JSON


@pytest.mark.parametrize(
    "year, board_id",
    [
        (None, 123),
        (2023, None),
        (None, None),
    ],
)
def test_get_private_leaderboard_invalid_inputs(year, board_id):
    """
    With the current implementation, passing None for year or board_id
    leads to a TypeError from underlying comparisons (e.g., year < 2015).

    If you later add explicit validation in get_private_leaderboard and
    raise ValueError instead, you can update this test to expect ValueError.
    """
    with pytest.raises(TypeError):
        get_private_leaderboard(year, board_id=board_id)


def test_get_private_leaderboard_default_format_model(monkeypatch):
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
    # Default for API is currently OutputFormat.MODEL
    assert captured["fmt"] == OutputFormat.MODEL
    assert captured["session_token"] == "resolved-token"


def test_get_user_status_forwards_explicit_session(monkeypatch):
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

    result = get_user_status(2023, session="manual-session", fmt=OutputFormat.JSON)

    assert result == "status-data"
    assert resolved == ["manual-session"]
    assert captured["year"] == 2023
    assert captured["session_token"] == "resolved-token"
    assert captured["fmt"] == OutputFormat.JSON


def test_get_user_status_uses_env_session(monkeypatch):
    captured = {}

    def fake_resolve(session):
        captured["resolved_from"] = session
        return "env-resolved-token"

    def fake_get_status(year, session_token, fmt):
        captured.update({"year": year, "session_token": session_token, "fmt": fmt})
        return "status-data"

    monkeypatch.setenv("AOC_SESSION", "env-token")
    monkeypatch.setattr("elf.client.resolve_session", fake_resolve)
    monkeypatch.setattr("elf.client.get_status", fake_get_status)

    result = get_user_status(2023)

    assert result == "status-data"
    assert captured["resolved_from"] is None
    assert captured["session_token"] == "env-resolved-token"
    assert captured["fmt"] == OutputFormat.MODEL
