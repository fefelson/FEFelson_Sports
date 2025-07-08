import wx

 
class FilterPanel(wx.ScrolledWindow):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, size=(-1, 200), style=wx.VSCROLL | wx.HSCROLL, *args, **kwargs)
        self.SetScrollbars(20, 20, 50, 50)

        self.hA = wx.RadioBox(self, label="home/away", choices=("all", "away", "home"), name="is_home")
        self.wL = wx.RadioBox(self, label="win/loss", choices=("all", "winner", "loser"), name="is_winner")
        self.fav = wx.RadioBox(self, label="favorites", choices=("all", "favorite", "underdog"), name="is_favorite")
        self.ats = wx.RadioBox(self, label="covers", choices=("all", "cover", "loser"), name="is_cover")
        self.over = wx.RadioBox(self, label="o/u", choices=("all", "over", "under"), name="is_over")
        self.timeframe = wx.RadioBox(self, label="time frame", choices=("season", "2Months", "1Month", "2Weeks"))

        # self.vs = wx.Button(self, label="VS")
        self.all = wx.Button(self, label="ALL")
        self.clear = wx.Button(self, label="CLR")

        buttonSizer = wx.BoxSizer()
        buttonSizer.Add(self.all)
        buttonSizer.Add(self.clear)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        optionsSizer = wx.BoxSizer()
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        rightSizer = wx.BoxSizer(wx.VERTICAL)

        leftSizer.Add(self.timeframe, 0, wx.ALL, 5)
        leftSizer.Add(self.hA, 0, wx.ALL, 5)
        leftSizer.Add(self.wL, 0, wx.ALL, 5)

        rightSizer.Add(self.fav, 0, wx.ALL, 5)
        rightSizer.Add(self.ats, 0, wx.ALL, 5)
        rightSizer.Add(self.over, 0, wx.ALL, 5)

        optionsSizer.Add(leftSizer)
        optionsSizer.Add(rightSizer)

        mainSizer.Add(optionsSizer)
        mainSizer.Add(buttonSizer)

        self.SetSizer(mainSizer)


    def bind_to_ctrl(self, ctrl):
        # Bind events
        self.hA.Bind(wx.EVT_RADIOBOX, ctrl.apply_filters)
        self.wL.Bind(wx.EVT_RADIOBOX, ctrl.apply_filters)
        self.fav.Bind(wx.EVT_RADIOBOX, ctrl.apply_filters)
        self.ats.Bind(wx.EVT_RADIOBOX, ctrl.apply_filters)
        self.over.Bind(wx.EVT_RADIOBOX, ctrl.apply_filters)
        self.timeframe.Bind(wx.EVT_RADIOBOX, ctrl.apply_filters)
        self.clear.Bind(wx.EVT_BUTTON, ctrl.clear_selection)
        self.all.Bind(wx.EVT_BUTTON, ctrl.select_all)


    def set_default(self, defaults):
        self.hA.SetSelection(self.hA.FindString(defaults["is_home"]))
        self.wL.SetSelection(self.wL.FindString(defaults["is_winner"]))
        self.fav.SetSelection(self.fav.FindString(defaults["is_favorite"]))
        self.ats.SetSelection(self.ats.FindString(defaults["is_cover"]))
        self.over.SetSelection(self.over.FindString(defaults["is_over"]))
        self.timeframe.SetSelection(self.timeframe.FindString(defaults["timeframe"]))


class FilterFrame(wx.Frame):

    def __init__(self, parent, closeHandler):
        super().__init__(parent, style=wx.FRAME_FLOAT_ON_PARENT | wx.DEFAULT_FRAME_STYLE, title="Edit Games")

        self.filterPanel = FilterPanel(self)
        sizer = wx.BoxSizer()
        sizer.Add(self.filterPanel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Bind(wx.EVT_CLOSE, closeHandler)


if __name__ == "__main__":

    app = wx.App()
    frame = FilterFrame(None)
    frame.Show()
    app.MainLoop()