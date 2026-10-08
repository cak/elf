import webbrowser

from .models import OpenKind
from .utils import validate_event_day


def open_page(year: int, day: int, kind: OpenKind) -> str:
    validate_event_day(year, day)

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
