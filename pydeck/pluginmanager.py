"""Plugin manager"""

import importlib.util
import logging
import os
import pathlib
import sys
import typing as t

from pydeck_shared import DeckPlugin

from .utils import get_path

libs_path = get_path(__file__) + "/plugin_libs"
sys.path.append(libs_path)


logger = logging.getLogger(__name__)

PLUGIN_SEP = "__"  # Separator for plugin's variables and methods


def _load_module(plugin_name: str, plugins_path: str) -> type[DeckPlugin] | None:
    if pathlib.Path(f"{plugins_path}/{plugin_name}").is_dir():
        module_path = f"{plugins_path}/{plugin_name}/__init__.py"
        module_name = plugin_name

    elif pathlib.Path(f"{plugins_path}/{plugin_name}").is_file():
        module_path = f"{plugins_path}/{plugin_name}"
        module_name, ext = plugin_name.rsplit(".", 1)

        if ext in ("zip", "pyz"):
            sys.path.append(module_path)

            _module = __import__(f"{module_name}")
            print(_module)

            return _module.Main

    else:
        logger.warning("File '%s' is not a plugin", plugin_name)
        return None

    _spec = importlib.util.spec_from_file_location(plugin_name, module_path)
    if not _spec:
        logger.warning("Failed to load plugin '%s'", plugin_name)
        return None
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[module_name] = _module
    if not _spec.loader:
        logger.warning("Failed to load plugin '%s'", plugin_name)
        return None
    _spec.loader.exec_module(_module)

    if not hasattr(_module, "Main"):
        logger.warning("Plugin '%s' has wrong structure", plugin_name)
        return None

    return _module.Main


class PluginManager:
    """Plugin manager

    Loads plugins
    """

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

            logger.debug("Loading plugin: %s", plugin)
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

            logger.debug("Loaded plugin: %s", plugin)

        logger.debug("Loaded plugins: %s", list(self.plugins.keys()))

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
            except Exception:
                logger.exception("Plugin '%s' error", plugin.name)

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
