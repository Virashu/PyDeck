import typing as t

ButtonId: t.TypeAlias = tuple[int, int]
ActionCallable: t.TypeAlias = t.Callable[..., t.Any]
