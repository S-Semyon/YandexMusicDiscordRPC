import os
from enum import Enum
from time import time

from src.track import Track, getCurrentTrack


class PlayerStatus(Enum):
    default = 0
    stop = 0
    play = 1


class Player:
    def __init__(self, token: str) -> None:
        self.current_player: str | None = None
        self.status: PlayerStatus = PlayerStatus.default
        self.token: str = token

        self.cached_title: str = ""
        self.cached_track: Track
        self.duration: int = 0

    @staticmethod
    def _exec(cmd: str) -> str:
        output = os.popen(cmd)
        out = output.read().removesuffix("\n")
        return out

    @classmethod
    def getPlayers(cls) -> list[str]:
        return cls._exec("playerctl -l").split("\n")

    def setPlayer(self, player: str) -> None:
        self.current_player = player

    def getTrackInfo(self) -> Track | None:
        status = self._exec("playerctl status")

        if status == "No players found":
            self.status = PlayerStatus.stop
            return
        elif status == "Playing":
            self.status = PlayerStatus.play
        else:
            self.status = PlayerStatus.stop

        title = self._exec(
            "playerctl -p " + self.current_player + ' metadata --format "{{title}}"'
        )

        if not title:
            return

        position = int(
            float(self._exec("playerctl -p " + self.current_player + " position"))
        )

        if self.cached_title == title:
            track = self.cached_track
        else:
            artists = self._exec(
                "playerctl -p "
                + self.current_player
                + ' metadata --format "{{artist}}"'
            )
            track = getCurrentTrack(title, artists, self.token)

        self.duration = time() - position
        self.cached_title = title
        self.cached_track = track

        if track is None:
            return

        return track
