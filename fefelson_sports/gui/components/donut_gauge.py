import sys
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from PySide6.QtCore import Qt, QRectF
import math

class DonutGauge(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0  # Current value (0-100)
        self._min_value = 0
        self._max_value = 100
        self._left_color = QColor(255, 0, 0)  # Red for left half
        self._right_color = QColor(0, 255, 0)  # Green for right half
        self._background_color = QColor(200, 200, 200)  # Background
        self._needle_color = QColor(0, 0, 0)  # Black needle
        self.setMinimumSize(200, 100)  # Ensure enough space for semi-circle

    def setValue(self, value):
        """Set the gauge value (0-100) and update the widget."""
        if self._min_value <= value <= self._max_value:
            self._value = value
            self.update()

    def setColors(self, left_color, right_color):
        """Set the colors for the left and right halves of the donut."""
        self._left_color = QColor(left_color)
        self._right_color = QColor(right_color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Define dimensions
        width = self.width()
        height = self.height()
        size = min(width, height * 2)  # Adjust for semi-circle
        outer_radius = size * 0.45
        inner_radius = size * 0.35
        center_x = width / 2
        center_y = height  # Bottom center for semi-circle

        # Draw background donut
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._background_color)
        outer_rect = QRectF(center_x - outer_radius, center_y - outer_radius * 2,
                           outer_radius * 2, outer_radius * 2)
        inner_rect = QRectF(center_x - inner_radius, center_y - inner_radius * 2,
                           inner_radius * 2, inner_radius * 2)
        painter.drawArc(outer_rect, 0, 180 * 16)  # 180 degrees (semi-circle)
        painter.setBrush(self.background().color())
        painter.drawEllipse(inner_rect)  # Cut out inner circle

        # Draw left half (0-50)
        painter.setBrush(self._left_color)
        painter.drawArc(outer_rect, 90 * 16, 90 * 16)  # Left half: 90° to 180°
        painter.setBrush(self.background().color())
        painter.drawArc(inner_rect, 90 * 16, 90 * 16)  # Cut out inner arc

        # Draw right half (50-100)
        painter.setBrush(self._right_color)
        painter.drawArc(outer_rect, 0, 90 * 16)  # Right half: 0° to 90°
        painter.setBrush(self.background().color())
        painter.drawArc(inner_rect, 0, 90 * 16)  # Cut out inner arc

        # Draw needle
        angle = 180 - (self._value / self._max_value) * 180  # Map 0-100 to 180°-0°
        needle_length = outer_radius * 0.9
        needle_end_x = center_x + needle_length * math.cos(math.radians(angle))
        needle_end_y = center_y - needle_length * math.sin(math.radians(angle))
        
        painter.setPen(QPen(self._needle_color, 3))
        painter.drawLine(center_x, center_y, needle_end_x, needle_end_y)

        # Draw center point
        painter.setBrush(self._needle_color)
        painter.drawEllipse(QRectF(center_x - 5, center_y - 5, 10, 10))

    def resizeEvent(self, event):
        """Ensure the widget updates when resized."""
        self.update()

# Example usage
if __name__ == "__main__":
    app = QApplication(sys.argv)
    print("here")
    window = QWidget()
    window.setWindowTitle("Donut Gauge")
    window.resize(300, 200)
    
    gauge = DonutGauge(window)
    gauge.setValue(75)  # Set initial value
    gauge.setColors("#FF0000", "#00FF00")  # Red left, Green right
    
    window.show()
    sys.exit(app.exec())