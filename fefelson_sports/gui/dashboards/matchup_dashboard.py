from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QComboBox, QScrollArea, QVBoxLayout, QHBoxLayout, 
                                QStackedLayout, QMainWindow, QApplication)

from ..panels.matchup_panel import NBAPanel, NCAABPanel
from ..panels.mlb_panel import MLBPanel
from ..panels.nfl_panel import NFLPanel
from ..panels.ncaaf_panel import NCAAFPanel


class MatchDash(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(1800, 800)

        self.currentSeason = None 
        self.currentPanel = None
        
        self.choiceBox = QComboBox(self)  

        self.ticker = QScrollArea(self)
        self.ticker.setWidgetResizable(True)  # Allow the widget to resize

        self.mainArea = QWidget(self)
        self.mlbPanel = MLBPanel(self.mainArea)
        self.nbaPanel = NBAPanel(self.mainArea)
        self.nflPanel = NFLPanel(self.mainArea)
        self.ncaabPanel = NCAABPanel(self.mainArea)
        self.ncaafPanel = NCAAFPanel(self.mainArea)
        
        self.stackedLayout = QStackedLayout()       
        self.stackedLayout.addWidget(self.mlbPanel)
        self.stackedLayout.addWidget(self.nbaPanel)
        self.stackedLayout.addWidget(self.nflPanel)
        self.stackedLayout.addWidget(self.ncaabPanel)
        self.stackedLayout.addWidget(self.ncaafPanel)
        self.mainArea.setLayout(self.stackedLayout)

        listLayout = QVBoxLayout()
        listLayout.addWidget(self.choiceBox)
        listLayout.addWidget(self.ticker)

        mainLayout = QHBoxLayout()
        mainLayout.addLayout(listLayout)
        mainLayout.addWidget(self.mainArea, 1)

        self.setLayout(mainLayout)


    def set_stats(self, session, timeFrame, awayHome):
        self.currentPanel.set_stats(session, timeFrame, awayHome)


    def _league_match(self, panel, session, timeFrame, awayHome, game):
        self.currentPanel = panel
        self.currentPanel.set_game(game)
        self.stackedLayout.setCurrentWidget(self.currentPanel)
        self.set_stats(session, timeFrame, awayHome)


    def mlb_match(self, session, timeFrame, awayHome, game):
        self._league_match(self.mlbPanel, session, timeFrame, awayHome, game)


    def nba_match(self, session, timeFrame, awayHome, game):
        self._league_match(self.nbaPanel, session, timeFrame, awayHome, game)


    def nfl_match(self, session, timeFrame, awayHome, game):
        self._league_match(self.nflPanel, session, timeFrame, awayHome, game)
        

    def ncaab_match(self, session, timeFrame, awayHome, game):
        self._league_match(self.ncaabPanel, session, timeFrame, awayHome, game)


    def ncaaf_match(self, session, timeFrame, awayHome, game):
        self._league_match(self.ncaafPanel, session, timeFrame, awayHome, game)


if __name__ == "__main__":
    app = QApplication()
    window = QMainWindow()
    panel = MatchPanel(window)
    window.setCentralWidget(panel)
    window.show()
    app.exec()