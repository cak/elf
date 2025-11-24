import os
import platform
from pathlib import Path


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


def get_cache_guess_file(year: int, day: int) -> Path:
    """Return path to guesses cache CSV."""
    return get_cache_dir() / f"{year:04d}" / f"{day:02d}" / "guesses.csv"


def get_cache_input_file(year: int, day: int) -> Path:
    """Return path to input cache file."""
    return get_cache_dir() / f"{year:04d}" / f"{day:02d}" / "input.txt"
