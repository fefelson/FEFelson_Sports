from datetime import datetime 
import wx

from ..components.logo_component import LogoComponent



#############################################################################
#############################################################################


spacetime_funnel_cake = wx.Colour(245, 245, 220)


#############################################################################
#############################################################################



class ThumbPanel(wx.Panel):
    def __init__(self, parent, matchup=None):
        wx.Panel.__init__(self, parent, size=wx.Size(170, 180), style=wx.BORDER_SIMPLE)
        self.SetMaxSize(wx.Size(170, 180))

        # Team data containers
        self.logos = {}
        self.abrvs = {}
        self.moneyLines = {}
        self.spreadLines = {}
        self.overLines = {}

        self._set_widgets()
        self._set_layout()
        
        if matchup:
            self.set_panel(matchup)

        self.Fit()
        self.Layout()


    def _set_widgets(self):
        # Font definitions
        gdFont = wx.Font(7, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString)
        gtFont = wx.Font(9, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString)
        moneyFont = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString)
        lineFont = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString)
        teamFont = wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString)

        # Game info
        self.gameDate = wx.StaticText(self, label="gamedate", size=wx.Size(90, 15), style=wx.ALIGN_CENTER_HORIZONTAL)
        self.gameDate.SetFont(gdFont)
        
        self.gameTime = wx.StaticText(self, label="gametime", size=wx.Size(90, 15), style=wx.ALIGN_CENTER_HORIZONTAL)
        self.gameTime.SetFont(gtFont)

        # Spread and Over/Under
        self.ptsSpread = wx.StaticText(self, label="-pts-", size=wx.Size(45, 15), style=wx.ALIGN_CENTER_HORIZONTAL)
        self.ptsSpread.SetFont(moneyFont)
        self.overUnder = wx.StaticText(self, label="-o/u-", size=wx.Size(45, 15), style=wx.ALIGN_CENTER_HORIZONTAL)
        self.overUnder.SetFont(moneyFont)

        # Initialize team widgets
        for a_h in ("away", "home"):
            self.logos[a_h] = LogoComponent(self, 45)
            self.abrvs[a_h] = wx.StaticText(self, wx.ID_ANY, label=a_h.upper(), size=wx.Size(45, 20), style=wx.ALIGN_CENTER_HORIZONTAL | wx.ST_ELLIPSIZE_END)
            self.abrvs[a_h].SetFont(teamFont)
            self.moneyLines[a_h] = wx.StaticText(self, wx.ID_ANY, label="-110", size=wx.Size(45, 15), style=wx.ALIGN_CENTER_HORIZONTAL)
            self.moneyLines[a_h].SetFont(moneyFont)
            self.spreadLines[a_h] = wx.StaticText(self, wx.ID_ANY, label="-110", size=wx.Size(45, 15), style=wx.ALIGN_CENTER_HORIZONTAL)
            self.spreadLines[a_h].SetFont(lineFont)


    def _set_layout(self):
        # GridBagSizer layout
        grid_sizer = wx.GridBagSizer(hgap=5, vgap=2)  # Reduced vgap for tighter spacing

        # Row 0-1: Game info (spans all columns)
        grid_sizer.Add(self.gameDate, pos=(0, 0), span=(1, 3), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=5)
        grid_sizer.Add(self.gameTime, pos=(1, 0), span=(1, 3), flag=wx.ALIGN_CENTER_HORIZONTAL, border=5)

        # Row 2-7: Team sections and middle column
        # Away team (Column 0)
        grid_sizer.Add(self.abrvs["away"], pos=(2, 0), flag=wx.ALIGN_CENTER_HORIZONTAL, border=5)
        grid_sizer.Add(self.logos["away"], pos=(3, 0), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=5)
        grid_sizer.Add(self.moneyLines["away"], pos=(4, 0), flag=wx.ALIGN_CENTER_HORIZONTAL, border=5)
        grid_sizer.Add(self.spreadLines["away"], pos=(5, 0), flag=wx.ALIGN_CENTER_HORIZONTAL, border=5)

        # Middle column (Column 1) - Spread and Over/Under
        grid_sizer.Add((0, 20), pos=(2, 1))  # Spacer to align with abrvs
        # grid_sizer.Add((0, 45), pos=(3, 1))  # Spacer to align with logos
        grid_sizer.Add((0, 20), pos=(4, 1))  # Spacer to align with money lines
        grid_sizer.Add(self.ptsSpread, pos=(5, 1), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND, border=5)
        grid_sizer.Add(self.overUnder, pos=(6, 1), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND, border=5)

        # Home team (Column 2)
        grid_sizer.Add(self.abrvs["home"], pos=(2, 2), flag=wx.ALIGN_CENTER_HORIZONTAL, border=5)
        grid_sizer.Add(self.logos["home"], pos=(3, 2), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=5)
        grid_sizer.Add(self.moneyLines["home"], pos=(4, 2), flag=wx.ALIGN_CENTER_HORIZONTAL, border=5)
        grid_sizer.Add(self.spreadLines["home"], pos=(5, 2), flag=wx.ALIGN_CENTER_HORIZONTAL, border=5)
        
        # Set the sizer and layout
        self.SetSizer(grid_sizer)


    def bind_to_controller(self, ctrl):
        self.Bind(wx.EVT_LEFT_DCLICK, ctrl.on_click)
        self.ptsSpread.Bind(wx.EVT_LEFT_DCLICK, ctrl.on_spread)
        self.overUnder.Bind(wx.EVT_LEFT_DCLICK, ctrl.on_total)
        [self.moneyLines[a_h].Bind(wx.EVT_LEFT_DCLICK, ctrl.on_money) for a_h in ("away", "home")]
            
        for item in (self.abrvs["home"], self.abrvs["away"], self.logos["home"].logo, self.logos["away"].logo):
            item.Bind(wx.EVT_LEFT_DCLICK, ctrl.on_team)

        for item in (self.gameDate, self.gameTime):
            item.Bind(wx.EVT_LEFT_DCLICK, ctrl.on_click)


    def _set_pts_spread(self, matchupOdds):
        item = "--"
        for i in range(len(matchupOdds)):
            for a_h in ("home", "away"):
                odds = matchupOdds[(i+1)*-1].get(f"{a_h}_spread", None)
                if odds:
                    if float(odds) > 0:
                        item = f"+{odds}"
                    else:
                        item = odds
                    return item
        return item



    def set_panel(self, matchup):
        
        leagueId = matchup.leagueId
        gameId = matchup.gameId
        gamedate = datetime.fromisoformat(matchup.gameTime)
        ptsSpread = self._set_pts_spread(matchup.odds)
        oU = "--"
        for i in range(len(matchup.odds)):
            if matchup.odds[(i+1)*-1].get("total", '') != '':
                oU = matchup.odds[(i+1)*-1]["total"]
                break
        
        
        self.gameDate.SetLabel(gamedate.strftime("%a %b %d"))
        self.gameTime.SetLabel(gamedate.strftime("%I:%M %p"))
        self.ptsSpread.SetLabel(ptsSpread)
        self.overUnder.SetLabel(f"{oU}")

        self.SetName(f"{leagueId} {gameId}") # Name of panel is set to gameId for event handling
        self.gameDate.SetName(f"{leagueId} {gameId}") 
        self.gameTime.SetName(f"{leagueId} {gameId}") 
        self.ptsSpread.SetName(f"{ptsSpread} {leagueId} {gameId}")
        self.overUnder.SetName(f"{oU} {leagueId} {gameId}")


        for a_h in ("away", "home"):
            index = a_h == "home"
            team = matchup.teams[index]
            teamId = team["team_id"]

            mL = "--"
            for i in range(len(matchup.odds)):
                if matchup.odds[(i+1)*-1].get(f"{a_h}_ml", '') != '':
                    temp = matchup.odds[(i+1)*-1][f"{a_h}_ml"]
                    if int(temp) > 0:
                        mL = f"+{temp}"
                    else:
                        mL = temp
                    break

            sL = "--"
            for i in range(len(matchup.odds)):
                if matchup.odds[(i+1)*-1].get(f"{a_h}_line", '') != '':
                    temp = matchup.odds[(i+1)*-1][f"{a_h}_line"]
                    if int(temp) > 0:
                        sL = f"+{temp}"
                    else:
                        sL = temp
                    break
            
            self.abrvs[a_h].SetLabel(team["abbr"])
            self.logos[a_h].set_logo(leagueId, teamId)
            self.moneyLines[a_h].SetLabel(mL)
            self.spreadLines[a_h].SetLabel(sL)

            self.abrvs[a_h].SetName(f"{teamId} {leagueId} {gameId}")
            self.logos[a_h].logo.SetName(f"{teamId} {leagueId} {gameId}")
            self.moneyLines[a_h].SetName(f"{mL} {leagueId} {gameId}")
           
        if leagueId != "MLB":
            for a_h in ("away", "home"):
                self.spreadLines[a_h].Hide()



########################################################################
########################################################################



class TickerPanel(wx.Panel):
    def __init__(self, parent, size=(185, -1)):
        super().__init__(parent, size=size, style=wx.VSCROLL)
        
        self.scrollPanel = wx.ScrolledWindow(self)
        self.scrollPanel.SetScrollbars(20, 20, 10, 10)
        self.scrollSizer = wx.BoxSizer(wx.VERTICAL)
        self.scrollPanel.SetSizer(self.scrollSizer)

        sizer = wx.BoxSizer()
        sizer.Add(self.scrollPanel, 1, wx.EXPAND)
        self.SetSizer(sizer)


    def add_matchup(self, matchup):
        thumbPanel = ThumbPanel(self.scrollPanel, matchup)
        thumbPanel.SetBackgroundColour(spacetime_funnel_cake)
        self.scrollSizer.Add(thumbPanel, 0, wx.BOTTOM, 10)
        return thumbPanel


    def clear(self):
        self.scrollPanel.DestroyChildren()