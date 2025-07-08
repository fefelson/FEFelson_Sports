import wx

from ..components.opposite_chart_component import OppositeChart
from ..components.opposite_shot_component import OppositeShot

class BasketballTeamStatsPanel(wx.ScrolledWindow):


    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, style=wx.VSCROLL, *args, **kwargs)
        self.SetScrollbars(20, 20, 10, 10)


        teamFont = wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString)

        self.teamLabel = wx.StaticText(self, label="Offense", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.teamLabel.SetFont(teamFont)
        
        self.oppLabel = wx.StaticText(self, label="Defense", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.oppLabel.SetFont(teamFont)

        self.teamPts = OppositeChart(self, "Points")
        self.teamFG = OppositeShot(self, "Field Goals")
        self.teamFT = OppositeShot(self, "Free Throws")
        self.teamTP = OppositeShot(self, "Three Points")
        self.teamTurn = OppositeChart(self, "Turnovers")
        self.teamReb = OppositeChart(self, "Rebounds")
        self.teamAst = OppositeChart(self, "Assists")
        
        
        nameSizer = wx.BoxSizer()
        nameSizer.Add(self.oppLabel, 1, wx.EXPAND)
        nameSizer.Add(wx.StaticLine(self, size=(-1,15)), 1, wx.EXPAND)
        nameSizer.Add(self.teamLabel, 1, wx.EXPAND)


        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(nameSizer, 0, wx.EXPAND)
        sizer.Add(self.teamPts, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 15)
        sizer.Add(self.teamFG, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 15)
        sizer.Add(self.teamFT, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 15)
        sizer.Add(self.teamTP, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 15)
        sizer.Add(self.teamTurn, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 15)
        sizer.Add(self.teamReb, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 15)
        sizer.Add(self.teamAst, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 15)

        self.SetSizer(sizer)        




    def set_panel(self, team):
        pass