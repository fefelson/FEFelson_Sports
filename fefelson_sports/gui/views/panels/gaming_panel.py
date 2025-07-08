import wx 

from ..components.label_component import PctComponent, FloatComponent, IntComponent

class GamingPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)

        self.winPct = PctComponent(self, "Money Pct:")
        self.winROI = PctComponent(self, "Money ROI:")
        self.coverPct = PctComponent(self, "Cover Pct:")
        self.coverROI = PctComponent(self, "Cover ROI:")
        self.ouPct = PctComponent(self, "O/U Pct:")
        self.ouROI = PctComponent(self, "O/U ROI:")

        self.moneyLine = IntComponent(self, "Money Line")
        self.spread = FloatComponent(self, "Pts Spread")
        self.oU = FloatComponent(self, "O/U")

        self.result = FloatComponent(self, "Result")
        self.total = FloatComponent(self, "Total")

        self.ats = FloatComponent(self, "ATS")
        self.att = FloatComponent(self, "ATT")


        moneySizer = wx.BoxSizer(wx.VERTICAL)
        moneySizer.Add(self.winROI, 0, wx.EXPAND | wx.BOTTOM, 10)
        moneySizer.Add(self.winPct, 0, wx.EXPAND | wx.BOTTOM, 10)
        moneySizer.Add(self.moneyLine, 0, wx.EXPAND | wx.BOTTOM, 10)

        atsSizer = wx.BoxSizer(wx.VERTICAL)
        atsSizer.Add(self.coverROI, 0, wx.EXPAND | wx.BOTTOM, 10)
        atsSizer.Add(self.coverPct, 0, wx.EXPAND | wx.BOTTOM, 10)
        atsSizer.Add(self.spread, 0, wx.EXPAND | wx.BOTTOM, 10)
        atsSizer.Add(self.result, 0, wx.EXPAND | wx.BOTTOM, 10)
        atsSizer.Add(self.ats, 0, wx.EXPAND | wx.BOTTOM, 10)

        ouSizer = wx.BoxSizer(wx.VERTICAL)
        ouSizer.Add(self.ouROI, 0, wx.EXPAND | wx.BOTTOM, 10)
        ouSizer.Add(self.ouPct, 0, wx.EXPAND | wx.BOTTOM, 10)
        ouSizer.Add(self.oU, 0, wx.EXPAND | wx.BOTTOM, 10)
        ouSizer.Add(self.total, 0, wx.EXPAND | wx.BOTTOM, 10)
        ouSizer.Add(self.att, 0, wx.EXPAND | wx.BOTTOM, 10)

        sizer = wx.BoxSizer()
        sizer.Add(moneySizer, 1, wx.EXPAND | wx.RIGHT | wx.TOP, 20)
        sizer.Add(atsSizer, 1, wx.EXPAND| wx.RIGHT | wx.TOP, 20)
        sizer.Add(ouSizer, 1, wx.EXPAND| wx.RIGHT | wx.TOP, 20)

        self.SetSizer(sizer)