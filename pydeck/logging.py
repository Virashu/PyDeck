import logging

red = "\x1b[31m"
green = "\x1b[32m"
yellow = "\x1b[33m"
blue = "\x1b[34m"
grey = "\x1b[38m"
bold_red = "\x1b[31;1m"
reset = "\x1b[0m"

FORMATS = {
    logging.DEBUG: green,
    logging.INFO: blue,
    logging.WARNING: yellow,
    logging.ERROR: red,
    logging.CRITICAL: bold_red,
}


class ColoredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        _fmt_p = self._fmt
        color = FORMATS.get(record.levelno)

        if color is None or _fmt_p is None:
            return "Bruh"

        return color + super().format(record) + reset
