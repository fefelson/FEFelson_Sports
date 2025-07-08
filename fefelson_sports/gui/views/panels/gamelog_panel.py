import wx

from ..components.logo_component import LogoComponent



############################################################################
############################################################################


class GamePanel(wx.Panel):

    def __init__(self, parent, game=None):
        super().__init__(parent, size=(-1,60), style=wx.BORDER_SIMPLE)
        self.gameId = None

        self.isActive = wx.CheckBox(self, label="active", style=wx.ALIGN_RIGHT)
        self.isActive.SetValue(True)
        self.isActive.Hide()

        self.gameDate = wx.StaticText(self, label="Jun 06", size=(40,40))
        self.gameDate.SetFont(wx.Font(wx.FontInfo(9).Bold()))
        self.logo = LogoComponent(self, 22)
        self.values = {}
        
        self._set_layout()
        if game is not None:
            self._set_game(game)

        self.Layout()


    def _set_game(self, game):
        gameId = game["game_id"]
        self.SetName(gameId)
        self.isActive.SetName(gameId)

        self.logo.set_logo(game["league_id"], game["opp_id"])
        self.gameDate.SetLabel(game["game_date"].strftime("%b\n%d"))
        
        self.values["team_pts"].SetLabel(f"{game['team_pts']}")
        self.values["opp_pts"].SetLabel(f"{game['opp_pts']}")

        for index in ("pts_spread", "money_line", "over_under"):
            gameValue = "--"
            if game[index] is not None:
                gameValue = f"+{game[index]}" if game[index] > 0 else f"{game[index]}"
            self.values[index].SetLabel(gameValue)


        backColor = wx.WHITE if game["is_home"] == 1 else wx.Colour("KHAKI")
        moneyColor = wx.Colour("GREEN") if game["is_winner"] == 1 else wx.Colour("RED")
        spreadColor = wx.Colour("BLACK")
        ouColor = wx.Colour("BLACK")

        try:
            if game["is_cover"] > 0:
                spreadColor = wx.Colour("GREEN")
            elif game["is_cover"] < 0:
                spreadColor = wx.Colour("RED")
        except:
            spreadColor = wx.Colour("GREY")


        try:
            if game["is_over"] > 0:
                ouColor = wx.Colour("RED")
            elif game["is_over"] < 0:
                ouColor = wx.Colour("BLUE")
        except:
            ouColor = wx.Colour("GREY")

        
        self.SetBackgroundColour(backColor)

        self.values["pts_spread"].SetForegroundColour(spreadColor)
        self.values["money_line"].SetForegroundColour(moneyColor)
        self.values["over_under"].SetForegroundColour(ouColor)


    def _set_layout(self):

        ptsFont = wx.Font(wx.FontInfo(10).Bold())
        spreadFont = wx.Font(wx.FontInfo(12).Bold())

        for t_o in ("team", "opp"):
            self.values[f"{t_o}_pts"] = wx.StaticText(self, size=(30,40))
            self.values[f"{t_o}_pts"].SetFont(ptsFont)

        for index in ("pts_spread", "money_line", "over_under"):
            self.values[index] = wx.StaticText(self, size=(50,40))
            self.values[index].SetFont(spreadFont)
        

        self.sizer = wx.BoxSizer()
        self.sizer.Add(self.isActive, 0)
        self.sizer.Add(self.gameDate, 0, wx.CENTER | wx.LEFT | wx.RIGHT, 15)
        self.sizer.Add(self.values["team_pts"], 0,  wx.CENTER)
        self.sizer.Add(self.logo, 0, wx.CENTER | wx.RIGHT, 10)
        self.sizer.Add(self.values["opp_pts"], 0,  wx.CENTER | wx.RIGHT, 15)
        self.sizer.Add(self.values["pts_spread"], 0,  wx.CENTER | wx.RIGHT, 15)
        self.sizer.Add(self.values["money_line"], 0,  wx.CENTER | wx.RIGHT, 15)
        self.sizer.Add(self.values["over_under"], 0, wx.CENTER | wx.RIGHT, 15)
        self.SetSizer(self.sizer)



############################################################################
############################################################################



class GamelogPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent, style=wx.VSCROLL | wx.HSCROLL)

        self.scrollPanel = wx.ScrolledWindow(self)
        self.scrollPanel.SetScrollbars(20, 20, 50, 50)

        self.panels = {}
        self.scrollSizer = wx.BoxSizer(wx.VERTICAL)
        self.scrollPanel.SetSizer(self.scrollSizer)
                        
        # Main layout
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.scrollPanel, 1, wx.EXPAND)
        
        self.SetSizer(mainSizer)
        self.Layout()


    def set_display(self, filterDisplayed):
        for panel in self.panels.values():
            if filterDisplayed:
                panel.isActive.Show()
                panel.Show()
                panel.Layout()
            else:
                panel.isActive.Hide()
                if panel.isActive.GetValue():
                    panel.Show()
                else:
                    panel.Hide()
                panel.Layout()
        self.scrollPanel.Layout()


    def set_panel(self, gamelog, gameIds, gamelogCtrl):
        self.scrollPanel.DestroyChildren()
        self.panels = {}
        
        gamelog = gamelog.sort_values('game_date', ascending=False)
                
        for _, game in gamelog.iterrows():
            panel = GamePanel(self.scrollPanel, game)
            panel.isActive.Bind(wx.EVT_CHECKBOX, gamelogCtrl.on_checkbox)
            if game["game_id"] not in gameIds:
                panel.isActive.SetValue(False)
            self.scrollSizer.Add(panel, 0, wx.BOTTOM, 15)
            self.panels[game["game_id"]] = panel
        self.Layout()
        
        
    def set_selected_gameIds(self, gameIds):

        for panel in self.panels.values():
            if panel.GetName() in gameIds:
                panel.isActive.SetValue(True)
            else:
                panel.isActive.SetValue(False)
            panel.Layout()
        

    


    

        
    


    

   


