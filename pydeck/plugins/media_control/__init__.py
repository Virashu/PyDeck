import json
import urllib.request
import urllib.error
import typing as t
from pydeck.plugin import DeckPlugin
import logging

logger = logging.getLogger(__name__)


def _check_connection(url: str):
    try:
        with urllib.request.urlopen(url, timeout=0.1):
            pass
    except urllib.error.URLError:
        return False
    return True


def _get_data(url: str):
    try:
        with urllib.request.urlopen(url, timeout=0.1) as response:
            contents = response.read()
    except urllib.error.URLError:
        return None

    try:
        data = json.loads(contents)
    except json.JSONDecodeError:
        return None
    return data


class Main(DeckPlugin):
    name = "Media Control"
    description = "Media control plugin"
    author = "Virashu"

    plugin_id = "media_control"

    @t.final
    def load(self):
        self.variables = {
            "title": "",
            "artist": "",
            "album": "",
        }
        self.config = {
            "url": "http://localhost:8888",
        }
        self.actions: dict[str, t.Any] = {"toggle_pause": self._toggle_pause}

        if not _check_connection(self.config["url"]):
            logger.warning("Media control server not running")

    @t.final
    def update(self) -> None:
        data = _get_data(self.config["url"] + "/data")

        if not data:
            return

        self.variables = {
            "title": data["metadata"]["title"],
            "artist": data["metadata"]["artist"],
            "album": data["metadata"]["album"],
        }

    def _toggle_pause(self):
        _get_data(self.config["url"] + "/control/pause")
