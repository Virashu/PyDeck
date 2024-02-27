import logging
from .pydeck import Deck


logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("{levelname:<10} {name:<32} {message}", style="{")
handler.setFormatter(formatter)
logger.addHandler(handler)


if __name__ == "__main__":
    deck = Deck()

    try:
        deck.run()
    except KeyboardInterrupt:
        deck.stop()
