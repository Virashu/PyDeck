"""Loads configuration

CONFIG
    Dictionary of loaded configuration (merged with default configuration)

DEFAULTS
    Default values for some objects. Not to be confused with default config
"""

__all__ = ["CONFIG", "DEFAULTS"]


import json
import pathlib
import shutil
from typing import Any

DEFAULT_CONFIG: dict[str, Any]
CONFIG: dict[str, Any]
DEFAULTS: dict[str, Any]

PATH = __file__.replace("\\", "/").rsplit("/", 1)[0]

_DEFAULT_CONFIG_FILE = f"{PATH}/config.default.json"
_CONFIG_FILE = f"{PATH}/config.json"
_DEFAULTS_FILE = f"{PATH}/defaults.json"

with open(_DEFAULT_CONFIG_FILE, encoding="utf-8") as f:
    DEFAULT_CONFIG = json.load(f)

if not pathlib.Path(_CONFIG_FILE).exists():
    shutil.copy(_DEFAULT_CONFIG_FILE, _CONFIG_FILE)
    CONFIG = DEFAULT_CONFIG
else:
    with open(_CONFIG_FILE, encoding="utf-8") as f:
        CONFIG = json.load(f)

CONFIG = DEFAULT_CONFIG | CONFIG

with open(_DEFAULTS_FILE, encoding="utf-8") as f:
    DEFAULTS = json.load(f)
