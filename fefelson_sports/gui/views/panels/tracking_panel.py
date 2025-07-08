import wx

from ..visualizations.charts import ATSChart, SpreadChart, TrackLine, WinLossChart

class TrackingPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, style=wx.VSCROLL | wx.HSCROLL, *args, **kwargs)
        self.SetMaxSize((600,-1))


        self.choice = wx.Choice(self, choices=["pts spread", "total"])
        self.choice.Bind(wx.EVT_CHOICE, self.on_choice)
        self.ptsSpreadTrack = TrackLine(self)
        self.totalTrack = TrackLine(self)
        
        sizer = wx.BoxSizer()
        sizer.Add(self.choice, 0, wx.RIGHT | 10)
        sizer.Add(self.ptsSpreadTrack.canvas, 1, wx.EXPAND)
        sizer.Add(self.totalTrack.canvas, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.totalTrack.canvas.Hide()


    def on_choice(self, evt):
        if self.choice.GetString(self.choice.GetSelection()) == "pts spread":
            self.ptsSpreadTrack.canvas.Show()
            self.totalTrack.canvas.Hide()
        else:
            self.ptsSpreadTrack.canvas.Hide()
            self.totalTrack.canvas.Show()
        self.Layout()
        


