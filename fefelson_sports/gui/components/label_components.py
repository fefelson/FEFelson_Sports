from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt


###############################################################################
###############################################################################





###############################################################################
###############################################################################



class LabelComponent(QWidget):
    def __init__(self, label="label"):
        super().__init__()
        
        self.label = QLabel(label)
        self.value = QLabel("--")
        
        self._set_fonts()
        self._set_layout()


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

        text_color = "white" if background_color in ("red", "forestgreen", "black") else "black"
        return background_color, text_color


    def _set_fonts(self):
        label_font = QFont("Serif", 12)
        value_font = QFont("Serif", 15)
        value_font.setBold(True)

        self.label.setFont(label_font)
        self.value.setFont(value_font)

        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.value.setAlignment(Qt.AlignHCenter | Qt.AlignTop)


    def _set_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.value)
        self.setLayout(layout)

    def _set_label(self, label_text):
        self.label.setText(label_text)

    def _set_value(self, value_text):
        self.value.setText(str(value_text))

    def set_panel(self, value, analytics=None, *, label=None):
        self._set_value(value)
        if analytics is not None:
            bg_color, fg_color = self._set_colors(value, analytics)
            self.label.setStyleSheet(f"background-color: {bg_color}; color: {fg_color};")
        else:
            self.label.setStyleSheet(f"background-color: slateblue; color: white;")
        if label is not None:
            self._set_label(label)


###############################################################################
###############################################################################


class IntComponent(LabelComponent):

    def __init__(self, label="int"):
        super().__init__(label)


    def _set_value(self, value):
        try:
            value = int(value)
        except: 
            value = '--'
        super()._set_value(value)



###############################################################################
###############################################################################



class FloatComponent(LabelComponent):
    def __init__(self, label="float", n=1):
        self.digits = n
        super().__init__(label)

    def _set_value(self, value):
        try:
            value = round(value, self.digits)
        except:
            value = '--'
        super()._set_value(value)


###############################################################################
###############################################################################


class PctComponent(LabelComponent):

    def __init__(self, label="pct", n=1):
        self.digits = n
        super().__init__(label)


    def _set_value(self, value):
        try:
            value = round(value, self.digits)
            super()._set_value(f"{value}%")
        except:
            super()._set_value(f"--")




###############################################################################
###############################################################################


class OddsComponent(LabelComponent):

    def __init__(self, label="odds"):
        super().__init__(label)


    def _set_value(self, value):
        if float(value) > 0:
            value = f"+{value}"
        super()._set_value(f"{value}")




###############################################################################
###############################################################################


class MoneyComponent(LabelComponent):

    def __init__(self, label="money", n=2):
        self.digits = n
        super().__init__(label)


    def _set_value(self, value):
        try:
            value = round(value, self.digits)
            super()._set_value(f"${value}")
        except:
            super()._set_value(f"--")

###############################################################################
###############################################################################

