import typing as t

ButtonId: t.TypeAlias = tuple[int, int]
ActionCallable: t.TypeAlias = t.Callable[..., t.Any]

_AnyBase: t.TypeAlias = "_AnyDict | _AnyList | str | int | float | None"
_AnyList: t.TypeAlias = list["_AnyBase"]
_AnyDict: t.TypeAlias = dict[str, _AnyBase]
JSONDict: t.TypeAlias = _AnyDict
