from threading import Lock
from typing import Any, Dict


class Singleton(type):
    _instances: Dict = {}
    _lock: Lock = Lock()

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        with self._lock:
            if self not in self._instances:
                instance = super().__call__(*args, **kwds)
                self._instances[self] = instance
        return self._instances[self]
