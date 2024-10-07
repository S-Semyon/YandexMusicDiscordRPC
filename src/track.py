from dataclasses import dataclass
from typing import List

from yandex_music import Client
from yandex_music.track.track import Track as TrackYandex


@dataclass
class Track:
    artists: List[str]
    name: str
    preview: str
    link: str
    duration_sec: int
    track: TrackYandex


def getCurrentTrack(name: str, artist: str, token: str | None = None) -> Track | None:
    client = Client(token).init() if token else Client()
    try:
        track = client.search(text=f"{name} {artist}", type_="track")
        track = track.tracks.results[0]
        track = Track(
            [artist.name for artist in track.artists],
            track.title,
            "https://" + track.cover_uri.replace("%%", "1000x1000"),
            f"https://music.yandex.ru/album/{track.albums[0].id}/track/{track.id}",
            int(track.duration_ms / 1000),
            track,
        )
        return track

    except Exception as e:
        print("An error occurred: ", e)

    return None
