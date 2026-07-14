from collections.abc import Callable
from typing import Any

_handlers: dict[str, Callable[[Any], dict | None]] = {}


def register_handler(event_type):
    def decorator(handler):
        _handlers[event_type] = handler
        return handler

    return decorator


def get_handler(event_type):
    return _handlers.get(event_type)
