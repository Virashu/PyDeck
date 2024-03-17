"""System plugin

Execute keystrokes
Run applications
Control volume
"""

import typing as t
import subprocess
import warnings

from pydeck.plugin import DeckPlugin


class Main(DeckPlugin):
    name = "System (win)"
    description = "System plugin"
    author = "Virashu"

    plugin_id = "system"

    @t.final
    def load(self) -> None:
        self.actions = {
            "launch": self._launch_app,
        }

    @t.final
    def update(self) -> None: ...

    def _launch_app(self, path: str, capture: bool = False, var_name: str = "") -> None:
        """
        path: path to executable
        can be launched as sub or distinct process
        """
        if capture:
            if not var_name:
                warnings.warn("You should specify a variable name to use capture")
            res = subprocess.check_output(path.split()).decode("utf-8")
            self.variables[var_name] = res

        subprocess.Popen(path.split())
