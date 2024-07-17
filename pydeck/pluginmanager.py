"""Plugin manager"""

import importlib.util
import logging
import os
import pathlib
import sys
import typing as t
import zipimport

from pydeck.plugin import DeckPlugin

logger = logging.getLogger(__name__)

PLUGIN_SEP = "__"  # Separator for plugin's variables and methods


def _load_module(module_name: str, plugins_path: str) -> type | None:
    if pathlib.Path(f"{plugins_path}/{module_name}").is_dir():
        module_path = f"{plugins_path}/{module_name}/__init__.py"

    elif (
        pathlib.Path(f"{plugins_path}/{module_name}").is_file()
        and module_name.endswith(".py")
        or module_name.endswith(".zip")
    ):
        module_path = f"{plugins_path}/{module_name}"

    else:
        logger.warning("File '%s' is not a plugin", module_name)
        return None

    # if module_path.endswith(".zip"):
    #     _zip = zipimport.zipimporter(module_path)
    #     _module = _zip.load_module(module_name)
    #     zipimport.zipimporter.find_spec()
    #     return _module

    _spec = importlib.util.spec_from_file_location(module_name, module_path)
    if not _spec:
        logger.warning("Failed to load plugin '%s'", module_name)
        return None
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[module_name] = _module
    if not _spec.loader:
        logger.warning("Failed to load plugin '%s'", module_name)
        return None
    _spec.loader.exec_module(_module)

    if not hasattr(_module, "Main"):
        logger.warning("Plugin '%s' has wrong structure", module_name)
        return None

    return _module.Main


class PluginManager:
    """Plugin manager

    Loads plugins"""

    plugins: dict[str, DeckPlugin]
    plugin_dir: str

    def __init__(self, plugin_dir: str) -> None:
        self.plugin_dir = plugin_dir
        self.plugins = {}

    def load(self) -> None:
        """Load plugins & execute them"""

        packages = os.listdir(self.plugin_dir)

        for plugin in packages:
            if plugin.startswith("_"):
                continue

            # plugin_module = __import__(f"pydeck.plugins.{plugin}")
            plugin_main: type[DeckPlugin] | None = _load_module(plugin, self.plugin_dir)

            if plugin_main is None:
                continue

            obj: DeckPlugin = plugin_main()
            obj.load()

            if hasattr(obj, "plugin_id"):
                self.plugins[obj.plugin_id] = obj
            else:
                self.plugins[plugin.replace(".py", "")] = obj

    def set_config(self, config: dict[str, dict[str, t.Any]]) -> None:
        """Set plugins' config

        config: dict { plugin_name: { setting: value } }
        """

        for plugin_name, settings in config.items():
            plugin = self.plugins.get(plugin_name)

            if plugin:
                plugin.config.update(settings)

    def update(self) -> None:
        """Update plugins"""

        for plugin in self.plugins.values():
            try:
                plugin.update()
            except Exception as e:
                logger.error("Plugin '%s' error: %s", plugin.name, e)

    @property
    def variables(self) -> dict[str, t.Any]:
        """Get variables from plugins"""

        variables: dict[str, t.Any] = {}

        for plugin_id, plugin in self.plugins.items():
            variables.update(
                {f"{plugin_id}{PLUGIN_SEP}{k}": v for k, v in plugin.variables.items()}
            )

        return variables

    @property
    def actions(self) -> dict[str, t.Any]:
        """Get actions from plugins"""

        actions: dict[str, t.Any] = {}

        for plugin_id, plugin in self.plugins.items():
            actions.update(
                {f"{plugin_id}{PLUGIN_SEP}{k}": v for k, v in plugin.actions.items()}
            )

        return actions
