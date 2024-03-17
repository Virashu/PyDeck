"""Main module"""

__all__ = ["Deck"]

import copy
import logging
import threading
import time
import typing as t
import re
from itertools import product

import flask

from pydeck.button import Button as DeckButton
from pydeck.pluginmanager import PluginManager
from pydeck.utils import empty

logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.getLogger("flask").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Disable banner (cannot be done other way :( )
flask.cli.show_server_banner = empty

PATH = __file__.replace("\\", "/").rsplit("/", 1)[0]


ButtonId: t.TypeAlias = tuple[int, int]


def prep_buttons(obj: dict[ButtonId, DeckButton]) -> dict[str, list[dict[str, t.Any]]]:
    """Prepare buttons for API response

    (Adds id as value in dictionary)"""
    buttons: list[dict[str, t.Any]] = []
    for k, v in obj.items():
        buttons.append({"id": k} | v.dict())

    return {"buttons": buttons}


class Deck:
    """Deck, the main point of the app"""

    config: dict[str, t.Any]
    plugins_config: dict[str, t.Any]
    _actions: dict[str, t.Any]
    _variables: dict[str, t.Any]

    buttons: dict[ButtonId, DeckButton]
    _buttons_base: dict[ButtonId, DeckButton]
    _buttons_rendered: dict[ButtonId, DeckButton]

    def __init__(self) -> None:

        self._plugin_manager = PluginManager(plugin_dir=f"{PATH}/plugins")
        self._variables = {}
        self._running = True

        # Blank dummy buttons
        self._buttons_base = {
            (x, y): DeckButton(f"{x}:{y}")
            for x, y in product(
                range(self.config["dimensions"]["rows"]),
                range(self.config["dimensions"]["cols"]),
            )
        }
        # Rendered initialized buttons
        self._buttons_rendered = {}

        # User configurable
        self.buttons = {
            (0, 0): DeckButton("Button 1\n{media_control__title}"),
            (1, 1): DeckButton("Button 2\n{media_control__artist}"),
            (2, 4): DeckButton("Button 3\n{media_control__artist}"),
            (2, 2): DeckButton("time: {builtin__time}"),
            (2, 3): DeckButton("pause", action="media_control__toggle_pause"),
            (1, 3): DeckButton(
                "Start browser",
                action="system__launch",
                action_args={"path": "firefox"},
            ),
        }
        self.config = {
            "connection": {"host": "127.0.0.1", "port": 8192},
            "dimensions": {"rows": 3, "cols": 5},
        }
        self.plugins_config = {
            "media_control": {"url": "http://localhost:8888/data"},
        }

    def run(self) -> None:
        """Start deck server"""

        self._plugin_manager.load()

        self._plugin_manager.set_config(self.plugins_config)

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

        self._variables.update(self._plugin_manager.variables)

        self._buttons_rendered = copy.deepcopy(self.buttons)

        for button in self._buttons_rendered.values():
            button.format(**self._variables)

    def _handle_click(self, json: dict[str, t.Any]) -> None:
        str_id = json.get("button_id")

        if not isinstance(str_id, str) or not re.search(r"^\d+:\d+$", str_id):
            logger.warning("Invalid button_id: %s", str_id)
            return

        logger.info("Button clicked: %s", str_id)

        tuple_id: ButtonId = tuple(map(int, str_id.split(":")[:2]))  # type: ignore
        button = self.buttons.get(tuple_id)  # type: ignore

        if button:
            if button.action:
                logger.info("Action: %s", button.action)
                self._actions[button.action](**button.action_args)

    def _run_update_loop(self) -> None:
        while self._running:
            self.update()

    def _run_web_interface(self) -> None:
        app = flask.Flask(__name__)

        # Test GUI

        @app.get("/")
        def _a1() -> flask.Response:  # type: ignore
            return flask.send_from_directory(f"{PATH}/public", "index.html")

        @app.get("/<path:path>")
        def _a(path: str) -> flask.Response:  # type: ignore
            return flask.send_from_directory(f"{PATH}/public", path)

        # API

        @app.get("/api/<path:path>")
        def _b(path: str) -> flask.Response:  # type: ignore
            if path == "config":
                logger.info("New connection: %s", flask.request.remote_addr)
                response = flask.jsonify(self.config)
            elif path == "buttons":
                buttons = prep_buttons(self._buttons_base | self._buttons_rendered)
                response = flask.jsonify(buttons)
            else:
                response = flask.Response()
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response

        @app.post("/api/event")
        def _c() -> flask.Response:  # type: ignore
            json = flask.request.get_json()
            if json.get("type") == "click":
                self._handle_click(json.get("data"))
            response = flask.Response("bruh")
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Methods", "GET, POST")
            response.headers.add("Access-Control-Allow-Headers", "*")
            return response

        host = self.config["connection"]["host"]
        port = self.config["connection"]["port"]

        logger.info("Running on %s:%s", host, port)
        app.run(host, port)
