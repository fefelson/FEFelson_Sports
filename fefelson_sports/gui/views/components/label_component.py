import wx



###############################################################################
###############################################################################



class LabelComponent(wx.Panel):

    def __init__(self, parent, label="label"):
        super().__init__(parent)
        
        self.label = None
        self.value = None

        self._set_components(label)
        self._set_fonts()
        self._set_layout()


    def _set_analytics(self, value, analytics):
        # Use the provided analytics DataFrame
        backgroundColor, textColor = self._set_colors(value, analytics)
        self.SetBackgroundColour(wx.Colour(backgroundColor))
        self.SetForegroundColour(wx.Colour(textColor))


    def _set_colors(self, value, analytics):
        greaterThan = lambda v,a: v > a
        lessThan = lambda v,a: v < a

        colors = ["gold", "forest green", "spring green", "medium goldenrod", "salmon", "red"]
        if analytics.best_value > analytics.worst_value:
            qList = ["q9", "q8", "q6", "q4", "q2", "q1"]
            func = greaterThan
        else:
            qList = ["q1", "q2", "q4", "q6", "q8", "q9"]
            func = lessThan

        for index, color in zip(qList, colors):
            if func(value, analytics[index]):
                backgroundColor = color
                break
            backgroundColor = "black"

        textColor = "black"
        if backgroundColor in ("red", "forest green", "black"):
            textColor = "white"
        return backgroundColor, textColor


    def _set_components(self, label):

        self.label = wx.StaticText(self, label=label, size=(40,20), style=wx.ALIGN_CENTER_HORIZONTAL )
        self.value = wx.StaticText(self, label="VALUE", size=(40,20), style=wx.ALIGN_CENTER_HORIZONTAL)


    def _set_fonts(self):
        
        labelFont = wx.Font(9, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        valueFont = wx.Font(10, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        self.label.SetFont(labelFont)
        self.value.SetFont(valueFont)


    def _set_label(self, label):
        self.label.SetLabel(label)



    def _set_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label, 1, wx.EXPAND)
        sizer.Add(self.value, 1, wx.EXPAND )
        self.SetSizer(sizer)


    def _set_value(self, value):
        self.value.SetLabel(f"{value}")


    def bind_to_ctrl(self, handler):
        self.Bind(wx.EVT_LEFT_DCLICK, handler)
        self.label.Bind(wx.EVT_LEFT_DCLICK, handler)
        self.value.Bind(wx.EVT_LEFT_DCLICK, handler)


    def set_panel(self, value, analytics=None, *, label=None):
        self._set_value(value)
        if analytics is not None:
            self._set_analytics(value, analytics)
        if label is not None:
            self._set_label(label)



###############################################################################
###############################################################################


class IntComponent(LabelComponent):

    def __init__(self, parent, label="x pct"):
        super().__init__(parent, label)


    def _set_value(self, value):
        value = int(value)
        return super()._set_value(value)



###############################################################################
###############################################################################


class FloatComponent(LabelComponent):

    def __init__(self, parent, label="x pct"):
        super().__init__(parent, label)


    def _set_value(self, value, digits=1):
        value = round(value, digits)
        return super()._set_value(value)



    
###############################################################################
###############################################################################


class PctComponent(LabelComponent):

    def __init__(self, parent, label="x pct"):
        super().__init__(parent, label)


    def _set_value(self, value, digits=0):
        value = round(value, digits)
        return super()._set_value(f"{value}%")


###############################################################################
###############################################################################



class OverallComponent(FloatComponent):

    def __init__(self, parent, label="OVERALL"):
        super().__init__(parent, label)

    def _set_components(self, label):

        self.label = wx.StaticText(self, label=label, size=(70,25), style=wx.ALIGN_CENTER_HORIZONTAL )
        self.value = wx.StaticText(self, label="VALUE", size=(70,25), style=wx.ALIGN_CENTER_HORIZONTAL)



    def _set_fonts(self):

        labelFont = wx.Font(10, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        valueFont = wx.Font(14, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        self.label.SetFont(labelFont)
        self.value.SetFont(valueFont)


###############################################################################
###############################################################################


class PaceComponent(LabelComponent):

    def __init__(self, parent):
        super().__init__(parent, label="pace")


    def _set_components(self, label):
        self.SetMinSize((175,-1))

        self.value = wx.StaticText(self, label="VALUE", style=wx.ALIGN_CENTER_HORIZONTAL)



    def _set_fonts(self):
        
        valueFont = wx.Font(14, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.value.SetFont(valueFont)


    def _set_layout(self):
        self.SetBackgroundColour(wx.GREEN)
        sizer = wx.BoxSizer()
        sizer.Add(self.value, 1, wx.ALIGN_CENTER_VERTICAL )
        self.SetSizer(sizer)


    def _set_colors(self, value, analytics):

        colors = ["magenta", "orange red", "orange", "medium goldenrod", "cyan", "blue"]
        textMsgs = ["FASTEST", "FASTER", "FAST", "MEDIUM", "SLOW", "SLOWER"]
        qList = ["q9", "q8", "q6", "q4", "q2", "q1"]
        
        for index, color, txtMsg in zip(qList, colors, textMsgs):
            if value > analytics[index]:
                backgroundColor = color
                text = txtMsg
                break
            backgroundColor = "violet"
            text = "SLOWEST"

        textColor = "black"
        if backgroundColor in ("red", "forest green", "gold", "black"):
            textColor = "white"
        return text, backgroundColor, textColor


    def set_panel(self, value, analytics=None, *, label=None):

        text, backgroundColor, textColor = self._set_colors(value, analytics)
        self._set_value(f"{text}")
        self.SetBackgroundColour(wx.Colour(backgroundColor))
        self.SetForegroundColour(wx.Colour(textColor))
        self.Layout()

        


if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    panel = PaceComponent(frame)
    sizer = wx.BoxSizer()
    sizer.Add(panel, 0)
    frame.SetSizer(sizer)
    frame.Show()
    app.MainLoop()