"""Deck button"""

import typing as t


class Button:
    """Deck button data structure"""

    text: str

    text_align: str
    font_family: str
    font_size: str

    icon: t.Optional[str]

    action: t.Optional[str]
    action_args: dict[str, t.Any]

    def __init__(
        self,
        text: str = "",
        text_align: t.Optional[str] = None,
        font_family: t.Optional[str] = None,
        font_size: t.Optional[str] = None,
        action: t.Optional[str] = None,
        action_args: t.Optional[dict[str, t.Any]] = None,
    ):
        self.text = text

        self.text_align = text_align or "center"
        self.font_family = font_family or "sans-serif"
        self.font_size = font_size or "14"

        self.action = action
        self.action_args = action_args or {}

    def as_dict(self) -> dict[str, t.Any]:
        """Returns properties of a button as dictionary"""

        return {
            "text": self.text,
        }

    def __repr__(self):
        return str(self.as_dict())

    def format(self, **kwargs: t.Any) -> None:
        """Format inner text with variables

        Bruh. Use in copies"""
        self.text = self.text.format(**kwargs)

    def formatted(self, **kwargs: t.Any) -> str:
        """Format inner text with variables

        Returns formatted text"""
        return self.text.format(**kwargs)
