import wx

from ..visualizations.charts import ATSChart, SpreadChart, WinLossChart

class ChartPanel(wx.ScrolledWindow):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, style=wx.VSCROLL | wx.HSCROLL, *args, **kwargs)
        self.SetMinSize((500, -1))
        self.SetScrollbars(20, 20, 10, 10)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.atsChart = ATSChart(self)
        self.ptsSpreadChart = SpreadChart(self)
        self.winLossChart = WinLossChart(self)

        self.sizer.Add(self.ptsSpreadChart.canvas, 0, wx.BOTTOM, 20)
        self.sizer.Add(self.winLossChart.canvas, 0, wx.BOTTOM, 20)
        self.sizer.Add(self.atsChart.canvas, 0)
        self.SetSizer(self.sizer)
        


