from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt


###############################################################################
###############################################################################





###############################################################################
###############################################################################



class LabelComponent(QWidget):
    def __init__(self, parent=None, label="Label"):
        super().__init__(parent)
        
        self.label = QLabel(label)
        self.value = QLabel("VALUE")
        
        self._set_fonts()
        self._set_layout()

    def _set_fonts(self):
        label_font = QFont("Serif", 9)
        value_font = QFont("Serif", 10)
        value_font.setBold(True)

        self.label.setFont(label_font)
        self.value.setFont(value_font)

        self.label.setAlignment(Qt.AlignCenter)
        self.value.setAlignment(Qt.AlignCenter)

    def _set_colors(self, value, analytics):
        greater_than = lambda v, a: v > a
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
            self.setStyleSheet(f"background-color: {bg_color}; color: {fg_color};")
        if label is not None:
            self._set_label(label)


###############################################################################
###############################################################################


class IntComponent(LabelComponent):

    def __init__(self, parent, label="x pct"):
        super().__init__(parent, label)


    def _set_value(self, value):
        value = int(value)
        super()._set_value(value)



###############################################################################
###############################################################################



class FloatComponent(LabelComponent):
    def __init__(self, parent=None, label="Float Value"):
        super().__init__(parent, label)

    def _set_value(self, value, digits=1):
        value = round(value, digits)
        super()._set_value(value)


###############################################################################
###############################################################################


class PctComponent(LabelComponent):

    def __init__(self, parent, label="x pct"):
        super().__init__(parent, label)


    def _set_value(self, value, digits=0):
        value = round(value, digits)
        super()._set_value(f"{value}%")



###############################################################################
###############################################################################



if __name__ == "__main__":
    import sys
    from types import SimpleNamespace

    app = QApplication(sys.argv)

    # Simulated analytics object
    analytics = {
        "best_value": 10,
        "worst_value": 0,
        "q1": 1, "q2": 2, "q4": 4, "q6": 6, "q8": 8, "q9": 9
    }

    widget = FloatComponent(label="Example")
    widget.set_panel(7.3, )
    widget.resize(100, 60)
    widget.show()

    sys.exit(app.exec())
