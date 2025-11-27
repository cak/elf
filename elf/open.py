import webbrowser

from .models import OpenKind


def open_page(year: int, day: int, kind: OpenKind) -> str:
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
