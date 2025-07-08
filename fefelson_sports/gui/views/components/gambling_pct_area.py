import wx

from .label_component import PctComponent


class GamblingPctArea(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.SetMaxSize((200,200))

        self.winPct = PctComponent(self, "Money Pct:")
        self.winROI = PctComponent(self, "ROI:")
        self.coverPct = PctComponent(self, "Cover Pct:")
        self.coverROI = PctComponent(self, "ROI:")
        self.ouPct = PctComponent(self, "O/U Pct:")
        self.ouROI = PctComponent(self, "ROI:")


        winSizer = wx.BoxSizer()
        winSizer.Add(self.winPct, 1, wx.RIGHT, 10)
        winSizer.Add(self.winROI, 1)

        coverSizer = wx.BoxSizer()
        coverSizer.Add(self.coverPct, 1, wx.RIGHT, 10)
        coverSizer.Add(self.coverROI, 1)

        overSizer = wx.BoxSizer()
        overSizer.Add(self.ouPct, 1, wx.RIGHT, 10)
        overSizer.Add(self.ouROI, 1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(winSizer, 0, wx.EXPAND | wx.BOTTOM, 10)
        sizer.Add(coverSizer, 0, wx.EXPAND | wx.BOTTOM, 20)
        sizer.Add(overSizer, 0, wx.EXPAND)
        self.SetSizer(sizer)

        


if __name__ == "__main__":

    app = wx.App()
    frame = wx.Frame(None)
    panel = GamblingPctArea(frame)
    sizer = wx.BoxSizer()
    sizer.Add(panel, 1, wx.ALL, 0)
    frame.SetSizer(sizer)
    frame.Show()
    app.MainLoop()