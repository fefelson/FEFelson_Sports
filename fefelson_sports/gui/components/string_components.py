from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt



class StringComponent(QWidget):

    def __init__(self):
        super().__init__()
        
        valueFont = QFont("Serif", 12)
        valueFont.setBold(True)  

        self.value = QLabel(self.label)
        self.value.setFont(valueFont)
        self.value.setAlignment(Qt.AlignCenter)
        self.value.setFixedHeight(40)
        self.value.setStyleSheet(f"background-color: {self.bgColor}; color: white;")

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


###############################################################################
###############################################################################


class PlayDistComponent(StringComponent):

    bgColor = "midnightblue"
    label = "Play Calling"
    valueList = ["AIR RAID", "HEAVY PASS", "LEAN PASS", "BALANCED", "LEAN RUN", "HEAVY RUN", "SMASHMOUTH" ]
    
    def __init__(self):
        super().__init__()


###############################################################################
###############################################################################


class CompPctComponent(StringComponent):

    bgColor = "midnightblue"
    label = "Comp Pct"
    valueList = ["ELITE", "SOLID", "DECENT", "AVERAGE", "SPOTTY", "WEAK", "TERRIBLE"]

    def __init__(self):
        super().__init__()


###############################################################################
###############################################################################


class CompPerComponent(StringComponent):

    bgColor = "midnightblue"
    label = "Avg Completion"
    valueList = ["BOMBS AWAY", "LONG RANGE", "STRETCH FIELD", "MODERATE", "SHORT RANGE", "DINK DUNK", "TO NOWHERE"]

    def __init__(self):
        super().__init__()


###############################################################################
###############################################################################


class CarPerComponent(StringComponent):

    bgColor = "midnightblue"
    label = "Avg Rush"
    valueList = ["LIGHTS OUT", "RUNNING DOWNHILL", "DECENT", "AVERAGE", "SPOTTY", "WEAK", "TO NOWHERE"]

    def __init__(self):
        super().__init__()


###############################################################################
###############################################################################


class PassRushComponent(StringComponent):

    bgColor = "maroon"
    label = "Pass Rush"
    valueList = ["DOOMSDAY", "EARS PINNED BACK", "DECENT", "MODERATE", "SPOTTY", "WEAK", "NONEXISTENT"]

    def __init__(self):
        super().__init__()
        

###############################################################################
###############################################################################


class PassDefComponent(StringComponent):

    bgColor = "maroon"
    label = "Pass Coverage"
    valueList = ["LOCKDOWN", "SOLID", "DECENT", "AVERAGE", "SPOTTY", "WEAK", "TORCHED"]

    def __init__(self):
        super().__init__()
        


###############################################################################
###############################################################################


class RushDefComponent(StringComponent):

    bgColor = "maroon"
    label = "Rush Def"
    valueList = ["SOUL STEALING", "SOLID", "DECENT", "AVERAGE", "SPOTTY", "WEAK", "ROADKILL"]

    def __init__(self):
        super().__init__()
        


###############################################################################
###############################################################################


class PassProtectComponent(StringComponent):

    bgColor = "midnightblue"
    label = "Pass Protection"
    valueList = ["ALL DAY", "SOLID", "DECENT", "AVERAGE", "NOT GREAT", "NOT GOOD", "OH BOY"]

    def __init__(self):
        super().__init__()
        


