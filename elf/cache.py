import os
import platform
from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile


def get_cache_dir() -> Path:
    """Return the platform-appropriate cache directory for elf.

    Priority:
        1. ELF_CACHE_DIR environment variable
        2. Windows LOCALAPPDATA
        3. XDG_CACHE_HOME
        4. ~/.cache/elf
    """
    if env_cache_dir := os.getenv("ELF_CACHE_DIR"):
        return Path(os.path.expandvars(os.path.expanduser(env_cache_dir))).resolve()

    system = platform.system()

    if system == "Windows":
        base = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache"))

    return base / "elf"


def get_cache_scope(*credentials: str | None) -> str | None:
    """Return an opaque cache namespace for authentication credentials."""
    values = [value for value in credentials if value]
    if not values:
        return None
    digest = sha256("\0".join(values).encode("utf-8")).hexdigest()
    return digest[:24]


def get_session_cache_scope(session_token: str) -> str:
    """Return the shared input/guess/leaderboard namespace for one session."""
    scope = get_cache_scope("session", session_token)
    assert scope is not None
    return scope


def get_leaderboard_cache_scope(
    session_token: str | None, view_key: str | None
) -> str:
    """Return a namespace that cannot confuse session and view credentials."""
    if view_key is None and session_token is not None:
        return get_session_cache_scope(session_token)
    scope = get_cache_scope("leaderboard-view", session_token, view_key)
    assert scope is not None
    return scope


def _cache_root(scope: str | None) -> Path:
    if scope is None:
        return get_cache_dir()
    return get_cache_dir() / "accounts" / scope


def get_cache_guess_file(year: int, day: int, scope: str | None = None) -> Path:
    """Return path to guesses cache CSV."""
    return _cache_root(scope) / f"{year:04d}" / f"{day:02d}" / "guesses.csv"


def get_cache_input_file(year: int, day: int, scope: str | None = None) -> Path:
    """Return path to input cache file."""
    return _cache_root(scope) / f"{year:04d}" / f"{day:02d}" / "input.txt"


def get_cache_leaderboard_file(
    year: int, board_id: int, scope: str | None = None
) -> Path:
    """Return path to a cached private leaderboard response."""
    return (
        _cache_root(scope)
        / f"{year:04d}"
        / "leaderboards"
        / f"{board_id}.json"
    )


def find_scoped_guess_files(year: int, day: int) -> list[Path]:
    """Find account-scoped guess caches without requiring live credentials."""
    pattern = f"accounts/*/{year:04d}/{day:02d}/guesses.csv"
    return sorted(get_cache_dir().glob(pattern))


def migrate_legacy_cache_file(legacy: Path, scoped: Path) -> None:
    """Copy an unscoped pre-1.2 cache into the current account namespace once."""
    if scoped.exists() or not legacy.is_file():
        return
    write_cache_text(scoped, legacy.read_text(encoding="utf-8"))


def write_cache_text(path: Path, content: str) -> None:
    """Atomically replace a UTF-8 cache file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as temporary:
            temporary.write(content)
            temporary_name = temporary.name
        Path(temporary_name).replace(path)
    finally:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)
