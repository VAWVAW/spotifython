# resolve circular dependencies
from __future__ import annotations


class URI:
    def __init__(self, uri_string: str):
        assert isinstance(uri_string, str)
        uri_elements = uri_string.split(":")
        assert len(uri_elements) == 3 and uri_elements[0] == "spotify", 'invalid uri string (not in format "spotify:<type>:<id>")'

        self._type = uri_elements[1]
        self._id = uri_elements[2]

    @classmethod
    def from_values(cls, datatype: str, uid: str) -> URI:
        assert isinstance(datatype, str)
        assert isinstance(uid, str)

        new_uri = cls.__new__(cls)
        new_uri._type = datatype
        new_uri._id = uid
        return new_uri

    def __str__(self):
        return "spotify:" + self._type + ":" + self._id

    @property
    def id(self) -> str:
        return self._id

    @property
    def type(self) -> str:
        return self._type
