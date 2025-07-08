import os
import wx

from ..components.name_area import NameArea
from ..components.label_component import IntComponent, LabelComponent, OverallComponent, PaceComponent



module_dir = os.path.dirname(os.path.abspath(__file__))


class TitlePanel(wx.Panel):

    def __init__(self, parent, ctrl=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.SetBackgroundColour(wx.Colour("khaki"))

        self.nameArea = NameArea(self, 275)
        self.overall = OverallComponent(self)
        self.offEff = IntComponent(self, "OFF")
        self.defEff = IntComponent(self, "DEF")
        self.pace = PaceComponent(self)
        # self.gamblingPct = GamblingPctArea(self)
        self.gp = LabelComponent(self, "GP")

        effSizer = wx.BoxSizer()
        effSizer.Add(self.defEff, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        effSizer.Add(self.offEff, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        leftSizer = wx.BoxSizer(wx.VERTICAL)
        leftSizer.Add(self.overall, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        leftSizer.Add(effSizer, 0, wx.EXPAND)

        bottomSizer = wx.BoxSizer()
        bottomSizer.Add(self.pace, 5, wx.CENTER | wx.RIGHT, 10)
        bottomSizer.Add(self.gp, 1, wx.EXPAND)

        rightSizer = wx.BoxSizer(wx.VERTICAL)
        rightSizer.Add(self.nameArea)
        rightSizer.Add(bottomSizer)

        sizer = wx.BoxSizer()
        sizer.Add(leftSizer, 0, wx.EXPAND)
        sizer.Add(rightSizer, 0, wx.EXPAND)        
        self.SetSizer(sizer)




if __name__ == "__main__":

    app = wx.App()
    frame = wx.Frame(None)
    panel = TitlePanel(frame)
    sizer = wx.BoxSizer()
    sizer.Add(panel)
    frame.SetSizer(sizer)
    frame.Show()
    app.MainLoop()
        

        





