from typing import List

from .connection import Connection
from .cache import Cache
from .uri import URI
from .abc import Playable


class Track(Playable):
    def __init__(self, uri: URI, cache: Cache, name: str = None):
        super().__init__(uri=uri, cache=cache, name=name)

        self._album = None
        self._artists = None

    async def to_dict(self) -> dict:
        return {
            "uri": str(self._uri),
            "name": self._name,
            "album": self._album,
            "artists": self._artists
        }

    @staticmethod
    async def make_request(uri: URI, connection: Connection) -> dict:
        assert isinstance(uri, URI)
        assert isinstance(connection, Connection)

        endpoint = connection.add_parameters_to_endpoint(
            "tracks/{id}".format(id=uri.id),
            fields="uri,name,album(uri,name),artists(uri,name)",
        )
        return await connection.make_get_request(endpoint)

    def load_dict(self, data: dict):
        assert isinstance(data, dict)
        assert str(self._uri) == dict["uri"]

        self._name = data["name"]
        self._album = data["album"]
        self._artists = data["artists"]

    @property
    async def album(self) -> dict:
        if self._album is None:
            await self._cache.load(uri=self._uri)
        return self._album

    @property
    async def artists(self) -> List[dict]:
        if self._artists is None:
            await self._cache.load(uri=self._uri)
        return self._artists
