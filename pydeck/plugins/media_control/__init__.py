from __future__ import annotations

import json
import logging
import time
import typing as t
from urllib.error import URLError
from urllib.request import Request, urlopen

from pydeck_shared.plugin import DeckPlugin

logger = logging.getLogger(__name__)


def _check_connection(url: str) -> bool:
    try:
        with urlopen(url, timeout=0.1):  # noqa: S310
            pass
    except URLError:
        return False
    return True


def _get_data(url: str) -> dict[str, t.Any] | None:
    try:
        with urlopen(url, timeout=0.1) as response:  # noqa: S310
            contents = response.read()
        data = json.loads(contents)
    except (URLError, json.JSONDecodeError):
        return None
    return data


def _post(url: str) -> None:
    req = Request(  # noqa: S310
        url,
        method="GET",
        headers={"Allow-Origin": "*", "Cross-Origin-Resource-Policy": "cross-origin"},
    )
    with urlopen(req, timeout=1) as response:  # noqa: S310
        response.read()


class Main(DeckPlugin):
    name = "Media Control"
    description = "Media control plugin"
    author = "Virashu"

    plugin_id = "media_control"

    @t.final
    def load(self) -> None:
        self.variables = {
            "title": "",
            "artist": "",
            "album_title": "",
            "album_artist": "",
            "state": "",
        }
        self.config = {
            "url": "http://localhost:8888",
        }
        self.actions: dict[str, t.Any] = {
            "toggle_pause": self._toggle_pause,
            "next": self._next,
            "prev": self._prev,
        }

        if not _check_connection(self.config["url"]):
            logger.warning("Media control server not running")

        self._last = time.time()
        self._min_delta = 0.5

    @t.final
    def update(self) -> None:
        if time.time() - self._last < self._min_delta:
            return

        self._last = time.time()

        data = _get_data(self.config["url"] + "/data")

        if not data:
            return

        self.variables = {
            "title": data["title"],
            "artist": data["artist"],
            "album_title": data["album_title"],
            "album_artist": data["album_artist"],
            "staete": data["state"],
        }

    def _control(self, action: str) -> None:
        _post(self.config["url"] + "/control/" + action)

    def _toggle_pause(self) -> None:
        self._control("pause")

    def _next(self) -> None:
        self._control("next")

    def _prev(self) -> None:
        self._control("prev")
