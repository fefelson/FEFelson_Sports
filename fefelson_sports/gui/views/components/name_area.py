import wx

from .logo_component import LogoComponent


class NameArea(wx.Panel):
    default = 420
    def __init__(self, parent, x_size=default):
        super().__init__(parent, size=(x_size, -1))
        self.SetMaxSize((self.default,-1))

        fontSize = int(22*(x_size/self.default))
        logoSize = int(90*(x_size/self.default))

        nameFont = wx.Font(fontSize, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        self.firstName = wx.StaticText(self, label="Mississippi Valley State", style=wx.ST_ELLIPSIZE_END | wx.ALIGN_CENTER_HORIZONTAL)
        self.firstName.SetFont(nameFont)
        
        self.lastName = wx.StaticText(self, label="Delta Devils", style=wx.ST_ELLIPSIZE_END | wx.ALIGN_CENTER_HORIZONTAL)
        self.lastName.SetFont(nameFont)

        self.logo = LogoComponent(self, logoSize)
        self.logo.logo.SetBackgroundColour(wx.LIGHT_GREY)

        nameSizer = wx.BoxSizer(wx.VERTICAL)
        nameSizer.Add(self.firstName, 1, wx.EXPAND)
        nameSizer.Add(self.lastName, 1, wx.EXPAND)
        
        sizer = wx.BoxSizer()
        sizer.Add(nameSizer, 1, wx.EXPAND)
        sizer.Add(self.logo, 0, wx.EXPAND | wx.RIGHT, 5) 
        self.SetSizer(sizer)


if __name__ == "__main__":

    app = wx.App()
    frame = wx.Frame(None)
    panel = NameArea(frame, 300)
    sizer = wx.BoxSizer()
    sizer.Add(panel)
    frame.SetSizer(sizer)
    frame.Show()
    app.MainLoop()
        

