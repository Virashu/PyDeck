"""Deck button"""

import typing as t


class Button:
    """Deck button data structure"""

    text: str

    text_align: t.Optional[str] = None
    font_family: t.Optional[str] = None
    font_size: t.Optional[str] = None

    icon: t.Optional[str] = None

    action: t.Optional[str] = None

    def __init__(
        self,
        text: str = "",
        text_align: t.Optional[str] = None,
        font_family: t.Optional[str] = None,
        font_size: t.Optional[str] = None,
        action: t.Optional[str] = None,
    ):
        self.text = text

        self.text_align = text_align or "center"
        self.font_family = font_family or "sans-serif"
        self.font_size = font_size or "14"

        self.action = action

    def dict(self) -> dict[str, t.Any]:
        """Returns properties of a button as dictionary"""
        return {
            "text": self.text,
        }

    def __repr__(self):
        return str(self.dict())

    def format(self, **kwargs: t.Any) -> None:
        """Format inner text with variables

        Bruh. Use in copies"""
        self.text = self.text.format(**kwargs)
