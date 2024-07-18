# pyDeck daemon

StreamDeck or Macro-Deck copy in python

## ToDo

- [x] Buttons list --> dicts
- [x] Plugins list --> dict
- [ ] GUI API for server configuration
- [ ] Connection settings
- [ ] Actions args
- [ ] Plugin compilation/bundling (for external packages)
- [ ] User logs

## Development tools

- Ruff (Black)
- Pylint
- PyRight

## Configuration files

This files used to separate constants from code.

### pydeck/config.default.json

Default configuration.
Not supposed to be edited by user.

### pydeck/defaults.json

Default values for some objects.
Not supposed to be edited by user.

### pydeck/config.json

User configuration.
Override default configuration.

## Plugins

### How to make a plugin

#### 1.

You can either make it in one file:

```
plugins/
    my_plugin.py
```

or as a package with multiple files:

```
plugins/
    my_plugin/
        __init__.py
        other_file.py
```

#### 2.

You have to define class `Main` that inherits from `pydeck.DeckPlugin`

```python
class Main(DeckPlugin):

  name = "My plugin"
  description = "Example plugin"
  author = "Virashu"

  plugin_id = "my_plugin"

  def load(self): ...
  def update(self): ...
```

#### 3.

You can store user-accessible variables inside `self.variables` dictionary,
and actions for buttons inside `self.actions` dictionary.
