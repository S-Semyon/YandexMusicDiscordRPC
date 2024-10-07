import os
from pathlib import Path

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from PyQt5.QtWidgets import QVBoxLayout, QWidget

config_folder = Path(os.getenv("HOME")) / ".config/"
program_folder = config_folder / "ymdr/"
program_folder.mkdir(exist_ok=True)
token_file = program_folder / Path("token")


def getToken() -> str:
    if token_file.exists():
        with open(token_file) as f:
            return f.read()
    return ""


def writeToken(token: str) -> None:
    with open(token_file, "w") as f:
        f.write(token)


class CustomWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        pass


class TokenWindow(QWidget):
    def __init__(self, url, icon_path, main_window):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setGeometry(100, 100, 700, 800)
        self.setWindowIcon(QIcon(icon_path))
        self.main_window = main_window

        self.browser = QWebEngineView()
        self.browser.setPage(CustomWebEnginePage(self.browser))
        self.browser.page().profile().cookieStore().deleteAllCookies()
        self.browser.urlChanged.connect(self.on_url_changed)

        self.browser.setUrl(QUrl(url))

        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        self.setLayout(layout)

        self.token = None

    def on_url_changed(self, url):
        url_str = url.toString()
        if "#access_token" in url_str:
            self.token = url_str.split("=")[1].split("&")[0]
            self.close()

    def closeEvent(self, event):
        self.main_window.secondWindowClosed()
        event.accept()
