import os

import httpx
import pytest

import elf.aoc_client
from elf.aoc_client import (
    AOCClient,
    _default_user_agent,
    _user_agent_prefix,
    _validate_user_agent,
)


@pytest.fixture
def aoc_client(monkeypatch):
    def _make():
        monkeypatch.setattr(elf.aoc_client, "_shared_client", None)
        return AOCClient("fake_session")

    return _make


@pytest.mark.parametrize(
    ("aoc_user_agent", "ok"),
    [("", False), ("invalid", False), ("valid@email.com", True)],
)
def test_user_agent_header_validation(monkeypatch, aoc_user_agent, ok):
    monkeypatch.setenv("AOC_USER_AGENT", aoc_user_agent)
    user_agent = os.getenv("AOC_USER_AGENT")
    assert _validate_user_agent(user_agent) == ok


def test_user_agent_set_in_AOCClient(monkeypatch, aoc_client):
    user_agent = "valid@email.com"
    monkeypatch.setenv("AOC_USER_AGENT", user_agent)
    client = aoc_client()
    httpx_client: httpx.Client = client._client
    user_agent_header = httpx_client.headers.get("User-Agent", "")
    assert user_agent in user_agent_header
    assert _user_agent_prefix in user_agent_header


def test_default_user_agent_set_in_AOCClient(monkeypatch, aoc_client):
    # Simulate no AOC_USER_AGENT set in the environment so we hit the default UA path
    monkeypatch.delenv("AOC_USER_AGENT", raising=False)

    # Ensure we get a fresh client instead of reusing a previously-initialized one
    monkeypatch.setattr(elf.aoc_client, "_shared_client", None)

    with pytest.warns(RuntimeWarning):
        client = aoc_client()

    httpx_client: httpx.Client = client._client
    user_agent_header = httpx_client.headers.get("User-Agent", "")
    assert _default_user_agent in user_agent_header
    assert _user_agent_prefix in user_agent_header
