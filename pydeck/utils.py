__all__ = ["empty", "get_path"]

from typing import Any


def empty(*args: Any, **kwargs: Any) -> None:  # noqa: ANN401,ARG001
    """Dummy function.

    Can be used to disable some non-configurable annoying functions
    """


def get_path(name: str) -> str:
    """Get pathname for file.

    Args:
        name: file's __name__ attribute
    """
    return name.replace("\\", "/").rsplit("/", 1)[0]
