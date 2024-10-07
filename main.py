import sys

from PyQt5 import QtWidgets

from src.window import Ui

print("Автор: https://github.com/S-Semyon")

app = QtWidgets.QApplication(sys.argv)
window = Ui()
sys.exit(app.exec_())
