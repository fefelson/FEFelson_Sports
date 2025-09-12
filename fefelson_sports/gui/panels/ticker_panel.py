from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QMainWindow, QApplication
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from fefelson_sports.gui.components.name_logo import NameAndLogo

class ThumbPanel(QWidget):

    clicked = Signal(object)  # Define signal that emits game data

    def __init__(self, parent):
        super().__init__(parent)

        moneyFont = QFont("Times", 24, QFont.Bold)
        moneyLayout = QHBoxLayout()

        self.teams = {}
        self.money = {}

        for a_h in ("away", "home"):
            orient = "left" if a_h == "away" else "right"
            self.teams[a_h] = NameAndLogo(self, 180, orient)
            
            self.money[a_h] = QLabel("N/A")
            self.money[a_h].setAlignment(Qt.AlignCenter)
            self.money[a_h].setFont(moneyFont)

            moneyLayout.addWidget(self.money[a_h])
               
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.teams['away'], 1)
        mainLayout.addLayout(moneyLayout)
        mainLayout.addWidget(self.teams['home'], 1)

        self.setLayout(mainLayout)


    def mouseDoubleClickEvent(self, event):
        self.clicked.emit(self.title)  # Emit signal with game data
        super().mousePressEvent(event)


    def set_panel(self, game):
        self.title = game['title']

        for a_h in ("away", "home"):

            try:
                money = int(game['odds'][-1][f'{a_h}_ml'])
                money = f"+{money}" if int(money) > 0 else f"{money}"
            except (IndexError, ValueError):
                money = "N/A"

            self.money[a_h].setText(money)
            self.teams[a_h].set_team(game["teams"][a_h])




if __name__ == "__main__":
    app = QApplication()
    window = QMainWindow()
    panel = TickerPanel(window)
    window.setCentralWidget(panel)
    window.show()
    app.exec()