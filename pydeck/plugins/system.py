"""System plugin.

Execute keystrokes
Run applications
Control volume
"""

import logging
import subprocess
import typing as t

from pydeck_shared.plugin import DeckPlugin

logger = logging.getLogger(__name__)


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

    def _launch_app(
        self, path: str, *, capture: bool = False, var_name: str = ""
    ) -> None:
        """Launch executable.

        Args:
            path: path of executable
            capture: whether to capture output
            var_name: name of variable to save output
        """
        if capture:
            if not var_name:
                logger.warning("You should specify a variable name to use capture")
                return
            res = subprocess.check_output(path.split()).decode("utf-8")  # noqa: S603
            self.variables[var_name] = res

        else:
            p = subprocess.Popen(path.split())  # noqa: S603
            del p
