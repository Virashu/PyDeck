"""Abstract base plugin"""


import typing as t
import abc


class DeckPlugin:
    """Abstract base PyDeck plugin class

    All PyDeck plugins should inherit from this class

    Attributes:
        name: Name of the plugin
        description: Description of the plugin
        author: Author of the plugin

        plugin_prefix: String plugin prefix used for variables and actions

        actions: Dictionary of actions (Callables)
        variables: Dictionary of variables

        config: Custom settings editable by user and used by plugin
    """

    name: str
    description: str
    author: str

    plugin_prefix: str

    actions: dict[str, t.Any]
    variables: dict[str, t.Any]

    config: dict[str, t.Any]

    @abc.abstractmethod
    def __init__(self) -> None:
        self.actions = {}
        self.variables = {}

    @abc.abstractmethod
    def load(self) -> None:
        """Plugin's load"""

    @abc.abstractmethod
    def update(self) -> None:
        """Plugin's update"""
