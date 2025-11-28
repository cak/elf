# elf: Advent of Code helper for Python

<p align="center">
  <img src="https://snally.com/assets/elf-logo.png" width="200" alt="elf logo">
</p>

A fast, modern Advent of Code CLI with caching, guardrails, leaderboards, and a lightweight Python API.

Works on macOS, Linux, and Windows. Most networked commands require an AoC session cookie (`AOC_SESSION`).

![PyPI](https://img.shields.io/pypi/v/elf.svg) ![License: MIT](https://img.shields.io/badge/License-MIT-success.svg) ![AoC Ready](https://img.shields.io/badge/Advent%20of%20Code-Ready-00cc66?logo=data:image/png;base64,<tiny_pixel_icon>) ![North Pole API Compliant](https://img.shields.io/badge/North%20Pole%20API-Compliant-blue)

## Why I Built This

Advent of Code has become one of my favorite Christmas traditions. I am never the fastest solver, and some puzzles definitely keep me humble, but the challenges always spark new ideas and mark the start of the holiday season for me.

Thank you to **Eric Wastl**, the creator of [Advent of Code](https://adventofcode.com/). His work brings an incredible community together every December and inspires people around the world to learn, explore new ideas, and enjoy the joy of programming puzzles.

After refining a small helper tool I have used personally for the past few years, I decided to turn it into a package others can benefit from as well. I originally built an early version for my own workflows in [my personal AoC repo](https://github.com/cak/advent-of-code/tree/dc9c02a5a77a36b725a8e01cff18a6de46e0db0d?tab=readme-ov-file#%EF%B8%8F-automating-tasks-with-the-elf-cli).

If Advent of Code is part of your December ritual too, I hope this little elf makes the journey smoother, more fun, and a bit more magical.

## Highlights

- One-line input fetch with **local caching** (never re-downloads)
- **Submission guardrails:** locked puzzle check, cooldown messages, and duplicate/high/low detection from cached guesses
- Private leaderboards as **tables**, **JSON**, or **Pydantic models**
- **Status calendar** (table, JSON, or model) with AoC++ badge support
- Guess history viewer (per part) built in
- `elf open` opens puzzle, input, or main AoC pages.
- CLI (`elf ...`) and importable library (`import elf`)

## Installation

### Using uv (recommended)

#### Install as tool

```bash
uv tool install elf
```

#### Inside a project

```sh
uv add elf
```

### Using pip

```bash
pip install elf
```

### Requirements

- Python 3.11 or newer
- An Advent of Code account
- `AOC_SESSION` cookie set in your environment for most commands

## Configure your AoC Session

Most features in elf require your Advent of Code session cookie so the CLI can access your personal puzzle inputs and progress.

To get it:

1. Log in to https://adventofcode.com using GitHub, Google, or Reddit.
2. Open your browser’s developer tools.
   - Chrome: View → Developer → Developer Tools
   - Firefox: Tools → Browser Tools → Web Developer Tools
3. Go to the **Application** (Chrome) or **Storage** (Firefox) tab.
4. Look for **Cookies** for the domain `adventofcode.com`.
5. Find the cookie named **`session`**.
6. Copy the value (a long hex string).
7. Set it as an environment variable:

```bash
export AOC_SESSION="your-session-token"
```

Most commands require this. You can also pass it via `--session` in the CLI or `session=` in the API.

## CLI Documentation

### `elf --help`

```sh
Usage: elf [OPTIONS] COMMAND [ARGS]...

Advent of Code CLI

Options:
  --version, -V
  --debug
  --install-completion
  --show-completion
  --help

Commands:
  input        Fetch the input for a given year/day
  answer       Submit an answer
  leaderboard  Fetch/display a private leaderboard
  guesses      Show cached guesses
  status       Show yearly star status
  open         Open puzzle/input/website
  cache        Show cache information
```

Enable detailed tracebacks with `--debug` or `ELF_DEBUG=1` when troubleshooting.

---

## Commands

### `elf input`

Fetch puzzle input with caching. Requires a session cookie.

```sh
Usage: elf input [YEAR] [DAY]

Options:
  --session TEXT   AOC session cookie (env: AOC_SESSION)
```

Defaults:

- `year`: current year
- `day`: current day in December, otherwise 1 (Dec 1)
- Caches to `~/.cache/elf/<year>/<day>/input.txt` (or platform equivalent)

### `elf answer`

Submit an answer with safety guardrails. Requires a session cookie. Guardrails use your local guess cache to short-circuit duplicate answers and infer too-high/too-low for integer guesses.

```sh
Usage: elf answer YEAR DAY LEVEL ANSWER

Options:
  --session TEXT  AOC session cookie
```

Behaviors:

- Year and day are required to avoid accidental submissions.
- Detects **locked puzzles** (year >= current year) and shows unlock timestamp
- Identifies **too high / too low / duplicate** guesses from local cache
- Writes to guess cache automatically (per part)

Example errors:

```sh
❄️ Puzzle YYYY‑MM‑DD not unlocked yet
1234 is not correct.
You submitted an answer recently. Please wait...
12345 is correct. Star awarded.
```

### `elf guesses`

Display local guess history (per part). Requires a cached `guesses.csv` from previous submissions.

```sh
Usage: elf guesses [YEAR] [DAY]
```

Example table:

```sh
Time (UTC)      Guess  Status
2024‑12‑05 ...  959    too_low
2024‑12‑05 ...  6951   correct
```

### `elf leaderboard`

Fetch private leaderboards. Provide a view key for read-only access or a session cookie for authenticated access. A view key is the read-only share token you can generate on your AoC leaderboard page.

```sh
Usage: elf leaderboard YEAR BOARD_ID

Options:
  --view-key TEXT
  --session TEXT
  --format table|json|model
```

Supports:

- **table:** pretty Rich table
- **json:** raw JSON
- **model:** structured Pydantic model

### `elf status`

View your Advent of Code star calendar. Requires a session cookie.

```sh
Usage: elf status [YEAR]

Options:
  --session TEXT
  --format table|json|model
```

Defaults:
- `year`: current year if omitted

Prints stars for each day and your AoC++ badge.

### `elf open`

Opens puzzle pages in your browser.

```sh
Usage: elf open [YEAR] [DAY]

Options:
  --kind puzzle|input|website
```

### `elf cache`

Display cache directory information.

```sh
Usage: elf cache
```

Shows:

- Cache root directory (platform-aware)
- Number of cached files
- Reminder to delete the directory manually to clear cache

---

## Caching Behavior

- Default cache dir: macOS/Linux `~/.cache/elf`, Windows `%LOCALAPPDATA%\elf`
- Override location with `ELF_CACHE_DIR` (respects `XDG_CACHE_HOME` on Linux)
- Inputs stored under: `<cache>/<year>/<day>/input.txt`
- Guess history stored as `<cache>/<year>/<day>/guesses.csv`
- Duplicate/high/low guesses are short‑circuited locally when possible
- Delete the cache directory to clear everything

---

## Library Usage

```python
from elf import (
    get_puzzle_input,
    submit_puzzle_answer,
    get_private_leaderboard,
    get_user_status,
    OutputFormat,
)

# AOC_SESSION is used automatically if not passed explicitly
input_text = get_puzzle_input(2023, 5)

result = submit_puzzle_answer(2023, 5, 1, "12345")
print(result.is_correct, result.message)

leaderboard = get_private_leaderboard(
    2023, session=None, board_id=123456, view_key=None, fmt=OutputFormat.MODEL
)

status = get_user_status(2023, fmt=OutputFormat.TABLE)
print(status)
```

### Puzzle Helpers

`elf.helpers` includes some small utilities you can use in your own AoC solutions:

```python
from elf.helpers import parse_input, read_test_input, timer
```

### Leaderboard Example

```sh
❯ elf leaderboard 2024 3982840
              Advent of Code 2024 – Private Leaderboard
┏━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Rank ┃ Name           ┃ Stars ┃ Local Score ┃ Last Star (UTC)     ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│    1 │ User A         │    45 │         900 │ 2024-12-26 00:53:17 │
│    2 │ User B         │    45 │         855 │ 2024-12-26 00:53:56 │
│    3 │ User C         │    36 │         622 │ 2024-12-26 03:29:21 │
└──────┴────────────────┴───────┴─────────────┴─────────────────────┘
```

JSON format:

```sh
elf leaderboard 2024 3982840 --format json
```

Model format (Pydantic):

```python
lb = get_private_leaderboard(2024, board_id=3982840, fmt=OutputFormat.MODEL)
members = sorted(lb.members.values(), key=lambda m: (-m.local_score, -m.stars))
print(members[0].name, members[0].stars)
```

### Status Example

```sh
❯ elf status 2023
Advent of Code
  2023 – cak
(AoC++) [34⭐]
┏━━━━━┳━━━━━━━┓
┃ Day ┃ Stars ┃
┡━━━━━╇━━━━━━━┩
│   1 │  ★★   │
│   2 │  ★★   │
│   3 │  ★★   │
│   4 │  ★☆   │
│   5 │  ★☆   │
│   6 │  ★★   │
│   7 │  ★★   │
│   8 │  ★☆   │
│   9 │  ☆☆   │
│  10 │  ☆☆   │
│  .. │  ..   │
│  25 │  ☆☆   │
└─────┴───────┘
```

JSON format:

```sh
elf status 2023 --format json
```

Model format:

```python
status = get_user_status(2023, fmt=OutputFormat.MODEL)
print(status.days[0].day, status.days[0].stars)
```

---

## Special Thanks

Thanks to **Solos** for donating the `elf` PyPI name.
