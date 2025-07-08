

#################################################################
#################################################################



class TickerController:

    def __init__(self, tickerPanel, parentCtrl=None):
        self.tickerPanel = tickerPanel 
        self.parentCtrl = parentCtrl


    def set_ticker_panel(self, matchups):
        self.tickerPanel.clear()
        for matchup in matchups:
            thumbPanel = self.tickerPanel.add_matchup(matchup)
            thumbPanel.bind_to_controller(self)  


    def on_spread(self, event):
        obj = event.GetEventObject()
        ptsSpread, leagueId, gameId = obj.GetName().split()


    def on_team(self, event):
        obj = event.GetEventObject()
        teamId, leagueId, gameId = obj.GetName().split()

        if self.parentCtrl:
            self.parentCtrl.on_team(teamId, leagueId, gameId)


    def on_total(self, event):
        obj = event.GetEventObject()
        oU, leagueId, gameId = obj.GetName().split()


    def on_money(self, event):
        obj = event.GetEventObject()
        moneyLine, leagueId, gameId = obj.GetName().split()


    def on_click(self, event):
        obj = event.GetEventObject()
        leagueId, gameId = obj.GetName().split()

        if self.parentCtrl:
            self.parentCtrl.on_click(leagueId, gameId)

             