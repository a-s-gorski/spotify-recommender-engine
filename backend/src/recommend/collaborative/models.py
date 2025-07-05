from typing import List

from beanie import Document
from pydantic import Field


class Playlist(Document):
    name: str
    tracks: List[str]

    class Settings:
        name = "playlists"


class Track(Document):
    id: str = Field(alias="_id")  # Track URI as _id
    pos: int
    artist_name: str
    track_uri: str
    artist_uri: str
    track_name: str
    album_uri: str
    duration_ms: int
    album_name: str

    class Settings:
        name = "tracks"
