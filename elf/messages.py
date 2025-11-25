import random

from elf.models import Guess


def get_positive_message(answer: int | str, *, festive: bool = True) -> str:
    """General “nice job” feedback, not necessarily tied to star awarding."""
    if not festive:
        return f"{answer} is correct."

    messages: list[str] = [
        f"[bold green]🎉 {answer} is correct! You’ve lit up another star on the tree. ✨[/bold green]",
        f"[bold green]🎄 {answer} is right on the money. The calendar ticks to the next puzzle! 🎄[/bold green]",
        f"[bold green]✨ Nailed it! {answer} matches the puzzle output exactly. ✨[/bold green]",
        f"[bold green]🎁 {answer} is spot on. Time to unwrap the next part. 🎁[/bold green]",
        f"[bold green]🌟 Great job! {answer} shines brighter than a gold star. 🌟[/bold green]",
        f"[bold green]☃️ {answer} is correct. The elves added it to today’s solved list. ☃️[/bold green]",
        f"[bold green]🍪 {answer} is right. You’ve earned a debugging cookie. 🍪[/bold green]",
        f"[bold green]🧝 {answer} is correct. The workshop quietly nods in approval. 🧝[/bold green]",
    ]
    return random.choice(messages)


def get_negative_message(answer: int, *, festive: bool = True) -> str:
    """Generic “not quite” feedback (no high/low hint)."""
    if not festive:
        return "That answer is not correct. Check your logic and try again."

    messages: list[str] = [
        "[bold yellow]🤔 Not quite. Give the puzzle text another careful read.[/bold yellow]",
        "[bold yellow]🎄 Close, but not there yet. Check edge cases and off-by-ones.[/bold yellow]",
        "[bold yellow]🌨️ That output missed. Compare a few sample inputs by hand.[/bold yellow]",
        "[bold yellow]🎅 Not the right answer. Walk through your logic step by step.[/bold yellow]",
        "[bold yellow]🦌 The elves think you’re close. Re-check your parsing or types.[/bold yellow]",
        "[bold yellow]🍭 That guess didn’t land. Add a few more print/debug lines.[/bold yellow]",
        "[bold yellow]✨ Almost there. Time for one more small refactor or check.[/bold yellow]",
        "[bold yellow]❄️ No luck this time. Don’t give up—AoC is all about iteration.[/bold yellow]",
        "[bold yellow]🌟 Keep going. Every “wrong” run gets you nearer the star.[/bold yellow]",
        "[bold yellow]☃️ Snow worries. Try a different approach or data structure.[/bold yellow]",
    ]
    return random.choice(messages)


def get_correct_answer_message(answer: int | str, *, festive: bool = True) -> str:
    """When AoC confirms the answer is correct and awards a star."""
    if not festive:
        return f"{answer} is correct. Star awarded."

    messages: list[str] = [
        f"[bold green]🎉 {answer} is correct! You’ve earned a shiny new star. ✨[/bold green]",
        f"[bold green]🎄 Santa approves {answer} as the official answer. Star unlocked! 🎄[/bold green]",
        f"[bold green]✨ {answer} is exactly right. Another square on the calendar is complete. ✨[/bold green]",
        f"[bold green]🎁 {answer} is the correct solution. The puzzle is wrapped up nicely. 🎁[/bold green]",
        f"[bold green]🌟 {answer} is a star answer. Part cleared, on to the next! 🌟[/bold green]",
        f"[bold green]🎅 {answer} is spot on. The sleigh can take off a little earlier now. 🎅[/bold green]",
    ]
    return random.choice(messages)


def get_answer_too_high_message(answer: int | str, *, festive: bool = True) -> str:
    """For numeric guesses that are too high."""
    if not festive:
        return f"{answer} is too high."

    messages: list[str] = [
        f"[bold yellow]🎅 {answer} is too high. Try a smaller number.[/bold yellow]",
        f"[bold yellow]❄️ {answer} overshoots the target. Think lower. ❄️[/bold yellow]",
        f"[bold yellow]🦌 {answer} flies above the right value. Bring it down.[/bold yellow]",
        f"[bold yellow]🎄 {answer} is close but too high. Trim a bit off the top.[/bold yellow]",
        f"[bold yellow]🎈 {answer} is floating too high in the sky. Drop it a little.[/bold yellow]",
        f"[bold yellow]🔥 {answer} is running hot. Cool it off with a lower guess.[/bold yellow]",
    ]
    return random.choice(messages)


def get_answer_too_low_message(answer: int | str, *, festive: bool = True) -> str:
    """For numeric guesses that are too low."""
    if not festive:
        return f"{answer} is too low."

    messages: list[str] = [
        f"[bold yellow]🎅 {answer} is too low. Bump that number up.[/bold yellow]",
        f"[bold yellow]🔥 {answer} is close, but you need to nudge it higher.[/bold yellow]",
        f"[bold yellow]🦌 {answer} is below the mark. Look up a bit.[/bold yellow]",
        f"[bold yellow]🎈 {answer} isn’t quite enough. Increase it.[/bold yellow]",
        f"[bold yellow]🌟 {answer} is low compared to the target. Aim higher. 🌟[/bold yellow]",
        f"[bold yellow]📈 {answer} is beneath the correct value. Slide the dial up.[/bold yellow]",
    ]
    return random.choice(messages)


def get_recent_submission_message(*, festive: bool = True) -> str:
    """When AoC says you’re in the cooldown window."""
    if not festive:
        return "You submitted an answer recently. Please wait before trying again."

    messages: list[str] = [
        "[bold cyan]🕒 You submitted recently. Wait a bit before trying again. ⏳[/bold cyan]",
        "[bold cyan]🎅 Slow and steady—AoC has a cooldown. Try again in a moment.[/bold cyan]",
        "[bold cyan]❄️ The elves are still processing your last answer. Please wait.[/bold cyan]",
        "[bold cyan]🎁 Hold on a bit before your next attempt. The server needs a breather.[/bold cyan]",
        "[bold cyan]⏰ Cooldown in effect. Grab some cocoa and try again soon.[/bold cyan]",
        "[bold cyan]🧝 The workshop needs a second. Wait before resubmitting.[/bold cyan]",
    ]
    return random.choice(messages)


def get_already_completed_message(*, festive: bool = True) -> str:
    """When the user has already completed this part on AoC."""
    if not festive:
        return "You have already completed this part."

    messages: list[str] = [
        "[bold green]🎉 You’ve already completed this part and claimed the star. Nice job! 🎉[/bold green]",
        "[bold green]🌟 This part is already done—your star is safely on the tree. 🌟[/bold green]",
        "[bold green]🎄 This puzzle piece is in place already. Time to tackle another day or part.[/bold green]",
        "[bold green]🎁 You’ve unwrapped this gift already. Choose a different puzzle.[/bold green]",
        "[bold green]☑️ Task complete. You’re ahead of the sleigh on this one. 🛷[/bold green]",
    ]
    return random.choice(messages)


def get_incorrect_answer_message(answer: int | str, *, festive: bool = True) -> str:
    """When AoC says the answer is wrong but doesn’t specify high/low."""
    if not festive:
        return f"{answer} is not correct."

    messages: list[str] = [
        f"[bold red]🎅 {answer} isn’t correct. Keep trying—every run teaches you something.[/bold red]",
        f"[bold red]❄️ {answer} missed the mark. Re-check the puzzle text and examples.[/bold red]",
        f"[bold red]🦌 {answer} is close, but not quite. Review your logic and types.[/bold red]",
        f"[bold red]🎁 {answer} is incorrect, but you’re unwrapping more insight with each attempt.[/bold red]",
        f"[bold red]🎄 {answer} didn’t land. Try a different angle or algorithm.[/bold red]",
        f"[bold red]🌟 {answer} didn’t shine this time. Refine and give it another go.[/bold red]",
    ]
    return random.choice(messages)


def get_unexpected_response_message(*, festive: bool = True) -> str:
    """When the AoC server responds with something the tool didn’t expect."""
    if not festive:
        return "Received an unexpected response from Advent of Code. Check the website for details."

    messages: list[str] = [
        "[bold magenta]🤔 The elves are puzzled by this response from the server.[/bold magenta]",
        "[bold magenta]🎄 Unexpected response. Check the Advent of Code website for details.[/bold magenta]",
        "[bold magenta]🌟 Something odd happened. Open the site to see the full message.[/bold magenta]",
        "[bold magenta]🎁 Curious response from the server. Time for a quick investigation.[/bold magenta]",
        "[bold magenta]🔮 Unexpected result. Verify directly on Advent of Code.[/bold magenta]",
    ]
    return random.choice(messages)


def get_cached_low_message(
    answer: int | str,
    highest_low_guess: Guess,
    *,
    festive: bool = True,
) -> str:
    """User guessed too low and we know their previous highest “too low” guess."""
    time_str = highest_low_guess.timestamp.strftime("%B %d at %I:%M %p")

    if not festive:
        return f"{answer} is still too low. Your highest low was {highest_low_guess.guess} on {time_str}."

    messages: list[str] = [
        (
            f"[bold yellow]🎅 {answer} is still too low. "
            f"Your highest low was [bold]{highest_low_guess.guess}[/bold] on {time_str}. Aim higher.[/bold yellow]"
        ),
        (
            f"[bold yellow]🔥 {answer} is below your previous low of "
            f"[bold]{highest_low_guess.guess}[/bold] ({time_str}). Increase it.[/bold yellow]"
        ),
        (
            f"[bold yellow]🎈 {answer} hasn’t passed your earlier low of "
            f"[bold]{highest_low_guess.guess}[/bold] from {time_str}. Go up.[/bold yellow]"
        ),
        (
            f"[bold yellow]🌤️ {answer} is under your top low "
            f"[bold]{highest_low_guess.guess}[/bold] (from {time_str}). Try higher.[/bold yellow]"
        ),
        (
            f"[bold yellow]🛷 {answer} is still below [bold]{highest_low_guess.guess}[/bold] "
            f"(guessed on {time_str}). Push upward.[/bold yellow]"
        ),
    ]
    return random.choice(messages)


def get_cached_high_message(
    answer: int | str,
    lowest_high_guess: Guess,
    *,
    festive: bool = True,
) -> str:
    """User guessed too high and we know their previous lowest “too high” guess."""
    time_str = lowest_high_guess.timestamp.strftime("%B %d at %I:%M %p")

    if not festive:
        return f"{answer} is too high. Your lowest high was {lowest_high_guess.guess} on {time_str}."

    messages: list[str] = [
        (
            f"[bold yellow]🎅 {answer} is too high. Your lowest high was "
            f"[bold]{lowest_high_guess.guess}[/bold] on {time_str}. Go lower.[/bold yellow]"
        ),
        (
            f"[bold yellow]❄️ {answer} is above your lowest high of "
            f"[bold]{lowest_high_guess.guess}[/bold] ({time_str}). Cool it down.[/bold yellow]"
        ),
        (
            f"[bold yellow]🦌 {answer} beats your previous high of "
            f"[bold]{lowest_high_guess.guess}[/bold] from {time_str}. Drop it.[/bold yellow]"
        ),
        (
            f"[bold yellow]🎄 {answer} is higher than "
            f"[bold]{lowest_high_guess.guess}[/bold] (from {time_str}). Try a smaller value.[/bold yellow]"
        ),
        (
            f"[bold yellow]🔔 {answer} rings above your lowest high "
            f"[bold]{lowest_high_guess.guess}[/bold] ({time_str}). Tone it down.[/bold yellow]"
        ),
    ]
    return random.choice(messages)


def get_cached_duplicate_message(
    answer: int | str,
    previous_guess: Guess,
    *,
    festive: bool = True,
) -> str:
    """User guessed exactly the same thing as a prior attempt."""
    time_str = previous_guess.timestamp.strftime("%B %d at %I:%M %p")

    if not festive:
        return f"You already tried {answer} on {time_str}. Please choose a different guess."

    messages: list[str] = [
        f"[bold yellow]🎅 You already tried {answer} on {time_str}. Pick a new number.[/bold yellow]",
        f"[bold yellow]🔄 {answer} again? You guessed that on {time_str}. Try something else.[/bold yellow]",
        f"[bold yellow]🎄 {answer} was submitted on {time_str}. Choose a different guess.[/bold yellow]",
        f"[bold yellow]🧝 The elves remember {answer} from {time_str}. Think of a new one.[/bold yellow]",
        f"[bold yellow]📜 {answer} is on the scroll from {time_str}. Time for a fresh guess.[/bold yellow]",
    ]
    return random.choice(messages)
