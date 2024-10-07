from pypresence import ActivityType, Presence
from src.track import Track


class Rpc:
    def __init__(self) -> None:
        self.app_id = 1292562197389508789
        self._rpc = Presence(self.app_id)

    def connect(self) -> None:
        self._rpc.connect()

    def close(self) -> None:
        self._rpc.close()

    def clear(self) -> None:
        self._rpc.clear()

    def changePresence(self, track: Track, time_started: int) -> None:
        self._rpc.update(
            details=f"{track.name}",
            large_image=track.preview,
            state=", ".join(track.artists),
            small_image="yandex-music",
            start=time_started,
            end=int(time_started + track.duration_sec),
            activity_type=ActivityType.LISTENING,
            buttons=[{"label": "Яндекс Музыка", "url": track.link}],
        )

    def changePresencePaused(self, track: Track) -> None:
        self._rpc.update(
            details=f"{track.name}",
            large_image=track.preview,
            state=", ".join(track.artists),
            small_image="pause",
            activity_type=ActivityType.LISTENING,
            buttons=[{"label": "Яндекс Музыка", "url": track.link}],
        )
