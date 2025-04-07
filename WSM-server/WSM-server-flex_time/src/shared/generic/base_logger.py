from abc import abstractmethod

from src.shared.generic.singleton_thread_safe_meta import SingletonThreadSafeMeta


class BaseLogger(SingletonThreadSafeMeta):
    @abstractmethod
    def debug(cls, message: str):
        pass

    @abstractmethod
    def info(cls, message: str):
        pass

    @abstractmethod
    def warning(cls, message: str):
        pass

    @abstractmethod
    def error(cls, message: str):
        pass

    @abstractmethod
    def critical(cls, message: str):
        pass