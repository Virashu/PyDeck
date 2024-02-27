from pydeck.plugin import DeckPlugin
import typing as t
import datetime


class Main(DeckPlugin):
    name = "Builtin"
    description = "Builtin plugin"
    author = "Virashu"

    plugin_prefix = "builtin"

    @t.final
    def load(self):
        self.variables = {"time": self._get_time()}

    @t.final
    def update(self) -> None:
        self.variables = {"time": self._get_time()}

    def _get_time(self) -> str:
        return datetime.datetime.now().strftime("%H:%M:%S")
