import wx


class TeamsCompareView(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.listPanel = wx.Panel(self)
        self.listPanel.SetBackgroundColour(wx.Colour("red"))
        self.searchCtrl = wx.TextCtrl(self.listPanel)
        self.searchCtrl.SetMaxSize((250, -1))
        self.teamList = wx.ListCtrl(self.listPanel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.teamList.InsertColumn(0, "Teams", width=250 - 10)
        self.teamList.SetMaxSize((250, -1))

        listSizer = wx.BoxSizer(wx.VERTICAL)
        listSizer.Add(self.searchCtrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        listSizer.Add(self.teamList, 6, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.listPanel.SetSizer(listSizer)


        self.displayPanel = wx.ScrolledWindow(self)
        self.displayPanel.SetBackgroundColour(wx.Colour("green"))
        self.displayPanel.SetScrollbars(20, 0, 50, 0)
        self.displayPanel.SetMinSize((400, -1))
        self.displaySizer = wx.BoxSizer(wx.HORIZONTAL)
        self.displayPanel.SetSizer(self.displaySizer)


        boxSizer = wx.BoxSizer(wx.HORIZONTAL)
        boxSizer.Add(self.listPanel, 1, wx.EXPAND | wx.ALL , 10)
        boxSizer.Add(self.displayPanel, 5, wx.EXPAND | wx.ALL , 10)

        self.SetSizer(boxSizer)


    def update_team_list(self, teams):
        self.teamList.ClearAll()
        self.teamList.InsertColumn(0, "Teams", width=self.teamList.GetSize()[0] - 10)
        for i, team in enumerate(teams):
            self.teamList.InsertItem(i, team)



logoPath = "/home/ededub/FEFelson/{}/logos/{}.png"

class TeamPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, size=(350,-1), *args, **kwargs)

        
        self.SetBackgroundColour(wx.Colour("BLUE"))
        




