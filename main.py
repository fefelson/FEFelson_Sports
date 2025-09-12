from os import environ

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QToolBar

from fefelson_sports.database.stores.matchup import MatchupStore
from fefelson_sports.database.orms.database import get_db_session
from fefelson_sports.gui.dashboards.matchup_dashboard import MatchDash
from fefelson_sports.gui.panels.ticker_panel import ThumbPanel


# for debugging
# from pprint import pprint 



BASE_PATH = f"{environ['HOME']}/FEFelson/FEFelson_Sports"

class MainWindow(QMainWindow):

    _defaultTF = "1Month"
    _defaultAH = "all"

    def __init__(self):
        super().__init__()

        self.setWindowTitle("FEFelson MoneyMaker")

        self.gameData = MatchupStore().get_game_data()
        self.timeFrame = self._defaultTF

        self.mainPanel = MatchDash()
        self.mainPanel.choiceBox.addItems(sorted(list(self.gameData.keys())))
        self.mainPanel.choiceBox.textActivated.connect(self.choice)
    
        self._set_toolbar()

        self.setCentralWidget(self.mainPanel)


    def _set_a_h(self, label):
        if self.away_home != label:
            self.away_home = label
            self.mainPanel.set_stats(self._use_session(), self.timeFrame, self.away_home)


    def _set_timeFrame(self, label):
        if self.timeFrame != label:
            self.timeFrame = label
            self.mainPanel.set_stats(self._use_session(), self.timeFrame, self.away_home)


    def _set_toolbar(self):
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(25, 25))
        self.addToolBar(toolbar)

        all_action = QAction(
            QIcon(f"{BASE_PATH}/data/universal.png"),
            "All Stats",
            self,
        )
        all_action.setStatusTip("All Stats")
        all_action.triggered.connect(self.set_timeFrame_all)
        toolbar.addAction(all_action)

        season_action = QAction(
            QIcon(f"{BASE_PATH}/data/acorn.png"),
            "Season",
            self,
        )
        season_action.setStatusTip("Season")
        season_action.triggered.connect(self.set_timeFrame_season)
        toolbar.addAction(season_action)

        sixty_action = QAction(
            QIcon(f"{BASE_PATH}/data/star-half.png"),
            "60 Days",
            self,
        )
        sixty_action.setStatusTip("60 Days")
        sixty_action.triggered.connect(self.set_timeFrame_60)
        toolbar.addAction(sixty_action)

        thirty_action = QAction(
            QIcon(f"{BASE_PATH}/data/star.png"),
            "30 Days",
            self,
        )
        thirty_action.setStatusTip("30 Days")
        thirty_action.triggered.connect(self.set_timeFrame_30)
        toolbar.addAction(thirty_action)

        twoWeeks_action = QAction(
            QIcon(f"{BASE_PATH}/data/service-bell.png"),
            "2 Weeks",
            self,
        )
        twoWeeks_action.setStatusTip("2 Weeks")
        twoWeeks_action.triggered.connect(self.set_timeFrame_14)
        toolbar.addAction(twoWeeks_action)

        all_a_h_action = QAction(
            QIcon(f"{BASE_PATH}/data/all.png"),
            "All Games",
            self,
        )
        all_a_h_action.setStatusTip("all")
        all_a_h_action.triggered.connect(self.set_a_h_all)
        toolbar.addAction(all_a_h_action)

        away_home_a_h_action = QAction(
            QIcon(f"{BASE_PATH}/data/home.png"),
            "away_home",
            self,
        )
        away_home_a_h_action.setStatusTip("away_home")
        away_home_a_h_action.triggered.connect(self.set_a_h_away_home)
        toolbar.addAction(away_home_a_h_action)

        


    def _use_session(self):
        """Execute a function with an appropriate session, either provided or new."""
        with get_db_session() as session:
            return session


    def choice(self, signal):
        # Create a new widget for the scroll area
        scrollPanel = QWidget()
        scrollLayout = QVBoxLayout()
        scrollPanel.setLayout(scrollLayout)

        # Populate the scroll panel with ThumbPanel widgets
        for game in self.gameData[signal].values():
            thumbPanel = ThumbPanel(scrollPanel)
            thumbPanel.set_panel(game)
            thumbPanel.clicked.connect(self.new_matchup)
            scrollLayout.addWidget(thumbPanel)
            scrollLayout.addSpacing(40)

        # Add a stretch to push content to the top
        scrollLayout.addStretch(1)

        # Set the new widget in the scroll area
        self.mainPanel.ticker.setWidget(scrollPanel)


    def new_matchup(self, signal):
        leagueId = signal.split("_")[0]
        game = self.gameData[leagueId][signal]
        self.timeFrame = self._defaultTF
        self.away_home = self._defaultAH
        
        if leagueId == "MLB":
            self.mainPanel.mlb_match(self._use_session(), self.timeFrame, self.away_home, game)

        elif leagueId == "NBA":
            self.mainPanel.nba_match(self._use_session(), self.timeFrame, self.away_home, game)

        elif leagueId == "NFL":
            self.mainPanel.nfl_match(self._use_session(), self.timeFrame, self.away_home, game)

        elif leagueId == "NCAAB":
            self.mainPanel.ncaab_match(self._use_session(), self.timeFrame, self.away_home, game)

        elif leagueId == "NCAAF":
            self.mainPanel.ncaaf_match(self._use_session(), self.timeFrame, self.away_home, game)


    def set_a_h_all(self, s):
        self._set_a_h("all")
        

    def set_a_h_away_home(self, s):
        self._set_a_h("away_home")


    def set_timeFrame_14(self, s):
        self._set_timeFrame("2Weeks")
        

    def set_timeFrame_30(self, s):
        self._set_timeFrame("1Month")


    def set_timeFrame_60(self, s):
        self._set_timeFrame("2Months")


    def set_timeFrame_season(self, s):
        self._set_timeFrame("Season")


    def set_timeFrame_all(self, s):
        self._set_timeFrame("All")
    

        



    
if __name__ == "__main__":
    

    
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()

   