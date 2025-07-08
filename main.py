import wx
from .gui.views.felson_frame import FelsonFrame
from .gui.controllers.matchup_controller import MatchupController
from .gui.views.splash_screen import SplashScreen

from .sports.basketball.leagues import NBA, NCAAB

class MainApp(wx.App):
    def OnInit(self):

        leagueList = (NBA(), NCAAB())

        leagues = {league._leagueId: league for league in leagueList if league.is_active()}
        
        self.frame = FelsonFrame()
        self.matchupController = MatchupController(self.frame, leagues)
        self.matchupController.set_gamedate(None)
        
        # self.frame.Show() # remove to use splash screen
        splash = SplashScreen(self.frame)
        splash.Show()

        # self.compareTeamsController = CompareTeamsController(self.frame)
        return True
    
    

if __name__ == "__main__":
    noLog = wx.LogNull()
    app = MainApp()
    app.MainLoop()