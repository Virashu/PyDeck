# pyDeck daemon

StreamDeck or Macro-Deck copy in python

## How plugins work

[Markdown doc](./pydeck/plugins/README.md)



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

