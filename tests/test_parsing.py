from elf.leaderboard import format_leaderboard_as_table
from elf.models import Leaderboard
from elf.status import build_year_status_table, parse_login_state, parse_year_status


def test_leaderboard_model_accepts_string_keys_and_formats_table():
    payload = {
        "num_days": 25,
        "event": "Advent of Code 2025",
        "day1_ts": 1700000000,
        "owner_id": 123,
        "members": {
            "123": {
                "id": 123,
                "name": "Elf One",
                "last_star_ts": 1700000123,
                "stars": 45,
                "local_score": 900,
                "completion_day_level": {
                    "1": {
                        "1": {"get_star_ts": 1700000001, "star_index": 1},
                    }
                },
            },
            "456": {
                "id": 456,
                "name": "Elf Two",
                "last_star_ts": 1700000456,
                "stars": 38,
                "local_score": 750,
                "completion_day_level": {},
            },
        },
    }

    leaderboard = Leaderboard.model_validate(payload)

    assert list(leaderboard.members.keys()) == [123, 456]
    table = format_leaderboard_as_table(leaderboard)
    assert table.title and "Advent of Code 2025" in table.title
    assert table.row_count == 2


def test_status_parsing_handles_basic_calendar_html():
    html = """
    <html>
      <header>
        <div class="user">
          elf@example.com
          <a class="supporter-badge" href="/support">AoC++</a>
          <span class="star-count">5*</span>
        </div>
      </header>
      <h1 class="title-event">
        <a>2025</a>
      </h1>
      <pre class="calendar">
        <a class="calendar-day1 calendar-verycomplete" aria-label="Day 1, two stars">
          <span class="calendar-day">1</span>
        </a>
        <a class="calendar-day2 calendar-complete" aria-label="Day 2, one star">
          <span class="calendar-day">2</span>
        </a>
        <a class="calendar-day3" aria-label="Day 3">
          <span class="calendar-day">3</span>
        </a>
      </pre>
      <a href="/settings">Settings</a>
    </html>
    """

    assert parse_login_state(html)

    status = parse_year_status(html)
    assert status.year == 2025
    assert status.total_stars == 5
    assert len(status.days) == 3

    table = build_year_status_table(status)
    assert table.row_count == 3
    assert table.title and "2025" in table.title
