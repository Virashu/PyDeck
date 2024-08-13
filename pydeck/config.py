"""Loads configuration.

CONFIG
    Dictionary of loaded configuration (merged with default configuration)

DEFAULTS
    Default values for some objects. Not to be confused with default config
"""

__all__ = ["config", "defaults"]


import json
import shutil
from pathlib import Path
from typing import Any

default_config: dict[str, Any]
config: dict[str, Any]
defaults: dict[str, Any]

PATH = __file__.replace("\\", "/").rsplit("/", 1)[0]

_DEFAULT_CONFIG_FILE = f"{PATH}/config.default.json"
_CONFIG_FILE = f"{PATH}/config.json"
_DEFAULTS_FILE = f"{PATH}/defaults.json"

with Path(_DEFAULT_CONFIG_FILE).open() as f:
    default_config = json.load(f)

if (config_path := Path(_CONFIG_FILE)).exists():
    with config_path.open() as f:
        config = json.load(f)
else:
    shutil.copy(_DEFAULT_CONFIG_FILE, _CONFIG_FILE)
    config = default_config

config = default_config | config

with Path(_DEFAULTS_FILE).open() as f:
    defaults = json.load(f)
