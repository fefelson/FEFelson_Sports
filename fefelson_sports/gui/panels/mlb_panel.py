from datetime import date, timedelta
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea

from .matchup_panel import MatchupPanel
from .baseball_team import BaseballTeamStats
from .baseball_pitcher import PitcherStats



class FrontPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.pitcherStats = PitcherStats()
        self.teamStats= BaseballTeamStats()

        layout = QVBoxLayout()
        layout.addWidget(self.pitcherStats)
        layout.addWidget(self.teamStats, 1)

        self.setLayout(layout)


    def set_team(self, awayHome, team):
        self.pitcherStats.set_team(awayHome, team)
        self.teamStats.set_team(awayHome, team)


    def set_stats(self, session, timeFrame, awayHome):
        self.pitcherStats.set_stats(session, timeFrame, awayHome)
        self.teamStats.set_stats(session, timeFrame, awayHome)
        


class MLBPanel(MatchupPanel):

    def __init__(self, parent):
        super().__init__(parent)


        self.frontPanel = {}

        for a_h in ("away", "home"):
            
            self.frontPanel[a_h] = FrontPanel()
            self.tabs[a_h].addTab(self.frontPanel[a_h], "page1")


    def set_game(self, game):
        super().set_game(game)

        starters = game.get("pitchers", {})
        lineups = game.get("lineups", {})

        for a_h in ("away", "home"):

            starter = starters.get(a_h)
            lineup = lineups.get(a_h)

            team = {"starter": starter, "team": game["teams"][a_h], "lineup": lineup}

            self.frontPanel[a_h].set_team(a_h, team)



    def set_stats(self, session, timeFrame, awayHome):
        super().set_stats(session, timeFrame, awayHome)
        for a_h in ("away", "home"):
            self.frontPanel[a_h].set_stats(session, timeFrame, awayHome)
        

