import time
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any


def parse_input(input_str: str) -> list[str]:
    """Parses the input string into a list of lines.

    🎄 Splitting the input into delightful pieces! 🎁

    Args:
        input_str (str): The raw input string.

    Returns:
        list[str]: A list of input lines.
    """
    return input_str.strip().splitlines()


def timer(enabled: bool = True, logger: Callable[[str], None] | None = None):
    """Decorator to measure the execution time of functions.

    Args:
        enabled (bool): Whether to enable timing.
        logger (Optional[Callable[[str], None]]): A logging function to output the timing message.
            If `None`, the message will be printed to the console.

    Returns:
        Callable[[Callable[..., Any]], Callable[..., Any]]: The decorator that wraps the function.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if enabled:
                start_time = time.perf_counter()
            else:
                start_time = None  # Ensure start_time is always defined
            result = func(*args, **kwargs)
            if enabled:
                end_time = time.perf_counter()
                duration = end_time - start_time if start_time is not None else 0
                message = (
                    f"⏱️ Function '{func.__name__}' took {duration:.6f}s to complete 🎅."
                )
                if logger:
                    logger(message)
                else:
                    print(message)
            return result

        return wrapper

    return decorator


def read_test_input(base_dir: Path) -> str:
    """Read test input from test_input.txt file."""
    test_input_file = base_dir / "test_input.txt"
    if test_input_file.exists():
        return test_input_file.read_text().strip()
    else:
        raise FileNotFoundError(
            "🛑 No test_input.txt found. Please add test input data."
        )
