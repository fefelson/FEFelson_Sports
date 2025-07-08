import wx
import matplotlib
matplotlib.use('WxAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure



class OppositeShot(wx.Panel):

    def __init__(self, parent, label="LABEL"):
        super().__init__(parent)

        baseSize = (1.3, 0.4)
        
        self.figures = {}
        self.axis = {}
        self.canvas = {}

        for off_def in ("offense", "defense"):
            self.figures[off_def] = Figure(figsize=baseSize,  layout='constrained')
            self.axis[off_def] = self.figures[off_def].add_subplot(111)
            self.canvas[off_def] = FigureCanvas(self, -1, self.figures[off_def])

        self.label = wx.StaticText(self, label=label, size=(100,-1), style=wx.ALIGN_CENTER_HORIZONTAL)

        
        sizer = wx.BoxSizer()
        sizer.Add(self.canvas["defense"], 1)
        sizer.Add(self.label, 0)
        sizer.Add(self.canvas["offense"], 1)
        self.SetSizer(sizer)



    def _set_color(self, value, analytics):

        greaterThan = lambda v,a: v > a
        lessThan = lambda v,a: v < a

        colors = ["gold", "forestgreen", "springgreen", "palegoldenrod", "salmon", "red"]
        if analytics.best_value > analytics.worst_value:
            qList = ["q9", "q8", "q6", "q4", "q2", "q1"]
            func = greaterThan
        else:
            qList = ["q1", "q2", "q4", "q6", "q8", "q9"]
            func = lessThan

        for index, color in zip(qList, colors):
            if func(value, analytics[index]):
                barColor = color
                break
            barColor = "black"

        
        return barColor


    def _set_score(self, value, analytics):
        greaterThan = lambda v,a: v > a
        lessThan = lambda v,a: v < a

        if analytics.best_value > analytics.worst_value:
            func = greaterThan
            oppFunc = lessThan
            analyticsDiff = analytics.best_value - analytics.worst_value
            teamDiff = analytics.best_value - value 
            score = (analyticsDiff - teamDiff)/analyticsDiff +.03
        else:
            func = lessThan
            oppFunc = greaterThan
            analyticsDiff = analytics.worst_value - analytics.best_value
            teamDiff = value - analytics.best_value
            score = (analyticsDiff-teamDiff)/analyticsDiff +.03
        if func(value, analytics.best_value):
            score = 1
        elif oppFunc(value, analytics.worst_value):
            score = .03
                
        return score 
    

    def set_panel_value(self, off_def, shotValue, shotAnalytics, pctValue, pctAnalytics):
        self.axis[off_def].clear()
        self.axis[off_def].set_axis_off()
        shotColor = self._set_color(shotValue, shotAnalytics)
        shotScore = self._set_score(shotValue, shotAnalytics)

        pctColor = self._set_color(pctValue, pctAnalytics)
        pctScore = self._set_score(pctValue, pctAnalytics)

        if off_def == "offense":
            axis = [0, 1, -1, 2] 
        else:
            axis = [-1, 0, -1, 2]
            shotScore = shotScore*-1
            pctScore = pctScore*-1

        self.axis[off_def].axis(axis)
        self.axis[off_def].barh(1, shotScore, 1, color=shotColor)
        self.axis[off_def].barh(0, pctScore, 1, color=pctColor)
        self.canvas[off_def].draw()
        self.canvas[off_def].Refresh()
    

   


            