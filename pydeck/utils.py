__all__ = ["empty", "get_path"]

import typing as t


# pylint: disable=unused-argument
def empty(*args: t.Any, **kwargs: t.Any) -> None:
    """Dummy function.

    Can be used to disable some non-configurable annoying functions
    """


def get_path(name: str) -> str:
    """Get pathname for file.

    Args:
        name: file's __name__ attribute
    """
    return name.replace("\\", "/").rsplit("/", 1)[0]
