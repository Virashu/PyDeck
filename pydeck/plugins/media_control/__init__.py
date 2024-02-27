import json
import urllib.request
import typing as t
from pydeck.plugin import DeckPlugin


def _get_data(url: str):
    with urllib.request.urlopen(url, timeout=0.1) as response:
        contents = response.read()

    try:
        data = json.loads(contents)
    except json.JSONDecodeError:
        return None
    return data


class Main(DeckPlugin):
    name = "Media Control"
    description = "Media control plugin"
    author = "Virashu"

    plugin_prefix = "media_control"

    variables: dict[str, t.Any] = {
        "title": "",
        "artist": "",
        "album": "",
    }

    config: dict[str, t.Any] = {
        "url": "http://localhost:8888",
    }

    @t.final
    def load(self):
        self.actions: dict[str, t.Any] = {"toggle_pause": self._toggle_pause}

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
