from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QMainWindow, QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from fefelson_sports.gui.components.logo_component import LogoComponent  

class NameAndLogo(QWidget):

    default_size = 420

    def __init__(self, parent, x_size=default_size, orient="right"):
        super().__init__(parent)
        self.setFixedWidth(x_size)

        fontSize = int(x_size * 0.06)  # Reduced to 6% for better fit
        logoSize = int(x_size * 0.4)   # Increased to 40% for better balance

        fontSize = max(13, min(fontSize, 24))  # Tighter font size range
        logoSize = max(60, min(logoSize, 180))

        nameFont = QFont("Times", fontSize, QFont.Bold)

        self.firstName = QLabel("Mississippi Valley State", self)
        self.firstName.setFont(nameFont)
        self.firstName.setAlignment(Qt.AlignBottom)
        
        self.lastName = QLabel("Delta Devils", self)
        self.lastName.setFont(nameFont)
        self.lastName.setAlignment(Qt.AlignTop)
        
        self.logo = LogoComponent(self, logoSize)

        nameLayout = QVBoxLayout()
        nameLayout.addWidget(self.firstName)
        nameLayout.addWidget(self.lastName)

        mainLayout = QHBoxLayout()
        if orient == "right":
            # logo on the right
            mainLayout.addLayout(nameLayout)
            mainLayout.addWidget(self.logo)
        else:
            # logo on the left
            mainLayout.addWidget(self.logo)
            mainLayout.addLayout(nameLayout)

        self.setLayout(mainLayout)


    def set_team(self, team):
        
        try:
            self.firstName.setText(team["first_name"])
            self.lastName.setText(team["last_name"])
        except KeyError:
            self.firstName.setText("N/A")
            self.lastName.setText("N/A")
        try:
            self.logo.set_logo(team["org_id"])
            if team["type"] == "school":
                self.logo.setStyleSheet(f"background-color: #{team['primaryColor']};")
            else:
                self.logo.setStyleSheet(f"background-color: #{team['secondaryColor']};")
        except KeyError:
            self.logo.set_logo(-1)


   

if __name__ == "__main__":
    app = QApplication()
    window = QMainWindow()
    panel = NameArea(window, 200)
    window.setCentralWidget(panel)
    window.show()
    app.exec()