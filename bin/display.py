import os
import sys 
from PySide6.QtWidgets import QApplication, QSplashScreen, QMainWindow, QHBoxLayout, QWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
import time


from fefelson_sports.gui.views.dashboards.dashboard_test import DashboardTest
from fefelson_sports.sports.leagues import MLB
from fefelson_sports.gui.controllers.dashboard_controller import DashboardController


basePath = os.environ["HOME"] +"/FEFelson/FEFelson_Sports/leagues"    
splashPath = os.environ["HOME"]+"/FEFelson/FEFelson_Sports/data/spirit_banner.jpg"



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard Dev")
        

        # Create central widget with layout
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)
        
        # Initialize TickerPanel and BaseballMatchup
        self.dashboard = DashboardTest(central_widget)
        layout.addWidget(self.dashboard, 1)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and show the splash screen
    # splash_pix = QPixmap(splashPath)  # Replace with your image path
    # splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    # splash.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
    # splash.show()

    # # Simulate some loading time
    # for _ in range(5):
    #     app.processEvents()  # Keep UI responsive
    #     time.sleep(0.5)  # Simulate loading delay
    league = MLB()
    window = MainWindow()
    controller = DashboardController(league, window)
   
    window.show() 

    # Close the splash screen
    # splash.finish(window)

    sys.exit(app.exec())

