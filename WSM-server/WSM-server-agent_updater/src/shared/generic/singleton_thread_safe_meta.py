import threading
from abc import ABCMeta


class SingletonThreadSafeMeta(metaclass=ABCMeta):
    _instance = {}
    _lock = threading.Lock()

    @classmethod
    def __call__(cls, *args, **kwargs):
        print(f"instances Logger {cls._instance}")
        with cls._lock:
            if cls not in cls._instance:
                cls._instance[cls] = super().__call__(*args, **kwargs)
        return cls._instance[cls]