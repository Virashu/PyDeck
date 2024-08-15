"""Main module."""

from __future__ import annotations

__all__ = ["Deck"]

import copy
import logging
import re
import threading
import time
import typing as t
from itertools import product

import flask

from pydeck.button import Button as DeckButton
from pydeck.config import config
from pydeck.pluginmanager import PLUGIN_SEP, PluginManager
from pydeck.typing import ActionCallable, ButtonId
from pydeck.utils import empty

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Disable banner (cannot be done other way :( )
flask.cli.show_server_banner = empty

PATH: str = __file__.replace("\\", "/").rsplit("/", 1)[0]
ROOT: str = PATH.rsplit("/", 1)[0]

ButtonMatrix: t.TypeAlias = dict[ButtonId, DeckButton]


def buttons_as_list(obj: ButtonMatrix) -> list[dict[str, t.Any]]:
    """Return buttons as list.

    Adds `id` property
    """
    return [{"id": k} | v.as_dict() for k, v in obj.items()]


class Deck:
    """Deck, the main point of the app."""

    config: dict[str, t.Any]
    plugins_config: dict[str, t.Any]
    _actions: dict[str, ActionCallable]
    _variables: dict[str, t.Any]

    buttons: ButtonMatrix
    _buttons_base: ButtonMatrix
    _buttons_rendered: ButtonMatrix

    _click_events: list[dict[str, t.Any]]
    _running: bool
    _plugin_manager: PluginManager

    def __init__(self) -> None:
        self._plugin_manager = PluginManager(plugin_dir=f"{PATH}/plugins")
        self._variables = {}
        self._click_events = []
        self._running = True

        # User configurable
        self.buttons = {
            (0, 2): DeckButton("{media_control__title}\n{media_control__artist}"),
            (1, 1): DeckButton("Previous", action="media_control__prev"),
            (1, 2): DeckButton("Play/Pause", action="media_control__toggle_pause"),
            (1, 3): DeckButton("Next", action="media_control__next"),
            (2, 2): DeckButton("time: {builtin__time}"),
        }
        self.config = config

        fill = True

        # Blank dummy buttons
        self._buttons_base = {
            (x, y): DeckButton("&nbsp;" if fill else "")
            for x, y in product(
                range(self.config["deck"]["rows"]),
                range(self.config["deck"]["cols"]),
            )
        }
        # Rendered initialized buttons
        self._buttons_rendered = {}

        for _id in self.buttons:
            if (
                _id[0] >= self.config["deck"]["rows"]
                or _id[1] >= self.config["deck"]["cols"]
            ):
                logger.warning("Button id is out of bounds: %s", _id)

    def run(self) -> None:
        """Start deck server."""
        self._plugin_manager.load()

        self._plugin_manager.set_config(self.config["plugins"])

        self._actions = self._plugin_manager.actions

        deck_update_loop = threading.Thread(target=self._run_update_loop, daemon=True)
        web_interface = threading.Thread(target=self._run_web_interface, daemon=True)

        deck_update_loop.start()
        web_interface.start()

        while self._running:
            time.sleep(1e6)

    def stop(self) -> None:
        """Stop deck server"""
        self._running = False

    def update(self) -> None:
        """Update deck"""
        self._plugin_manager.update()

        while self._click_events:
            self._handle_click(self._click_events.pop(0))

        self._variables.update(self._plugin_manager.variables)

        temp_render = copy.deepcopy(self.buttons)

        for button in temp_render.values():
            button.format(**self._variables)

        self._buttons_rendered = temp_render

    def _handle_click(self, json: dict[str, t.Any]) -> None:
        str_id = json.get("button_id")

        if not isinstance(str_id, str) or not re.search(r"^\d+:\d+$", str_id):
            logger.warning("Invalid button_id: %s", str_id)
            return

        tuple_id: ButtonId = tuple(map(int, str_id.split(":")[:2]))  # type: ignore[reportAssignmentType]
        button: DeckButton | None = self.buttons.get(tuple_id)

        if not button:
            logger.warning("Invalid button_id: %s", str_id)
            return

        logger.info("Button clicked: %s", str_id)

        if not button.action:
            return

        logger.info("Action: %s", button.action)
        action_callable = self._actions.get(button.action)

        if not action_callable:
            logger.warning("Invalid action: %s", button.action)
            return

        try:
            action_callable(**button.action_args)
        except Exception:  # pylint: disable=broad-exception-caught
            # We need to catch plugin-generated exceptions and
            # log them to the user
            plugin_name: str = button.action.split(PLUGIN_SEP)[0]
            logger.exception("Plugin '%s' action error", plugin_name)

    def _run_update_loop(self) -> None:
        while self._running:
            self.update()

    def _run_web_interface(self) -> None:  # noqa: C901
        app = flask.Flask(__name__)

        # Test GUI

        @app.get("/", defaults={"path": "index.html"})
        @app.get("/<path:path>")
        def index(path: str) -> flask.Response:  # type: ignore[reportUnusedFunction]
            return flask.send_from_directory(f"{ROOT}/public", path)

        # API (Client)

        @app.get("/api/<path:path>")
        def api_any(path: str) -> flask.Response:  # type: ignore[reportUnusedFunction]
            if path == "config":
                logger.info("New connection: %s", flask.request.remote_addr)
                response = flask.jsonify(self.config)
            elif path == "buttons":
                buttons = buttons_as_list(self._buttons_base | self._buttons_rendered)

                response = flask.jsonify(buttons)
            elif path == "buttons_nonblank":
                buttons = buttons_as_list(self._buttons_rendered)
                response = flask.jsonify(buttons)
            else:
                response = flask.Response()
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response

        @app.post("/api/event")
        def api_event() -> flask.Response:  # type: ignore[reportUnusedFunction]
            json = flask.request.get_json()
            if json.get("type") == "click":
                self._click_events.append(json.get("data"))
            response = flask.Response("bruh")
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Methods", "GET, POST")
            response.headers.add("Access-Control-Allow-Headers", "*")
            return response

        # API (Server config)
        @app.get("/api/actions_list")
        def api_action_list() -> flask.Response:  # type: ignore[reportUnusedFunction]
            return flask.jsonify(list(self._actions.keys()))

        @app.get("/api/action_details/<path:path>")
        def api_action(path: str) -> flask.Response:  # type: ignore[reportUnusedFunction]
            if path in self._actions:
                return flask.jsonify(self._actions[path])

            return flask.Response()

        host = self.config["server"]["host"]
        port = self.config["server"]["port"]

        logger.info("Running on http://%s:%s", host, port)
        app.run(host, port)
