from abc import ABC, abstractmethod

from .uri import URI
from .connection import Connection
from .cache import Cache


class Cacheable(ABC):
    def __init__(self, uri: URI, cache: Cache, name: str = None):
        self._uri = uri
        self._name = name
        self._cache = cache

    @property
    async def uri(self) -> URI:
        return self._uri

    @property
    async def name(self) -> str:
        if self._name is None:
            await self._cache.load(self._uri)
        return self._name

    @abstractmethod
    def load_dict(self, data: dict):
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @staticmethod
    @abstractmethod
    def make_request(uri: URI, connection: Connection) -> dict:
        pass
