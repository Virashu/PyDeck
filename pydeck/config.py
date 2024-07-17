"""Loads configuration

CONFIG
    Dictionary of loaded configuration (merged with default configuration)

DEFAULTS
    Default values for some objects. Not to be confused with default config
"""

__all__ = ["config", "defaults"]


import json
import pathlib
import shutil
from typing import Any

default_config: dict[str, Any]
config: dict[str, Any]
defaults: dict[str, Any]

PATH = __file__.replace("\\", "/").rsplit("/", 1)[0]

_DEFAULT_CONFIG_FILE = f"{PATH}/config.default.json"
_CONFIG_FILE = f"{PATH}/config.json"
_DEFAULTS_FILE = f"{PATH}/defaults.json"

with open(_DEFAULT_CONFIG_FILE, encoding="utf-8") as f:
    default_config = json.load(f)

if not pathlib.Path(_CONFIG_FILE).exists():
    shutil.copy(_DEFAULT_CONFIG_FILE, _CONFIG_FILE)
    config = default_config
else:
    with open(_CONFIG_FILE, encoding="utf-8") as f:
        config = json.load(f)

config = default_config | config

with open(_DEFAULTS_FILE, encoding="utf-8") as f:
    defaults = json.load(f)
