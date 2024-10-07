from threading import Thread
from time import sleep, time

import requests
from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import QByteArray, QTimer

from src.player import Player, PlayerStatus
from src.presence import Rpc
from src.ym_token import TokenWindow, getToken, writeToken


def format_seconds(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes:02}:{remaining_seconds:02}"


class _UiType:
    def __init__(self) -> None:
        self.selectSource: QtWidgets.QComboBox
        self.tokenInput: QtWidgets.QLineEdit
        self.songName: QtWidgets.QLabel
        self.authorName: QtWidgets.QLabel
        self.splash: QtWidgets.QLabel
        self.currentTime: QtWidgets.QLabel
        self.currentTimeBar: QtWidgets.QProgressBar
        self.trackSize: QtWidgets.QLabel
        self.getToken: QtWidgets.QPushButton
        self.toggleService: QtWidgets.QPushButton


class Ui(QtWidgets.QMainWindow, _UiType):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("src/window.ui", self)
        self.setWindowIcon(QtGui.QIcon("src/yandex-music.png"))

        self.setSplash("src/yandex-music.png")

        self.ym_token = getToken()
        self.tokenInput.setText(self.ym_token)
        self.getToken.pressed.connect(self.oauth)
        self.toggleService.pressed.connect(self.funcToggleService)

        self.player = Player(self.ym_token)
        self.rpc = Rpc()

        self.listen_start = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.addPlayers)
        self.timer.start(1000)

        self.show()

    def closeEvent(self, event):
        self.listen_start = False
        self.close()

    def resizeEvent(self, event):
        size = min(self.width(), self.height())
        self.splash.setFixedSize(size - 80, size - 80)
        super().resizeEvent(event)

    def funcToggleService(self):
        if not self.listen_start:
            source = self.selectSource.currentText()
            if not source:
                return
            self.player.setPlayer(source)
            Thread(None, self.listen, daemon=True).start()
            self.toggleService.setText("Стоп")
        else:
            self.toggleService.setText("Старт")

        self.listen_start = not self.listen_start

    def addPlayers(self):
        text = self.selectSource.currentText()
        players = self.player.getPlayers()
        self.selectSource.clear()
        self.selectSource.addItems(players)
        if text in players:
            self.selectSource.setCurrentText(text)

    def setSplashFromUrl(self, url):
        response = requests.get(url)
        image_data = response.content

        image = QtGui.QImage()
        image.loadFromData(QByteArray(image_data))

        pixmap = QtGui.QPixmap.fromImage(image)
        self.splash.setPixmap(pixmap)

    def setSplash(self, image: str) -> None:
        self.splash.setPixmap(QtGui.QPixmap(image))

    def oauth(self):
        oauth_url = "https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d"
        self.token_window = TokenWindow(oauth_url, "src/yandex-music.png", self)
        self.token_window.show()

    def secondWindowClosed(self):
        self.ym_token = self.token_window.token if self.token_window.token else ""
        self.tokenInput.setText(self.ym_token)
        writeToken(self.ym_token)

    def listen(self):
        self.rpc.connect()
        cached_title = ""
        while self.listen_start:
            track = self.player.getTrackInfo()
            if track:
                if track.name != cached_title:
                    self.songName.setText("Текущая песня: " + track.name)
                    self.authorName.setText("Автор: " + ",".join(track.artists))
                    self.setSplashFromUrl(track.preview)

                cached_title = track.name

                if self.player.status == PlayerStatus.play:
                    self.rpc.changePresence(track, self.player.duration)
                else:
                    self.rpc.changePresencePaused(track)
            else:
                self.rpc.clear()

            for _ in range(5):
                if self.player.status == PlayerStatus.play:
                    _time = int(time() - self.player.duration)
                    self.currentTime.setText(
                        format_seconds(
                            _time if _time < track.duration_sec else track.duration_sec
                        )
                    )
                    duration = int(_time / track.duration_sec * 100)
                    self.currentTimeBar.setValue(duration)
                    self.trackSize.setText(format_seconds(track.duration_sec))
                sleep(1)
                track = self.player.getTrackInfo()

        self.rpc.close()
