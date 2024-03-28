# Deck actions

## Problem

Deck must be able perform actions on button press.

Actions can either be simple (increment variable)
or complex (make http request -> update some values -> change button state).

Action may depend on (deck-)variables.

Action may need arguments from user.

## Proposal

At minimal - action is an callable
but there are different ways to wrap it.

### 1. Class

```python
class Action:
  def __init__(self, callable_id: str, fields: dict):
    """ Callable id like  """
    self._callable = # Resolve from global actions
    self.fields = fields

  def call(self, **kwargs):
    self._callable(**self.kwargs)

callable_id = "system__launch"
fields = {
  "a": {
    "type": "int",
    "def": 0,
    "desc": "Some var"
  }
}
```

Fields is needed for GUI settings.

### 2. Annotations

```python
def func(a: int = 0): ...

func.__annotations__
```