from datetime import date, timedelta
from collections import defaultdict

from .front_panel import FootballFrontPanel
from .matchup_panel import MatchupPanel





class NFLPanel(MatchupPanel):

    def __init__(self, parent):
        super().__init__(parent)


        self.frontPanel = {}

        for a_h in ("away", "home"):
            
            self.frontPanel[a_h] = FootballFrontPanel("NFL", a_h)
            self.tabs[a_h].addTab(self.frontPanel[a_h], "page1")


    def set_game(self, game):
        super().set_game(game)

        for a_h in ("away", "home"):

            self.frontPanel[a_h].set_team(game["teams"][a_h])



    def set_stats(self, session, timeFrame, awayHome):
        super().set_stats(session, timeFrame, awayHome)
        for a_h in ("away", "home"):
            self.frontPanel[a_h].set_stats(session, timeFrame, awayHome)
        

