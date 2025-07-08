import os 
import wx



module_dir = os.path.dirname(os.path.abspath(__file__))


class LogoComponent(wx.Panel):

    def __init__(self, parent, size=85):
        super().__init__(parent)
        
        self.size = size
        self.logo = wx.StaticBitmap(self)
        self.logo.SetBitmap(wx.Image(f"{module_dir}/../../../../data/default.jpg", wx.BITMAP_TYPE_JPEG).Scale(size, size, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())

        sizer = wx.BoxSizer()
        sizer.Add(self.logo)
        self.SetSizer(sizer)
        

    def set_logo(self, leagueId, teamId):
        logoPath = module_dir+"/../../../../data/{}_logos/{}.png".format(leagueId.lower(), teamId.split(".")[-1])
        try:
            logo = wx.Image(logoPath, wx.BITMAP_TYPE_PNG).Scale(self.size, self.size, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        except:
            logo = wx.Image(f"{module_dir}/../../../../data/default.jpg", wx.BITMAP_TYPE_JPEG).Scale(self.size, self.size, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()

        self.logo.SetBitmap(logo)



