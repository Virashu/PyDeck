import typing as t

from pydeck.plugin import DeckPlugin


class Main(DeckPlugin):
    name = "System (win)"
    description = "System plugin"
    author = "Virashu"

    plugin_id = "system"

    @t.final
    def load(self):
        self.actions = {"launch": self._launch_app}

    @t.final
    def update(self) -> None: ...

    def _launch_app(self) -> None: ...
