from datetime import date, datetime, timedelta
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QMainWindow, QApplication
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from fefelson_sports.gui.components.name_logo import NameAndLogo

class ThumbPanel(QWidget):

    clicked = Signal(object)  # Define signal that emits game data

    def __init__(self, parent):
        super().__init__(parent)

        moneyFont = QFont("Times", 24, QFont.Bold)
        timeFont = QFont("Times", 15, QFont.Bold)

        moneyLayout = QHBoxLayout()

        self.gameTime = QLabel()
        self.gameTime.setFont(timeFont)
        self.gameTime.setAlignment(Qt.AlignCenter)
        
        self.teams = {}
        self.money = {}

        self.spread = QLabel("N/A")
        self.spread.setAlignment(Qt.AlignCenter)
        self.spread.setFont(moneyFont)

        for a_h in ("away", "home"):
            orient = "left" if a_h == "away" else "right"
            self.teams[a_h] = NameAndLogo(self, 180, orient)
            
            self.money[a_h] = QLabel("N/A")
            self.money[a_h].setAlignment(Qt.AlignCenter)
            self.money[a_h].setFont(moneyFont)

            moneyLayout.addWidget(self.money[a_h])
           
               
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.gameTime)
        mainLayout.addWidget(self.teams['away'], 1)
        mainLayout.addLayout(moneyLayout)
        mainLayout.addWidget(self.teams['home'], 1)
        mainLayout.addWidget(self.spread)



        self.setLayout(mainLayout)


    def mouseDoubleClickEvent(self, event):
        self.clicked.emit(self.title)  # Emit signal with game data
        super().mousePressEvent(event)


    def set_panel(self, game):

        self.title = game['title']
        gT = "%a %b %d\n%I:%M%p" if game["gameTime"].date() - date.today() >= timedelta(days=7) else "%a %I:%M%p"

        self.gameTime.setText(game["gameTime"].strftime(gT))

        try:
            self.spread.setText(game['odds'][-1]['home_spread'])
        except:
            self.spread.setText('N/A')

        for a_h in ("away", "home"):

            try:
                money = int(game['odds'][-1][f'{a_h}_ml'])
                money = f"+{money}" if int(money) > 0 else f"{money}"
            except (IndexError, ValueError):
                money = "N/A"

            self.money[a_h].setText(money)
            try:
                self.teams[a_h].set_team(game["teams"][a_h])
            except TypeError as e:
                print(e)




if __name__ == "__main__":
    app = QApplication()
    window = QMainWindow()
    panel = TickerPanel(window)
    window.setCentralWidget(panel)
    window.show()
    app.exec()