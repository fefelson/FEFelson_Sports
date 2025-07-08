from .team_controller import TeamController
from .ticker_controller import TickerController

from ..stores.game_line_store import GameLineStore
from ..stores.matchup_store import MatchupStore
from ..views.dashboards.matchup_dashboard import MatchupDashboard


###################################################################################
###################################################################################



class MatchupController:

    def __init__(self, frame, leagues):

        self.leagues = leagues

        self.model = MatchupStore()
        self.gameLine = GameLineStore()

        self.dashboard = MatchupDashboard(frame)     
        self.awayController = TeamController(self.dashboard.awayPanel)
        self.homeController = TeamController(self.dashboard.homePanel)
        self.tickerController = TickerController(self.dashboard.tickerPanel, parentCtrl=self)
        

    def set_gamedate(self, gamedate):
        matchups = self.model.get_gamedate(self.leagues, gamedate)
        self.tickerController.set_ticker_panel(matchups) 
        

    def on_team(self, teamId, leagueId, gameId):
        league = self.leagues[leagueId]
        season = league.get_current_season() 

        self.awayController.new_team(leagueId, teamId, season)
        team = self.awayController.get_team()
        gaming = self.awayController.get_gaming()

        self.dashboard.chartPanel.ptsSpreadChart.set_panel(team, *GameLineStore.get_pts_spread_chart(gaming))
        self.dashboard.chartPanel.atsChart.set_panel(team, *GameLineStore.get_ats_chart(gaming))
        self.dashboard.chartPanel.winLossChart.set_panel(team, *GameLineStore.get_win_loss_chart(gaming))
        
        self.dashboard.chartPanel.Layout()


        self.dashboard.chartPanel.Show()
        self.dashboard.homePanel.Hide()
        self.dashboard.Layout()


    def on_click(self, leagueId, gameId):
        league = self.leagues[leagueId]
        season = league.get_current_season() 

        self.dashboard.chartPanel.Hide()
        self.dashboard.homePanel.Show()

        matchup = self.model.get_matchup(self.leagues[leagueId], gameId.split(".")[-1])
        
        self.awayController.new_team(leagueId, matchup.awayId, season)
        self.homeController.new_team(leagueId, matchup.homeId, season)

        self.dashboard.trackingPanel.ptsSpreadTrack.set_panel(self.model.get_tracking("pts_spread", matchup))
        self.dashboard.trackingPanel.totalTrack.set_panel(self.model.get_tracking("total", matchup))
        self.dashboard.Layout()
        
    