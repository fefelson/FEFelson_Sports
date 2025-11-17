from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt



class StringComponent(QWidget):

    def __init__(self, bgColor):
        super().__init__()
        
        valueFont = QFont("Serif", 12)
        valueFont.setBold(True)  

        self.value = QLabel(self.label)
        self.value.setFont(valueFont)
        self.value.setAlignment(Qt.AlignCenter)
        self.value.setFixedHeight(40)
        self.value.setStyleSheet(f"background-color: {bgColor}; color: white;")

        colorList = ["gold", "forestgreen", "springgreen", "khaki", "salmon", "red", "black"]
        self.colorDict = dict(zip(colorList, self.valueList))

        layout = QVBoxLayout()
        layout.addWidget(self.value)
        self.setLayout(layout)


    def _set_colors(self, value, analytics):
        greater_than = lambda v, a: v >= a
        less_than = lambda v, a: v < a

        colors = ["gold", "forestgreen", "springgreen", "khaki", "salmon", "red"]
        if analytics["best_value"] > analytics["worst_value"]:
            q_list = ["q9", "q8", "q6", "q4", "q2", "q1"]
            func = greater_than
        else:
            q_list = ["q1", "q2", "q4", "q6", "q8", "q9"]
            func = less_than

        background_color = "black"
        for idx, color in zip(q_list, colors):
            if func(value, analytics[idx]):
                background_color = color
                break

        return background_color   


    def set_panel(self, value, analytics=None):
        if analytics is not None:
            bgColor = self._set_colors(value, analytics)
            value = self.colorDict[bgColor]
            self.value.setText(f"{self.label}:\n{value}")

    def clear(self):
        self.value.setText(f"{self.label}:\n--")


###############################################################################
###############################################################################


class PlayDistComponent(StringComponent):

    label = "Play Calling"
    valueList = ["AIR RAID", "HEAVY PASS", "LEAN PASS", "BALANCED", "LEAN RUN", "HEAVY RUN", "SMASHMOUTH" ]
    
    def __init__(self, bgColor="midnightblue"):
        super().__init__(bgColor)


###############################################################################
###############################################################################


class CompPctComponent(StringComponent):

    label = "Comp Pct"
    valueList = ["ELITE", "SOLID", "DECENT", "AVERAGE", "SPOTTY", "WEAK", "TERRIBLE"]

    def __init__(self, bgColor="midnightblue"):
        super().__init__(bgColor)


###############################################################################
###############################################################################


class CompPerComponent(StringComponent):

    label = "Avg Completion"
    valueList = ["BOMBS AWAY", "LONG RANGE", "STRETCH FIELD", "MODERATE", "SHORT RANGE", "DINK DUNK", "TO NOWHERE"]

    def __init__(self, bgColor="midnightblue"):
        super().__init__(bgColor)


###############################################################################
###############################################################################


class CarPerComponent(StringComponent):

    label = "Avg Rush"
    valueList = ["LIGHTS OUT", "RUNNING DOWNHILL", "DECENT", "AVERAGE", "SPOTTY", "WEAK", "TO NOWHERE"]

    def __init__(self, bgColor="midnightblue"):
        super().__init__(bgColor)


###############################################################################
###############################################################################


class PassRushComponent(StringComponent):

    label = "Pass Rush"
    valueList = ["DOOMSDAY", "EARS PINNED BACK", "DECENT", "MODERATE", "SPOTTY", "WEAK", "NONEXISTENT"]

    def __init__(self, bgColor="maroon"):
        super().__init__(bgColor)
        

###############################################################################
###############################################################################


class PassDefComponent(StringComponent):

    label = "Pass Coverage"
    valueList = ["LOCKDOWN", "SOLID", "DECENT", "AVERAGE", "SPOTTY", "WEAK", "TORCHED"]

    def __init__(self, bgColor="maroon"):
        super().__init__(bgColor)
        


###############################################################################
###############################################################################


class RushDefComponent(StringComponent):

    label = "Rush Def"
    valueList = ["SOUL STEALING", "SOLID", "DECENT", "AVERAGE", "SPOTTY", "WEAK", "ROADKILL"]

    def __init__(self, bgColor="maroon"):
        super().__init__(bgColor)
        


###############################################################################
###############################################################################


class PassProtectComponent(StringComponent):

    label = "Pass Protection"
    valueList = ["ALL DAY", "SOLID", "DECENT", "AVERAGE", "NOT GREAT", "NOT GOOD", "OH BOY"]

    def __init__(self, bgColor="midnightblue"):
        super().__init__(bgColor)
        


###############################################################################
###############################################################################


class ThirdConvPctComponent(StringComponent):

    label = "3rd %"
    valueList = ["ELITE", "GREAT", "GOOD", "AVG", "IFFY", "BAD", "AWFUL"]

    def __init__(self, bgColor="midnightblue"):
        super().__init__(bgColor)


###############################################################################
###############################################################################


class GoPctComponent(StringComponent):

    label = "GO %"
    valueList = ["GOING", "PROBABY", "ABV AVG", "AVG", "BLW AVG", "RARELY", "KICKING"]

    def __init__(self, bgColor="midnightblue"):
        super().__init__(bgColor)


###############################################################################
###############################################################################


class FourthConvPctComponent(StringComponent):

    label = "4th %"
    valueList = ["ELITE", "GREAT", "GOOD", "AVG", "IFFY", "BAD", "AWFUL"]

    def __init__(self, bgColor="midnightblue"):
        super().__init__(bgColor)


###############################################################################
###############################################################################


class PaceComponent(StringComponent):

    label = "PACE"
    valueList = ["BLAZZING", "FAST", "ABOVE AVERAGE", "AVERAGE", "BELOW AVERAGE", "SLOW", "GLACIAL"]

    def _set_colors(self, value, analytics):
        greater_than = lambda v, a: v >= a
        less_than = lambda v, a: v < a

        colors = ["orange", "firebrick", "crimson", "burlywood", "darkcyan", "blue"]
        if analytics["best_value"] > analytics["worst_value"]:
            q_list = ["q9", "q8", "q6", "q4", "q2", "q1"]
            func = greater_than
        else:
            q_list = ["q1", "q2", "q4", "q6", "q8", "q9"]
            func = less_than

        background_color = "purple"
        for idx, color in zip(q_list, colors):
            if func(value, analytics[idx]):
                background_color = color
                break

        return background_color 

    def set_panel(self, value, analytics=None):
        if analytics is not None:
            self.colorDict = dict(zip(["orange", "firebrick", "crimson", "burlywood", "darkcyan", "blue", "purple"], self.valueList))
            bgColor = self._set_colors(value, analytics)
            value = self.colorDict[bgColor]
            fgColor = "white" if bgColor in ["firebrick", "crimson", "darkcyan", "blue", "purple"] else "black"
            self.value.setStyleSheet(f"background-color: {bgColor}; color: {fgColor};")
            self.value.setText(f"{self.label}:\n{value}")

    def __init__(self, bgColor="midnightblue"):
        super().__init__(bgColor)


class ShotPctComponent(StringComponent):

    label = "2s/3s"
    valueList = ["1950s", "HEAVY 2s", "LEAN 2s", "AVERAGE", "LEAN 3s", "HEAVY 3s", "DIE BY 3"]

    def __init__(self, bgColor="midnightblue"):
        super().__init__(bgColor)


class B2BComponent(StringComponent):

    label = "B2B"
    valueList = []

    def __init__(self, bgColor="black"):
        super().__init__(bgColor)
        self.value.setStyleSheet(f"background-color: {bgColor}; color: red;")
        


