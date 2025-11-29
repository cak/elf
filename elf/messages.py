from .models import Guess


def get_correct_answer_message(answer: int | str) -> str:
    """When AoC confirms the answer is correct and awards a star."""
    return f"{answer} is correct. Star awarded."


def get_answer_too_high_message(answer: int | str) -> str:
    """For numeric guesses that are too high."""
    return f"{answer} is too high."


def get_answer_too_low_message(answer: int | str) -> str:
    """For numeric guesses that are too low."""
    return f"{answer} is too low."


def get_recent_submission_message() -> str:
    """When AoC says you’re in the cooldown window."""
    return "You submitted an answer recently. Please wait before trying again."


def get_already_completed_message() -> str:
    """When the user has already completed this part on AoC."""
    return "You have already completed this part."


def get_incorrect_answer_message(answer: int | str) -> str:
    """When AoC says the answer is wrong but doesn’t specify high/low."""
    return f"{answer} is not correct."


def get_wrong_level_message() -> str:
    """When AoC says the submission is for the wrong puzzle level."""
    return "You don't seem to be solving the right level. Double-check the part number."


def get_unexpected_response_message() -> str:
    """When the AoC server responds with something the tool didn’t expect."""
    return "Received an unexpected response from Advent of Code. Check the website for details."


def get_cached_low_message(
    answer: int | str,
    highest_low_guess: Guess,
) -> str:
    """User guessed too low and we know their previous highest “too low” guess."""
    time_str = highest_low_guess.timestamp.strftime("%B %d at %I:%M %p")
    return f"{answer} is still too low. Your highest low was {highest_low_guess.guess} on {time_str}."


def get_cached_high_message(
    answer: int | str,
    lowest_high_guess: Guess,
) -> str:
    """User guessed too high and we know their previous lowest “too high” guess."""
    time_str = lowest_high_guess.timestamp.strftime("%B %d at %I:%M %p")
    return f"{answer} is too high. Your lowest high was {lowest_high_guess.guess} on {time_str}."


def get_cached_duplicate_message(
    answer: int | str,
    previous_guess: Guess,
) -> str:
    """User guessed exactly the same thing as a prior attempt."""
    time_str = previous_guess.timestamp.strftime("%B %d at %I:%M %p")
    return f"You already tried {answer} on {time_str}. Please choose a different guess."
