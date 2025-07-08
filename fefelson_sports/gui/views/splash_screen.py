import wx
import wx.lib.agw.advancedsplash as AS
import os


class SplashScreen(AS.AdvancedSplash):

    def __init__(self, parent, timeout=2000):
        
        # Load the image for the splash screen

        module_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = module_dir+"/../../../data/spirit_banner.jpg"

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file {image_path} not found. Please ensure it exists in the script directory.")

        # Convert the image to a bitmap
        image = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
        # Optionally resize the image to fit the splash screen (e.g., 400x400)
        image = image.Scale(500, 500, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.Bitmap(image)
        shadow = wx.WHITE
        
        super().__init__(parent, bitmap=bitmap, timeout=timeout,
                           agwStyle=AS.AS_TIMEOUT |
                           AS.AS_CENTER_ON_PARENT |
                           AS.AS_SHADOW_BITMAP,
                           shadowcolour=shadow)
   

        # Bind the close event to transition to the main window
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, event):
        # Destroy the splash screen and show the main application window
        parent = self.GetParent()
        parent.Show()
        self.Destroy()
        



# class App(wx.App):
#     def OnInit(self):
#         # Show the splash screen
#         splash = SplashScreen()
#         splash.Show()
#         return True

