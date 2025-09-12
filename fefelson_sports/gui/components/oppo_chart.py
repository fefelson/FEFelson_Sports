from PySide6 import QtWidgets
from PySide6.QtCore import Qt
import matplotlib
matplotlib.use('QtAgg')  # Set Qt backend for Matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class OppositeChart(QtWidgets.QWidget):

    def __init__(self, parent, label="LABEL"):
        super().__init__(parent)
        self.setFixedHeight(50)

        baseSize = (1.3, 0.2)

        self.figures = {}
        self.axis = {}
        self.canvas = {}

        for off_def in ("off", "def"):
            self.figures[off_def] = Figure(figsize=baseSize)
            self.axis[off_def] = self.figures[off_def].add_subplot(111)
            self.canvas[off_def] = FigureCanvas(self.figures[off_def])

            self.figures[off_def].set_facecolor("darkslategrey") # Transparent figure background
            self.axis[off_def].set_facecolor("darkslategrey")     # Transparent axes background


        self.label = QtWidgets.QLabel(label)
        self.label.setFixedWidth(100)  # Match wx.StaticText size=(100, -1)
        self.label.setAlignment(Qt.AlignHCenter)  # Match wx.ALIGN_CENTER_HORIZONTAL
        self.label.setWordWrap(False)  # Disable wrapping to ensure ellipsis

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.canvas["def"])  # Stretch factor 1
        layout.addWidget(self.label, 0)  # No stretching
        layout.addWidget(self.canvas["off"])  # Stretch factor 1
        self.setLayout(layout)
        

    def _set_color(self, value, analytics):
        greaterThan = lambda v, a: v > a
        lessThan = lambda v, a: v < a

        colors = ["gold", "forestgreen", "springgreen", "palegoldenrod", "salmon", "red"]
        if analytics["best_value"] > analytics["worst_value"]:
            qList = ["q9", "q8", "q6", "q4", "q2", "q1"]
            func = greaterThan
        else:
            qList = ["q1", "q2", "q4", "q6", "q8", "q9"]
            func = lessThan

        barColor = "black"  # Default color
        for index, color in zip(qList, colors):
            if func(value, analytics[index]):
                barColor = color
                break
        return barColor

    def _set_score(self, value, analytics):
        greaterThan = lambda v, a: v > a
        lessThan = lambda v, a: v < a

        if analytics["best_value"] > analytics["worst_value"]:
            func = greaterThan
            oppFunc = lessThan
            analyticsDiff = analytics["best_value"] - analytics["worst_value"]
            teamDiff = analytics["best_value"] - value
            score = 0.03 if analyticsDiff == 0 else (analyticsDiff - teamDiff) / analyticsDiff + 0.03
        else:
            func = lessThan
            oppFunc = greaterThan
            analyticsDiff = analytics["worst_value"] - analytics["best_value"]
            teamDiff = value - analytics["best_value"]
            score = 0.03 if analyticsDiff == 0 else (analyticsDiff - teamDiff) / analyticsDiff + 0.03

        if func(value, analytics["best_value"]):
            score = 1
        elif oppFunc(value, analytics["worst_value"]):
            score = 0.03
        return score


    def set_panel_value(self, key, value, analytics):
        
        for off_def in ("off", "def"):
            self.axis[off_def].clear()
            self.axis[off_def].set_axis_off()
            label = f"{off_def}_{key}"
            barColor = self._set_color(value[label], analytics[label])
            score = self._set_score(value[label], analytics[label])

            if off_def == "off":
                axis = [0, 1, -1, 1]
            else:
                axis = [-1, 0, -1, 1]
                score = score * -1

            self.axis[off_def].axis(axis)
            self.axis[off_def].barh(0, score, 2, color=barColor)
            self.canvas[off_def].draw()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    frame = QtWidgets.QMainWindow()
    panel = OppositeChart(frame, "Points")
    frame.setCentralWidget(panel)
    frame.show()
    app.exec()