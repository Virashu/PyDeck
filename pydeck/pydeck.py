"""Main module"""

__all__ = ["Deck"]

from itertools import product
import typing as t
import threading
import time
import copy
import logging

import flask

from pydeck.pluginmanager import PluginManager
from pydeck.button import Button as DeckButton
from pydeck.utils import empty


logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.getLogger("flask").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

flask.cli.show_server_banner = empty

PATH = __file__.replace("\\", "/").rsplit("/", 1)[0]


ButtonId: t.TypeAlias = tuple[int, int]


def prep_buttons(obj: dict[ButtonId, DeckButton]) -> dict[str, list[dict[str, t.Any]]]:
    buttons: list[dict[str, t.Any]] = []
    for k, v in obj.items():
        buttons.append({"id": k} | v.dict())

    return {"buttons": buttons}


class Deck:
    """Deck, the main point of the app"""

    config: dict[str, t.Any]
    plugins_config: dict[str, t.Any]
    variables: dict[str, t.Any]
    actions: dict[str, t.Any]

    buttons: dict[ButtonId, DeckButton]
    buttons_rendered: dict[ButtonId, DeckButton]
    buttons_base: dict[ButtonId, DeckButton]

    def __init__(self) -> None:
        self.buttons = {
            (0, 0): DeckButton("Button 1\n{media_control_title}"),
            (1, 1): DeckButton("Button 2\n{media_control_artist}"),
            (2, 4): DeckButton("Button 3\n{media_control_artist}"),
            (2, 2): DeckButton("time: {builtin_time}",),
            (2, 3): DeckButton("pause", action="media_control_toggle_pause"),
        }
        self.config = {"dimensions": {"rows": 3, "cols": 5}}
        self.buttons_rendered = {}

        self.buttons_base = {
            (x, y): DeckButton(f"{x}:{y}")
            for x, y in product(
                range(self.config["dimensions"]["rows"]),
                range(self.config["dimensions"]["cols"]),
            )
        }

        self.plugins_config = {"media_control": {"url": "http://localhost:8888/data"}}

        self.variables = {}

        self.plugin_manager = PluginManager(plugin_dir=f"{PATH}/plugins")

        self._running = True

    def run(self) -> None:
        """Start deck server"""
        self.plugin_manager.load()

        self.actions = self.plugin_manager.actions

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

        self.plugin_manager.update()

        self.variables.update(self.plugin_manager.variables)

        self.buttons_rendered = copy.deepcopy(self.buttons)

        for button in self.buttons_rendered.values():
            button.format(**self.variables)

    def _handle_click(self, json: dict[str, t.Any]) -> None:
        str_id = json.get("button_id")

        logger.info("Button clicked: %s", str_id)

        tuple_id = tuple(map(int, str_id.split(":")))  # type: ignore
        button = self.buttons.get(tuple_id)  # type: ignore

        if button:
            if button.action:
                self.actions[button.action]()

    def _run_update_loop(self) -> None:
        while self._running:
            self.update()

    def _run_web_interface(self) -> None:
        app = flask.Flask(__name__)

        @app.get("/")
        def _a1() -> flask.Response:
            return flask.send_from_directory(f"{PATH}/public", "index.html")

        @app.get("/<path:path>")
        def _a(path: str) -> flask.Response:
            return flask.send_from_directory(f"{PATH}/public", path)

        @app.get("/api/<path:path>")
        def _b(path: str) -> flask.Response:
            if path == "config":
                logger.info("New connection: %s", flask.request.remote_addr)
                response = flask.jsonify(self.config)
            elif path == "buttons":
                buttons = prep_buttons(self.buttons_base | self.buttons_rendered)
                response = flask.jsonify(buttons)
            else:
                response = flask.Response()
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response

        @app.post("/api/event")
        def _c() -> flask.Response:
            json = flask.request.get_json()
            if json.get("type") == "click":
                self._handle_click(json.get("data"))
            response = flask.Response("bruh")
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Methods", "GET, POST")
            response.headers.add("Access-Control-Allow-Headers", "*")
            return response

        app.run("0.0.0.0", 8192)
