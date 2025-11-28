import json
import re

import httpx
from bs4 import BeautifulSoup
from bs4.element import Tag
from rich.table import Table

from .aoc_client import AOCClient
from .exceptions import StatusFetchError
from .models import DayStatus, OutputFormat, YearStatus
from .utils import current_aoc_year, handle_http_errors, resolve_session


def get_status(
    year: int, session: str | None, fmt: OutputFormat
) -> YearStatus | str | Table:
    session_token = resolve_session(session)

    now_year = current_aoc_year()
    if year > now_year:
        raise ValueError(
            f"Invalid year {year!r}. Advent of Code years are up to {now_year}."
        )
    if year < 2015:
        raise ValueError(f"Invalid year {year!r}. Advent of Code started in 2015.")

    with AOCClient(session_token=session_token) as client:
        try:
            response = client.fetch_event(year)
        except httpx.TimeoutException as exc:
            raise StatusFetchError(
                "Timed out while fetching status. Try again or check your network."
            ) from exc
        except httpx.RequestError as exc:
            raise StatusFetchError(
                f"Network error while connecting to Advent of Code: {exc}"
            ) from exc

    handle_http_errors(
        response,
        exc_cls=StatusFetchError,
        not_found_message=f"Event page not found for year={year} (HTTP 404).",
        bad_request_message="Bad request (HTTP 400). Your session token may be invalid.",
        server_error_message="Server error from Advent of Code (HTTP {status_code}). Your session token may be invalid.",
        unexpected_status_message="Unexpected HTTP error: {status_code}.",
    )

    logged_in = parse_login_state(response.text)

    if not logged_in:
        raise StatusFetchError(
            "Session cookie invalid or expired. "
            "Update AOC_SESSION with a valid 'session' cookie from your browser."
        )

    try:
        year_status = parse_year_status(response.text)
    except Exception as exc:
        raise StatusFetchError("Failed to parse Advent of Code status page.") from exc

    match fmt:
        case OutputFormat.MODEL:
            return year_status
        case OutputFormat.JSON:
            return json.dumps(year_status.model_dump(), indent=2)
        case OutputFormat.TABLE:
            return build_year_status_table(year_status)
        case _:
            raise ValueError(f"Unsupported output format: {fmt}")


def _parse_total_stars(user_div: Tag) -> int:
    """
    Parse total stars from the header, e.g.:
    <span class="star-count">11*</span>
    """
    star_span = user_div.select_one(".star-count")
    if not star_span:
        return 0

    text = star_span.get_text(strip=True)  # "11*"
    # strip trailing '*' and anything non-digit
    m = re.search(r"(\d+)", text)
    return int(m.group(1)) if m else 0


def _parse_username_and_supporter(user_div: Tag) -> tuple[str, bool]:
    """
    user_div looks like:
      <div class="user">
        cak <a ... class="supporter-badge">...</a> <span class="star-count">11*</span>
      </div>
    """
    # first text node is the username
    username = ""
    for child in user_div.contents:
        if isinstance(child, str):
            username = child.strip()
            if username:
                break

    is_supporter = user_div.select_one(".supporter-badge") is not None
    return username, is_supporter


def _stars_from_aria_and_classes(
    aria_label: str | None,
    classes: list[str],
) -> int:
    """
    Determine star count using only aria-label and day-level classes.

    - aria-label: "Day N, one star" / "Day N, two stars" / "Day N"
    - classes: "calendar-complete" (1 star), "calendar-verycomplete" (2 stars)
    """
    aria_label = aria_label or ""

    # 1. aria-label is authoritative
    if "two stars" in aria_label:
        return 2
    if "one star" in aria_label:
        return 1

    # 2. fall back to classes
    if "calendar-verycomplete" in classes:
        return 2
    if "calendar-complete" in classes:
        return 1

    # 3. otherwise: locked / zero stars
    return 0


def parse_year_status(html: str) -> YearStatus:
    soup = BeautifulSoup(html, "html.parser")

    # ---- Header: username, supporter flag, total stars ----
    user_div = soup.select_one("header .user")
    if not user_div:
        raise ValueError("Could not find user info in header")

    username, is_supporter = _parse_username_and_supporter(user_div)
    total_stars = _parse_total_stars(user_div)

    # ---- Year ----
    year_a = soup.select_one("h1.title-event a")
    if not year_a:
        raise ValueError("Could not find year in header")
    year = int(year_a.get_text(strip=True))

    # ---- Calendar days ----
    calendar = soup.select_one("pre.calendar")
    if not calendar:
        raise ValueError("Could not find calendar <pre>")

    day_statuses: list[DayStatus] = []

    # Each day is an <a> with class "calendar-dayN"
    for a in calendar.select("a[class^='calendar-day']"):
        aria_label = a.get("aria-label", "") or ""
        aria_label_str = str(aria_label) if aria_label else None

        # Try day number from aria-label first
        day_num: int | None = None
        m = re.search(r"Day\s+(\d+)", str(aria_label))
        if m:
            day_num = int(m.group(1))

        if day_num is None:
            # Fallback to the inner span with class "calendar-day"
            day_span = a.select_one(".calendar-day")
            if not day_span:
                continue
            day_num = int(day_span.get_text(strip=True))

        href_raw = a.get("href", "")
        href = str(href_raw) if href_raw else ""

        classes = a.get("class") or []
        if isinstance(classes, str):
            classes = classes.split()
        elif not isinstance(classes, list):
            classes = list(classes) if classes else []
        stars = _stars_from_aria_and_classes(aria_label_str, classes)

        day_statuses.append(
            DayStatus(
                day=day_num,
                stars=stars,
                href=href,
                aria_label=str(aria_label) if aria_label else "",
            )
        )

    # Sort by day number to be safe
    day_statuses.sort(key=lambda d: d.day)

    return YearStatus(
        year=year,
        username=username,
        is_supporter=is_supporter,
        total_stars=total_stars,
        days=day_statuses,
    )


def build_year_status_table(status: YearStatus) -> Table:
    """
    Build a Rich Table summarizing a user's AoC progress for a year.
    """
    supporter_suffix = " (AoC++)" if status.is_supporter else ""
    title = f"Advent of Code {status.year} – {status.username}{supporter_suffix} [{status.total_stars}⭐]"

    table = Table(title=title, show_lines=False)

    table.add_column("Day", justify="right", style="cyan", no_wrap=True)
    table.add_column("Stars", justify="center", style="yellow", no_wrap=True)

    for day in sorted(status.days, key=lambda d: d.day):
        # Render stars as a 2-star gauge: ★ for earned, ☆ for missing
        stars_str = "★" * day.stars + "☆" * (2 - day.stars)

        # Row coloring based on completion
        if day.stars == 2:
            row_style = "bold green"
        elif day.stars == 1:
            row_style = "bold yellow"
        else:
            row_style = "dim"

        table.add_row(str(day.day), stars_str, style=row_style)

    return table


def parse_login_state(html: str) -> bool:
    """
    Returns True if user is logged in.
    """
    has_login = "/auth/login" in html
    has_settings = "/settings" in html

    # Logged in = settings visible AND login missing
    if has_settings and not has_login:
        return True

    # Otherwise assume logged out
    return False
