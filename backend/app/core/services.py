"""Thread-safe service registry for cross-module communication."""

import threading
from typing import Any, Callable, Optional


class ServiceRegistry:
    """A simple registry that lets modules expose and consume named callables."""

    def __init__(self):
        self._lock = threading.Lock()
        self._services: dict[str, Callable] = {}

    def register(self, name: str, fn: Callable) -> None:
        """Register a callable under the given name."""
        with self._lock:
            self._services[name] = fn

    def call(self, name: str, *args, default: Optional[Any] = None, **kwargs) -> Any:
        """Call the named service, returning default if not registered."""
        with self._lock:
            fn = self._services.get(name)
        if fn is None:
            return default
        return fn(*args, **kwargs)

    def has(self, name: str) -> bool:
        with self._lock:
            return name in self._services
