import os
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


BASE_PATH = os.environ["HOME"]+"/FEFelson/FEFelson_Sports/team_logos"

class LogoComponent(QWidget):
    def __init__(self, parent=None, size=300):
        super().__init__(parent)
        self.size = size

        self.logo = QLabel(self)
        self.logo.setFixedSize(size, size)
        self.set_logo_pixmap(f"{BASE_PATH}/default.jpg")

        layout = QHBoxLayout()
        layout.addWidget(self.logo)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


    def set_logo_pixmap(self, path):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            pixmap = QPixmap(f"{BASE_PATH}/default.jpg")
        scaled = pixmap.scaled(
            self.size, self.size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.logo.setPixmap(scaled)


    def set_logo(self, teamId):
        logo_path = f"{BASE_PATH}/{teamId}.png"
        self.set_logo_pixmap(logo_path)


