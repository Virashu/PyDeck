"""CLI."""

import logging

from .logging import ColoredFormatter
from .pydeck import Deck

logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.getLogger("flask").setLevel(logging.ERROR)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = ColoredFormatter("{levelname:<10} {name:<32} {message}", style="{")
handler.setFormatter(formatter)
logger.addHandler(handler)


def main() -> None:
    deck = Deck()

    try:
        deck.run()
    except KeyboardInterrupt:
        deck.stop()


if __name__ == "__main__":
    main()
