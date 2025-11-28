import webbrowser

from .models import OpenKind


def open_page(year: int, day: int, kind: OpenKind) -> str:
    if year < 2015:
        raise ValueError(f"Invalid year {year!r}. Advent of Code started in 2015.")
    if not 1 <= day <= 25:
        raise ValueError(f"Invalid day {day!r}. Advent of Code days are 1–25.")

    url = "https://adventofcode.com/"

    match kind:
        case OpenKind.PUZZLE:
            url = f"https://adventofcode.com/{year}/day/{day}"
        case OpenKind.INPUT:
            url = f"https://adventofcode.com/{year}/day/{day}/input"
        case OpenKind.WEBSITE:
            url = "https://adventofcode.com/"

    webbrowser.open_new_tab(url)

    msg = f"🌟 Opened {kind.value} page: [blue underline]{url}[/blue underline]"

    return msg
