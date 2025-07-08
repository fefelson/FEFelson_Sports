import wx

from .basketball_team_stats_panel import BasketballTeamStatsPanel
from .gaming_panel import GamingPanel
from .gamelog_panel import GamelogPanel
from .title_panel import TitlePanel

from ....utils.color_helper import adjust_readability, hex_to_rgb


##############################################################################
##############################################################################



class TeamPanel(wx.ScrolledWindow):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, style=wx.HSCROLL)
        self.SetScrollbars(20, 20, 10, 10)
        self.SetMinSize((375,-1))
        self.titlePanel = TitlePanel(self)
        self.titlePanel.gp.SetBackgroundColour(wx.LIGHT_GREY)
        self.titlePanel.gp.value.Bind(wx.EVT_LEFT_DCLICK, self.on_gp)
       
        self.noteBookPanel = wx.Notebook(self)
        self.noteBookPanel.SetMinSize((-1,400))
        self.teamStatsPanel = BasketballTeamStatsPanel(self.noteBookPanel)
        self.noteBookPanel.AddPage(self.teamStatsPanel, "Team Stats")

        self.gamingPanel = GamingPanel(self.noteBookPanel)
        self.noteBookPanel.AddPage(self.gamingPanel, "Gaming")

        self.gamelogPanel = GamelogPanel(self.noteBookPanel)
        self.noteBookPanel.AddPage(self.gamelogPanel, "Gamelog")

        # self.playerStatsPanel = wx.Panel(self.noteBookPanel)
        # self.noteBookPanel.AddPage(self.playerStatsPanel, "Player Stats")
       

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.titlePanel, 1, wx.EXPAND)
        sizer.Add(self.noteBookPanel, 2, wx.EXPAND)


        self.SetSizer(sizer)


    def on_gp(self, event):
        if self.gamelogPanel.IsShown():
            self.gamelogPanel.Hide()
        else:
            self.gamelogPanel.Show()
        self.Layout()
        self.GetParent().Layout()



    def initialize_team(self, team):
        backgroundColor, foregroundColor = adjust_readability(hex_to_rgb(team['primary_color'].iloc[0]), hex_to_rgb(team['secondary_color'].iloc[0]))
        self.titlePanel.SetBackgroundColour(wx.Colour(backgroundColor))
        self.titlePanel.nameArea.firstName.SetForegroundColour(wx.Colour(foregroundColor))
        self.titlePanel.nameArea.lastName.SetForegroundColour(wx.Colour(foregroundColor))
        
        self.titlePanel.nameArea.firstName.SetLabel(team["first_name"].iloc[0])
        self.titlePanel.nameArea.lastName.SetLabel(team["last_name"].iloc[0])
        self.titlePanel.nameArea.logo.set_logo(team["league_id"].iloc[0], team["team_id"].iloc[0])
        self.titlePanel.Layout()
        

    def update_gaming_stats(self, gamingStats, analytics):

        from pprint import pprint 
        pprint(gamingStats)
        
        self.gamingPanel.moneyLine.set_panel(gamingStats["money_line"], analytics.loc[analytics["metric_name"] == "team_money_line"].squeeze())
        self.gamingPanel.winPct.set_panel(gamingStats["win_pct"], analytics.loc[analytics["metric_name"] == "win_pct"].squeeze())
        self.gamingPanel.coverPct.set_panel(gamingStats["cover_pct"], analytics.loc[analytics["metric_name"] == "cover_pct"].squeeze())
        self.gamingPanel.winROI.set_panel(gamingStats["money_roi"], analytics.loc[analytics["metric_name"] == "team_money_roi"].squeeze())
        self.gamingPanel.coverROI.set_panel(gamingStats["cover_roi"], analytics.loc[analytics["metric_name"] == "team_spread_roi"].squeeze())

        if gamingStats["under_pct"] > gamingStats["over_pct"]:
            self.gamingPanel.ouPct.set_panel(gamingStats["under_pct"], analytics.loc[analytics["metric_name"] == "under_pct"].squeeze(), label="UNDER%")
            self.gamingPanel.ouROI.set_panel(gamingStats["under_roi"], analytics.loc[analytics["metric_name"] == "team_under_roi"].squeeze(), label="UNDER ROI")

        else:
            self.gamingPanel.ouPct.set_panel(gamingStats["over_pct"], analytics.loc[analytics["metric_name"] == "over_pct"].squeeze(), label="OVER%")
            self.gamingPanel.ouROI.set_panel(gamingStats["over_roi"], analytics.loc[analytics["metric_name"] == "team_over_roi"].squeeze(), label="OVER ROI")
        
        self.gamingPanel.spread.set_panel(gamingStats["pts_spread"], analytics.loc[analytics["metric_name"] == "team_spread"].squeeze())
        self.gamingPanel.result.set_panel(gamingStats["result"], analytics.loc[analytics["metric_name"] == "team_result"].squeeze())
        self.gamingPanel.ats.set_panel(gamingStats["ats"], analytics.loc[analytics["metric_name"] == "team_ats"].squeeze())
        
        self.gamingPanel.oU.set_panel(gamingStats["over_under"], analytics.loc[analytics["metric_name"] == "team_over_under"].squeeze())
        self.gamingPanel.total.set_panel(gamingStats["total"], analytics.loc[analytics["metric_name"] == "team_total"].squeeze())
        self.gamingPanel.att.set_panel(gamingStats["att"], analytics.loc[analytics["metric_name"] == "team_att"].squeeze())

        self.gamingPanel.Layout()

                
    def update_team_stats(self, teamStats, analytics):
        self.titlePanel.gp.set_panel(teamStats["gp"])
        
        self.teamStatsPanel.teamPts.set_panel_value("offense", teamStats["team_pts"], analytics.loc[analytics["metric_name"] == "off_pts"].squeeze())
        self.teamStatsPanel.teamPts.set_panel_value("defense", teamStats["opp_pts"], analytics.loc[analytics["metric_name"] == "def_pts"].squeeze())
        
        self.teamStatsPanel.teamFG.set_panel_value("offense", teamStats["team_fga"], analytics.loc[analytics["metric_name"] == "off_fga"].squeeze(), teamStats["team_fgpct"], analytics.loc[analytics["metric_name"] == "off_fgm_per_fga"].squeeze())
        self.teamStatsPanel.teamFG.set_panel_value("defense", teamStats["opp_fga"], analytics.loc[analytics["metric_name"] == "def_fga"].squeeze(), teamStats["opp_fgpct"], analytics.loc[analytics["metric_name"] == "def_fgm_per_fga"].squeeze())
        
        self.teamStatsPanel.teamFT.set_panel_value("offense", teamStats["team_fta"], analytics.loc[analytics["metric_name"] == "off_fta"].squeeze(), teamStats["team_ftpct"], analytics.loc[analytics["metric_name"] == "off_ftm_per_fta"].squeeze())
        self.teamStatsPanel.teamFT.set_panel_value("defense", teamStats["opp_fta"], analytics.loc[analytics["metric_name"] == "def_fta"].squeeze(), teamStats["opp_ftpct"], analytics.loc[analytics["metric_name"] == "def_ftm_per_fta"].squeeze())
        
        self.teamStatsPanel.teamTP.set_panel_value("offense", teamStats["team_tpa"], analytics.loc[analytics["metric_name"] == "off_tpa"].squeeze(), teamStats["team_tppct"], analytics.loc[analytics["metric_name"] == "off_tpm_per_tpa"].squeeze())
        self.teamStatsPanel.teamTP.set_panel_value("defense", teamStats["opp_tpa"], analytics.loc[analytics["metric_name"] == "def_tpa"].squeeze(), teamStats["opp_tppct"], analytics.loc[analytics["metric_name"] == "def_tpm_per_tpa"].squeeze())
        
        self.teamStatsPanel.teamTurn.set_panel_value("offense", teamStats["team_turn"], analytics.loc[analytics["metric_name"] == "off_turnovers_per_possessions"].squeeze())
        self.teamStatsPanel.teamTurn.set_panel_value("defense", teamStats["opp_turn"], analytics.loc[analytics["metric_name"] == "def_turnovers_per_possessions"].squeeze())
        
        self.teamStatsPanel.teamReb.set_panel_value("offense", teamStats["oreb_pct"], analytics.loc[analytics["metric_name"] == "oreb_pct"].squeeze())
        self.teamStatsPanel.teamReb.set_panel_value("defense", teamStats["dreb_pct"], analytics.loc[analytics["metric_name"] == "dreb_pct"].squeeze())
        
        self.teamStatsPanel.teamAst.set_panel_value("offense", teamStats["team_ast"], analytics.loc[analytics["metric_name"] == "off_ast_per_fgm"].squeeze())
        self.teamStatsPanel.teamAst.set_panel_value("defense", teamStats["opp_ast"], analytics.loc[analytics["metric_name"] == "def_ast_per_fgm"].squeeze())


        self.titlePanel.pace.set_panel(teamStats["pace"], analytics.loc[analytics["metric_name"] == "off_possessions"].squeeze())
        self.titlePanel.overall.set_panel(teamStats["net_rating"], analytics.loc[analytics["metric_name"] == "net_rating"].squeeze())
        self.titlePanel.offEff.set_panel(teamStats["off_eff"], analytics.loc[analytics["metric_name"] == "off_eff"].squeeze())
        self.titlePanel.defEff.set_panel(teamStats["def_eff"], analytics.loc[analytics["metric_name"] == "def_eff"].squeeze())

        self.teamStatsPanel.Layout()
        self.titlePanel.Layout()


if __name__ == "__main__":

    app = wx.App()
    frame = wx.Frame(None)
    panel = TeamPanel(frame)
    sizer = wx.BoxSizer()
    sizer.Add(panel)
    frame.SetSizer(sizer)
    frame.Show()
    app.MainLoop()
        


