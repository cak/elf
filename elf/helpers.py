import time
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def parse_input(input_str: str) -> list[str]:
    """Split the raw input into lines without trimming whitespace or blank rows."""
    return input_str.splitlines()


def timer(
    enabled: bool = True, logger: Callable[[str], None] | None = None
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to measure the execution time of functions.

    Args:
        enabled (bool): Whether to enable timing.
        logger (Optional[Callable[[str], None]]): A logging function to output the timing message.
            If `None`, the message will be printed to the console.

    Returns:
        Callable[[Callable[..., Any]], Callable[..., Any]]: The decorator that wraps the function.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start_time: float | None = None
            if enabled:
                start_time = time.perf_counter()

            result = func(*args, **kwargs)
            if enabled:
                end_time = time.perf_counter()
                duration = end_time - start_time if start_time is not None else 0.0
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


def read_input(path: Path) -> str:
    """Read input from a file and return its contents."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Input file not found: {path}. Please add the missing file."
        )

    return path.read_text(encoding="utf-8").strip()
