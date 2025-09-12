from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QTabWidget

from fefelson_sports.database.stores.gaming import GamingStore
from fefelson_sports.gui.components.name_logo import NameAndLogo
from fefelson_sports.gui.panels.gaming_panel import GamingTitle



class TopPanel(QWidget):

    def __init__(self):
        super().__init__()

        self.records = {}
        self.teamNames = {}
        self.gamingTitle = GamingTitle()

        recordFont = QFont("Serif", 20)
        recordFont.setBold(True)

        teamLayout = {}

        for a_h in ("away", "home"):
            self.teamNames[a_h] = NameAndLogo(self, 250, "right" if a_h == "away" else "left")

            self.records[a_h] = QLabel()
            self.records[a_h].setAlignment(Qt.AlignCenter)
            self.records[a_h].setFont(recordFont)

            teamLayout[a_h] = QVBoxLayout()
            teamLayout[a_h].addWidget(self.records[a_h])
            teamLayout[a_h].addWidget(self.teamNames[a_h], 0, Qt.AlignCenter)

        mainLayout = QHBoxLayout()
        mainLayout.addStretch(1)
        mainLayout.addLayout(teamLayout["away"])
        mainLayout.addWidget(self.gamingTitle)
        mainLayout.addLayout(teamLayout["home"])
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)


    def set_game(self, game):
        self.game = game 

        self.gamingTitle.set_game(game)
        for a_h in ("away", "home"):
            self.teamNames[a_h].set_team(game["teams"][a_h])


    def set_stats(self, session, timeFrame, awayHome):
        for a_h in ("away", "home"):
            awayHome = a_h if awayHome == "away_home" else awayHome
            stats =  GamingStore().get_gaming_results(self.game[f"{a_h}Id"], timeFrame, awayHome, session)
            
            self.records[a_h].setText(f"{stats['wins']} - {stats['loses']}")








class MatchupPanel(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.tabs = {}
        self.topPanel = TopPanel()
        
        midLayout = QHBoxLayout()
        for a_h in ("away", "home"):
            self.tabs[a_h] = QTabWidget()
            midLayout.addWidget(self.tabs[a_h])
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.topPanel)
        mainLayout.addLayout(midLayout, 1)

        self.setLayout(mainLayout)


    def set_game(self, game):

        self.topPanel.set_game(game)
        

    def set_stats(self, session, timeFrame, awayHome):
        self.topPanel.set_stats(session, timeFrame, awayHome)

        



class NBAPanel(MatchupPanel):

    def __init__(self, parent):
        super().__init__(parent)


class NFLPanel(MatchupPanel):

    def __init__(self, parent):
        super().__init__(parent)


class NCAABPanel(MatchupPanel):

    def __init__(self, parent):
        super().__init__(parent)


class NCAAFPanel(MatchupPanel):

    def __init__(self, parent):
        super().__init__(parent)