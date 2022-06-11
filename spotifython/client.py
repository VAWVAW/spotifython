import json

from .connection import Connection
from .cache import Cache
from .user import User
from .playlist import Playlist
from .track import Track
from .uri import URI
from .abc import Playable, PlayContext, Cacheable
from .errors import BadRequestException
from .episode import Episode
from .album import Album
from .artist import Artist
from .show import Show
from .authentication import Authentication


class Client:
    def __init__(self, authentication: Authentication, cache_dir: str = None):
        """
        You need to request a token using Client.request_token() to interact with the api.

        You need to register an application at https://developer.spotify.com/dashboard/applications and edit the settings to add "http://localhost:2342/" to the redirect uris to allow this library to request a token.
        :param authentication: Authentication object for client authentication
        :param cache_dir: global path to the directory that this library should cache data in (note that sensitive data you request may be cached, set to None to disable caching)
        """
        assert isinstance(cache_dir, (str | None))
        assert isinstance(authentication, Authentication)

        self._connection = Connection(authentication=authentication)
        self._cache = Cache(connection=self._connection, cache_dir=cache_dir)

    def get_authentication_data(self) -> dict[str, (str | int | None)]:
        """
        Dump the authentication data for safe caching
        :return: { "client_id": client_id, "client_secret": client_secret, "scope": str(scope), "refresh_token": refresh_token, "show_dialog": show_dialog, "token": token, "expires": int(expires) }
        """
        return self._connection.dump_token_data()

    async def play(self, elements: list[(URI | Playable)] = None, context: (URI | PlayContext) = None, offset: int = None, position_ms: int = None, device_id: str = None):
        """
        resume playback or play specified resource\n
        only one of elements and context may be specified\n\n
        examples:\n
        await Client.play()\n
        await Client.play(context="spotify:album:5ht7ItJgpBH7W6vJ5BqpPr", offset=5, position_ms=1000)

        :param elements: list of spotify uris or Playable types to play (leave at None to resume playing)
        :param context: uri or PlayContext to use as context (e.g. playlist or album)
        :param offset: number of song in resource to start playing (only used if context_uri is set)
        :param position_ms: position in song to seek (only used if context_uri is set)
        :param device_id: device to target (leave at None to use currently active device
        :raises SpotifyException: errors according to http response status
        """
        assert isinstance(elements, (list | None))
        assert isinstance(context, (URI | PlayContext | None))
        assert isinstance(offset, (int | None))
        assert isinstance(position_ms, (int | None))
        assert isinstance(device_id, (str | None))

        data = {}
        send_payload = False

        endpoint = self._connection.add_parameters_to_endpoint("me/player/play", device_id=device_id)

        if offset is not None:
            data["offset"] = {"position": offset}
        if position_ms is not None:
            data["position_ms"] = position_ms

        if context is not None:
            data["context_uri"] = str(context if isinstance(context, URI) else await context.uri)
            send_payload = True

        if elements is not None:
            if send_payload:
                raise BadRequestException("only one of elements and context may be specified")
            data["uris"] = []
            for element in elements:
                assert isinstance(element, (URI | Playable))
                data["uris"].append(str(element if isinstance(element, URI) else await element.uri))
            send_payload = True

        if send_payload:
            # play specified resource
            await self._connection.make_request(method="PUT", endpoint=endpoint, data=json.dumps(data))
        else:
            # resume whatever was playing
            await self._connection.make_request(method="PUT", endpoint=endpoint)

    async def pause(self, device_id: str = None):
        """
        pause playback

        :param device_id: device to target (leave at None to use currently active device
        :raises SpotifyException: errors according to http response status
        """
        assert isinstance(device_id, (str | None))

        endpoint = self._connection.add_parameters_to_endpoint("me/player/pause", device_id=device_id)

        await self._connection.make_request(method="PUT", endpoint=endpoint)

    async def next(self, device_id: str = None):
        """
        skip to next track in queue

        :param device_id:
        :raises SpotifyException: errors according to http response status
        """
        assert isinstance(device_id, (str | None))

        endpoint = self._connection.add_parameters_to_endpoint("me/player/next", device_id=device_id)

        await self._connection.make_request(method="POST", endpoint=endpoint)

    async def prev(self, device_id: str = None):
        """
        skip to previous track in queue

        :param device_id:
        :raises SpotifyException: errors according to http response status
        """
        assert isinstance(device_id, (str | None))

        endpoint = self._connection.add_parameters_to_endpoint("me/player/previous", device_id=device_id)

        await self._connection.make_request(method="POST", endpoint=endpoint)

    async def set_playback_shuffle(self, state: bool = True, device_id: str = None):
        """
        set shuffle mode on the specified device

        :param state: whether to activate shuffle
        :param device_id: device to target (leave at None to use currently active device
        :raises SpotifyException: errors according to http response status
        """
        assert isinstance(state, bool)
        assert isinstance(device_id, (str | None))

        endpoint = self._connection.add_parameters_to_endpoint("me/player/shuffle", device_id=device_id, state=state)

        await self._connection.make_request(method="PUT", endpoint=endpoint)

    async def add_to_queue(self, element: (URI | Playable), device_id: str = None):
        """
        add uri to queue \n\n
        example: \n
        await SpotifyClient.add_to_queue("spotify:track:4iV5W9uYEdYUVa79Axb7Rh")

        :param element: resource to add to queue
        :param device_id: device to target (leave at None to use currently active device
        :raises SpotifyException: errors according to http response status
        """
        assert isinstance(element, (URI | Playable))
        assert isinstance(device_id, (str | None))

        endpoint = self._connection.add_parameters_to_endpoint("me/player/queue", device_id=device_id, uri=str(element if isinstance(element, URI) else await element.uri))
        await self._connection.make_request(method="POST", endpoint=endpoint)

    async def close(self):
        """
        clean session and exit
        """
        await self._connection.close()

    async def get_devices(self) -> list[dict[str, (str | bool | int)]]:
        """
        return a list of all devices registered in spotify connect
        """
        endpoint = "me/player/devices"
        data = await self._connection.make_request(method="GET", endpoint=endpoint)
        return data["devices"]

    async def transfer_playback(self, device_id: str, play: bool = False):
        """
        transfer playback to new device
        :param device_id: id of targeted device
        :param play: whether to start playing on new device
        """
        assert isinstance(device_id, (str | None))
        assert isinstance(play, bool)

        endpoint = "me/player"
        await self._connection.make_request(method="PUT", endpoint=endpoint, data=json.dumps({"device_ids": [device_id], "play": play}))

    async def user_playlists(self) -> list[Playlist]:
        """
        get playlists of current user
        :return: list of playlists saved in the user profile
        """
        return await (await self._cache.get_me()).playlists

    async def get_playlist(self, uri: URI) -> Playlist:
        """
        return Playlist object for the given id
        :param uri: uri of the playlist
        """
        assert isinstance(uri, URI)

        return self._cache.get_playlist(uri=uri)

    async def get_track(self, uri: URI) -> Track:
        """
        return Track object for the given id
        :param uri: uri of the track
        """
        assert isinstance(uri, URI)

        return self._cache.get_track(uri=uri)

    async def get_user(self, uri: URI) -> User:
        """
        return User object for the given id
        :param uri: uri of the user
        """
        assert isinstance(uri, URI)

        return self._cache.get_user(uri=uri)

    async def get_playing(self) -> dict:
        """
        returns information to playback state
        :return: dict with is_playing, device, repeat_state, shuffle_state, context(playlist), item(track), actions
        """
        endpoint = "me/player"

        return await self._connection.make_request(method="GET", endpoint=endpoint)

    async def search(self, query: str, element_type: str, limit: int = 5, offset: int = 0) -> dict[str, list[Cacheable]]:
        """
        search for item

        :param query: string to search
        :param element_type: comma-separated list of return types; possible values: "album" "artist" "playlist" "track" "episode" "show"
        :param limit: number of results to return per type
        :param offset: offset of results per type
        :return: dict with types as keys and lists as elements
        """
        assert isinstance(query, str)
        assert isinstance(element_type, str)
        assert isinstance(limit, int)
        assert isinstance(offset, int)

        endpoint = self._connection.add_parameters_to_endpoint(
            "search",
            offset=offset,
            limit=limit,
            q=query,
            type=element_type
        )
        data = await self._connection.make_request(method="GET", endpoint=endpoint)
        types = element_type.split(",")
        ret = {}
        for element_type in types:
            element_type += "s"
            ret[element_type] = []
            for element in data[element_type]["items"]:
                ret[element_type].append(self._cache.get_element(uri=URI(element["uri"])))
                ret[element_type][-1].load_dict(data=element)
        return ret

    async def search_track(self, query: str, limit: int = 5, offset: int = 0) -> list[Track]:
        """
        search for track

        :param query: string to search
        :param limit: number of results to return
        :param offset: offset of results
        :return: list of the found tracks
        """
        elements = (await self.search(query=query, element_type="track", offset=offset, limit=limit))["tracks"]
        for element in elements:
            assert isinstance(element, Track), "got invalid search result"
        # noinspection PyTypeChecker
        return elements

    async def search_episode(self, query: str, limit: int = 5, offset: int = 0) -> list[Episode]:
        """
        search for episode

        :param query: string to search
        :param limit: number of results to return
        :param offset: offset of results
        :return: list of the found episodes
        """
        elements = (await self.search(query=query, element_type="episode", offset=offset, limit=limit))["episodes"]
        for element in elements:
            assert isinstance(element, Episode), "got invalid search result"
        # noinspection PyTypeChecker
        return elements

    async def search_playlist(self, query: str, limit: int = 5, offset: int = 0) -> list[Playlist]:
        """
        search for playlist

        :param query: string to search
        :param limit: number of results to return
        :param offset: offset of results
        :return: list of the found playlists
        """
        elements = (await self.search(query=query, element_type="playlist", offset=offset, limit=limit))["playlists"]
        for element in elements:
            assert isinstance(element, Playlist), "got invalid search result"
        # noinspection PyTypeChecker
        return elements

    async def search_album(self, query: str, limit: int = 5, offset: int = 0) -> list[Album]:
        """
        search for album

        :param query: string to search
        :param limit: number of results to return
        :param offset: offset of results
        :return: list of the found albums
        """
        elements = (await self.search(query=query, element_type="album", offset=offset, limit=limit))["albums"]
        for element in elements:
            assert isinstance(element, Album), "got invalid search result"
        # noinspection PyTypeChecker
        return elements

    async def search_artist(self, query: str, limit: int = 5, offset: int = 0) -> list[Artist]:
        """
        search for artist

        :param query: string to search
        :param limit: number of results to return
        :param offset: offset of results
        :return: list of the found artists
        """
        elements = (await self.search(query=query, element_type="artist", offset=offset, limit=limit))["artists"]
        for element in elements:
            assert isinstance(element, Artist), "got invalid search result"
        # noinspection PyTypeChecker
        return elements

    async def search_user(self, query: str, limit: int = 5, offset: int = 0) -> list[User]:
        """
        search for user

        :param query: string to search
        :param limit: number of results to return
        :param offset: offset of results
        :return: list of the found users
        """
        elements = (await self.search(query=query, element_type="user", offset=offset, limit=limit))["users"]
        for element in elements:
            assert isinstance(element, User), "got invalid search result"
        # noinspection PyTypeChecker
        return elements

    async def search_show(self, query: str, limit: int = 5, offset: int = 0) -> list[Show]:
        """
        search for show

        :param query: string to search
        :param limit: number of results to return
        :param offset: offset of results
        :return: list of the found users
        """
        elements = (await self.search(query=query, element_type="show", offset=offset, limit=limit))["shows"]
        for element in elements:
            assert isinstance(element, User), "got invalid search result"
        # noinspection PyTypeChecker
        return elements

    async def search_playable(self, query: str, limit: int = 5, offset: int = 0) -> list[Playable]:
        """
        search for playable

        :param query: string to search
        :param limit: number of results to return
        :param offset: offset of results
        :return: list of the found playables
        """
        data = await self.search(query=query, element_type="track,episode", offset=offset, limit=limit)
        elements = data["tracks"] + data["episodes"]
        for element in elements:
            assert isinstance(element, Playable), "got invalid search result"
        # noinspection PyTypeChecker
        return elements