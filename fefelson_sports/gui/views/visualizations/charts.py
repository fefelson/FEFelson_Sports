import wx
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from ....utils.color_helper import ColorScheme




class Chart:
    _figHeight = 1.5  # Default height in inches
    _figWidth = 3  # Default width in inches
    _title = None
    _xLabel = None
    _yLabel = None
    _grid = True
    _backgroundColor = ColorScheme.chrome_chill
    _frameColor = ColorScheme.dark_matter_haunted_house
    _titleColor = ColorScheme.laser_lemon
    _xLabelColor = None
    _yLabelColor = None
    _gridColor = ColorScheme.laser_lemon


    def __init__(self, parent):
        # Initialize the Matplotlib figure and canvas
        self.figure=Figure(layout='constrained')
        self.figure.set_figheight(self._figHeight)
        self.figure.set_figwidth(self._figWidth)
        self.axes = self.figure.add_subplot(111)  # Single subplot
        self.canvas = FigureCanvas(parent, -1, self.figure)
        self.on_setup()        


    def on_setup(self):
        # Set default background and frame colors
        self.axes.clear()
        self.axes.set_facecolor(ColorScheme.to_matplotlib_color(self._backgroundColor))
        self.figure.set_facecolor(ColorScheme.to_matplotlib_color(self._frameColor))

        if self._title:
            self.axes.set_title(self._title, color=ColorScheme.to_matplotlib_color(self._titleColor))
        self.axes.set_axis_off()


class TrackLine(Chart):
    
    _frameColor = ColorScheme.lunar_lavender
    _titleColor = ColorScheme.palm_emerald
    _figHeight = 1  
    _title = "Line Movement"
    _xLabel = None
    _yLabel = None

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


    def set_panel(self, data):
        self._title = f"{data['title']}"
        self.on_setup()
        self.set_axes(data)

        self.axes.plot(data["xData"], data["yData"], linestyle='dashdot', color=ColorScheme.to_matplotlib_color(ColorScheme.stardust_gold), label=data["label"])

        self.axes.legend(loc="lower left")
        self.canvas.draw()
        self.canvas.Refresh()


    def set_axes(self, data):
        # self.axes.set_xticks(data["xData"])
        # self.axes.set_xticklabels(data["xLabels"], rotation=45)
        
        # Set axis limits of time dependent data dynamically
        start = 0
        end = 300 if data["xData"][-1] < 300 else data["xData"][-1] +60
        y_min = min(data["yData"])-2
        y_max = max(data["yData"]) +2
        self.axes.axis([start, end, y_min, y_max])
        




# Fixed BarChart class
class BarChart(Chart):
    _figHeight = 2
    _figWidth = 3

    _lowerBound = -20
    _upperBound = 20
    _aLabel = "Home"
    _bLabel = "Away"


    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


    def set_axes(self, length):
        # Set axis limits dynamically
        start = 0 if length <=20 else length-20
        end = length + 1 if length > 10 else 13
        y_min = self._lowerBound
        y_max = self._upperBound
        self.axes.axis([start, end, y_min, y_max])


    def set_colors(self, team):
        homeColor = ColorScheme.to_matplotlib_color(team['primary_color'].iloc[0])
        awayColor = ColorScheme.to_matplotlib_color(team["secondary_color"].iloc[0])

        return homeColor, awayColor


    def set_panel(self, team, aBoxes, bBoxes, sixAvg, thirteenAvg):

        from pprint import pprint 
        pprint(aBoxes)
        
        aColor, bColor = self.set_colors(team)
        self.on_setup()
        self.set_axes(len(aBoxes)+len(bBoxes))

        # Set up the chart
        self.axes.bar([x[0] for x in aBoxes], [x[1] for x in aBoxes], color=aColor, label=self._aLabel)
        self.axes.bar([x[0] for x in bBoxes], [x[1] for x in bBoxes], color=bColor, label=self._bLabel)

        # Plot moving averages if available
        if sixAvg:
            self.axes.plot([i+6 for i in range(len(sixAvg))], sixAvg, color=ColorScheme.to_matplotlib_color(ColorScheme.neon_green),
                           label=f"6 GMA {sixAvg[-1]:.1f}")
        if thirteenAvg:
            self.axes.plot([i+13 for i in range(len(thirteenAvg))], thirteenAvg, color=ColorScheme.to_matplotlib_color(ColorScheme.grid_grape),
                           label=f"13 GMA {thirteenAvg[-1]:.1f}")

        self.axes.legend(loc="lower left")
        self.canvas.draw()
        self.canvas.Refresh()



class WinLossChart(BarChart):
    _aLabel = "Home"
    _bLabel = "Away"
    _title = "Win / Loss"

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


class SpreadChart(BarChart):
    
    _aLabel = "Home"
    _bLabel = "Away"
    _title = "Favored By (Pts Spread)"

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    
class ATSChart(BarChart):
    _aLabel = "Win"
    _bLabel = "Loss"
    _title = "Against The Spread (ATS)"

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def set_colors(self, team):
        return [ColorScheme.to_matplotlib_color(ColorScheme.moss_mint),
                ColorScheme.to_matplotlib_color(ColorScheme.neon_red)]

          
        



class WinROIChart(BarChart):
    _aLabel = "Win"
    _bLabel = "Loss"
    _discriminator = "isWinner"
    _lowerBound = -400
    _upperBound = 400
    _selector = "money"
    _title = "Win ROI"
    _xLabel = "Game Date"
    _yLabel = "Money Returned"

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def dataMaker(self, gameLog):
        aList = []
        bList = []
        data = []
        for i, mO in enumerate(gameLog):
            money = mO.get(self._selector)
            if money is not None:
                if mO.get(self._discriminator):  # Winner
                    if money > 0:
                        roi = 100 + int(money)
                    else:
                        roi = 100 + ((10000 / max(abs(money), 1)) * 100) if money != 0 else 0
                    aList.append((i, roi))
                    data.append(roi)
                else:  # Loser
                    bList.append((i, -100))
                    data.append(-100)
        return aList, bList, data

