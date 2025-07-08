import wx

from ..panels.chart_panel import ChartPanel
from ..panels.team_panel import TeamPanel
from ..panels.ticker_panel import TickerPanel
from ..panels.tracking_panel import TrackingPanel


emerald_fog = wx.Colour(50, 168, 82)         # #32A852
# A soft, beige-cream, like funnel cake dusted with powdered sugar in a spacetime distortion.

rune_rose = wx.Colour(188, 143, 143)
dark_matter_haunted_house = wx.Colour(47, 79, 79)  # #2F4F4F
# A dark, slate teal, as mysterious as dark matter lurking in a haunted house.



class MatchupDashboard(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.SetBackgroundColour(dark_matter_haunted_house)


        self.tickerPanel = TickerPanel(self)
        self.tickerPanel.SetBackgroundColour(dark_matter_haunted_house)
        
        # self.matchupPanel = MatchupPanel(self)
        # self.matchupPanel.SetBackgroundColour(emerald_fog)

        self.awayPanel = TeamPanel(self)
        self.awayPanel.SetBackgroundColour(rune_rose)
        
        self.homePanel = TeamPanel(self)
        self.homePanel.SetBackgroundColour(rune_rose)
        
        self.trackingPanel = TrackingPanel(self)

        self.chartPanel = ChartPanel(self)
        self.chartPanel.Hide()
        
        teamSizer = wx.BoxSizer()
        teamSizer.Add(self.awayPanel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        teamSizer.Add(self.homePanel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        teamSizer.Add(self.chartPanel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        bodySizer = wx.BoxSizer(wx.VERTICAL)
        bodySizer.Add(self.trackingPanel, 0, wx.EXPAND | wx.ALL, 10 )
        bodySizer.Add(teamSizer, 1, wx.EXPAND)

        sizer = wx.BoxSizer()
        sizer.Add(self.tickerPanel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        sizer.Add(bodySizer, 1, wx.EXPAND)
        
        self.SetSizer(sizer)


    

        


        

