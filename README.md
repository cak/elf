# elf — Advent of Code helper for Python

Fetch and cache puzzle inputs, submit answers safely, inspect your private leaderboards, and track your yearly progress — from a single CLI or a small Python API.

## Highlights

- One-line fetch for puzzle input with **local caching** (never re-downloads)
- **Safe submissions** with guardrails, duplicate/high/low guess detection, and cooldown awareness
- View private leaderboards as **tables**, **JSON**, or **Pydantic models**
- Show your **personal calendar/status** for any year
- Optional **guess cache** to avoid re-submitting incorrect answers
- Works as both a CLI (`elf …`) and importable library (`import elf`)

## Installation

### Using uv (recommended)

```bash
uv tool install elf
# or, inside a project:
uv add elf
```

### Using pip

```bash
pip install elf
```

Requirements: Python 3.11+.

## Configure your AoC session

Grab the `session` cookie from Advent of Code and set it as an environment variable:

```bash
export AOC_SESSION="your-session-token"
```

Most commands require this. You can also pass it via `--session` in the CLI or `session=` in the API.

## CLI quickstart

```bash
elf input --year 2023 --day 5                       # Print puzzle input (cached)
elf answer --year 2023 --day 5 --level 1 "12345"    # Submit an answer
elf leaderboard --year 2023 --board-id 123456       # Show a private leaderboard
elf status --year 2023                              # Show your calendar/stars
elf guesses --year 2023 --day 5                     # Inspect cached guesses
elf open --year 2023 --day 5 --kind puzzle          # Open puzzle/input/site
elf cache                                           # Show cache location/details
```

Useful flags:

- `--format table|json|model` for leaderboard/status output
- `--festive / --no-festive` toggles emoji/colored responses
- Year/day default to “today,” capped at Dec 25 of the current year

Run `elf --help` or any subcommand with `--help` for full options.

## Library usage

```python
from elf import (
    get_puzzle_input,
    submit_puzzle_answer,
    get_private_leaderboard,
    get_user_status,
    OutputFormat,
)

input_text = get_puzzle_input(2023, 5)

result = submit_puzzle_answer(2023, 5, 1, "12345")
print(result.is_correct, result.message)

leaderboard = get_private_leaderboard(
    2023, session=None, board_id=123456, view_key=None, fmt=OutputFormat.MODEL
)

status = get_user_status(2023, fmt=OutputFormat.TABLE)
print(status)
```

## Caching behavior

- Inputs: stored under `~/.cache/elf/<year>/<day>/input.txt`  
  (override with `ELF_CACHE_DIR`)
- Guesses: stored as CSV per day; duplicate/high/low guesses are short-circuited locally
- Delete the cache directory at any time to clear everything

## Notes and tips

- AoC puzzles unlock at **midnight America/New_York**; requests before unlock raise a friendly error.
- View-key leaderboards still require a session cookie (per AoC rules).
- Internal implementation uses pattern matching; Python 3.11+ required.

## Special Thanks to Solos

Special thanks to [Solos](https://github.com/solos) for donating the `elf` package name on PyPI.
