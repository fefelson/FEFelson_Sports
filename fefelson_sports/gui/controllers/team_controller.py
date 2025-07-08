from .gamelog_controller import GamelogController

from ..stores.analytic_store import AnalyticStore
from ..stores.team_store import TeamStore

from ...analytics import get_stats_calculator


################################################################################
################################################################################


class TeamController:

    def __init__(self, teamPanel):
        
        self.leagueId = None 
        self.teamId = None 
        self.season = None 

        self.teamPanel = teamPanel
                
        # Initialize controllers
        self.gamelogCtrl = GamelogController(self, self.teamPanel.gamelogPanel)

        # Bind gp component to toggle filter frame
        self.teamPanel.titlePanel.gp.bind_to_ctrl(self.gamelogCtrl.filterCtrl.toggle_filter_frame) 


    def get_team(self):
        return TeamStore.get_team(self.leagueId, self.teamId)
    

    def get_gaming(self):
        selectedGameIds = self.gamelogCtrl.get_selectedIds()
        teamGaming = TeamStore.get_team_gaming(self.leagueId, self.teamId, self.season)
        focusedGaming = teamGaming[teamGaming['game_id'].isin(selectedGameIds)]
        return focusedGaming





    def new_team(self, leagueId, teamId, season):
        #TODO: Make Modular HERE

        ########################

        self.leagueId = leagueId 
        self.teamId = teamId
        self.season = season 

        self.gamelogCtrl.new_team(leagueId, teamId, season)
        
        self.teamPanel.initialize_team(TeamStore.get_team(leagueId, teamId))
        self.redisplay_team_panel()
                    

    def redisplay_team_panel(self):

        statsCalculator = get_stats_calculator(self.leagueId)
        teamStats = TeamStore.get_team_stats(self.leagueId, self.teamId, self.season)
        teamGaming = TeamStore.get_team_gaming(self.leagueId, self.teamId, self.season)

        timeframe = self.gamelogCtrl.get_timeframe()
        selectedGameIds = self.gamelogCtrl.get_selectedIds()

        focusedAnalytics = AnalyticStore.get_stat_metrics(self.leagueId, timeframe)
        focusedGaming = teamGaming[teamGaming['game_id'].isin(selectedGameIds)]
        focusedStats = teamStats[teamStats['game_id'].isin(selectedGameIds)]

        calculatedGaming = statsCalculator.calculate_gaming_stats(focusedGaming)
        calculatedTeamStats = statsCalculator.calculate_team_stats(focusedStats)

        self.teamPanel.update_gaming_stats(calculatedGaming, focusedAnalytics)
        self.teamPanel.update_team_stats(calculatedTeamStats, focusedAnalytics)
        self.teamPanel.Layout()


    def on_gp(self, event):
        self.gamelogCtrl.filterCtrl.toggle_filter_frame()





