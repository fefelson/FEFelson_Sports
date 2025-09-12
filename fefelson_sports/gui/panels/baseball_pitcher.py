from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QFont

from ..components.label_components import IntComponent, FloatComponent, PctComponent

from ...database.stores.analytics import AnalyticsStore
from ...database.stores.baseball import PitcherStore

#for debugging
# from pprint import pprint 


class BullpenPanel(QWidget):

    def __init__(self):
        super().__init__()

        self.teamId = None 

        self.name = QLabel("bullpen")
        self.name.setFont(QFont("Serif", 15))

        self.ip = FloatComponent("IP")
        self.ip.label.setFixedSize(30,30)

        self.w = IntComponent('W')
        self.w.label.setFixedSize(30,30)

        self.l = IntComponent('L')
        self.l.label.setFixedSize(30,30)

        self.sv = PctComponent("SV")
        self.sv.label.setFixedSize(30,30)

        self.era = FloatComponent("ERA", 2)
        self.era.label.setFixedSize(30,30)

        self.whip = FloatComponent("WHIP", 2)
        self.whip.label.setFixedSize(30,30)

        self.k9 = FloatComponent("K/9", 2)
        self.k9.label.setFixedSize(30,30)


        layout = QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.name, 1)
        layout.addWidget(self.ip)
        layout.addWidget(self.w)
        layout.addWidget(self.l)
        layout.addWidget(self.sv)
        layout.addWidget(self.era)
        layout.addWidget(self.whip)
        layout.addWidget(self.k9)

        self.setLayout(layout)


    def set_team(self, team):
        self.teamId = team["team"]["team_id"]



    def set_stats(self, session, timeFrame, awayHome):
        metrics = AnalyticsStore()
        analytics = {}
        for metric in ("ip", "w", "l", "sv", "era", "whip", "k9"):
            analytics[metric] = metrics.get_league_metrics("MLB", timeFrame, awayHome, "bullpen", metric, session)

        stats = PitcherStore().get_bullpen_stats(self.teamId, timeFrame, awayHome, session)
        if stats:
            self.ip.set_panel(stats["ip"], analytics["ip"])
            self.w.set_panel(stats['w'], analytics["w"])
            self.l.set_panel(stats['l'], analytics["l"])
            self.sv.set_panel(stats['sv'], analytics["sv"])
            self.era.set_panel(stats['era'], analytics["era"])
            self.whip.set_panel(stats['whip'], analytics["whip"])
            self.k9.set_panel(stats['k9'], analytics["k9"])
        else:
            self._clear_stats()


    def _clear_stats(self):
        self.ip.set_panel('')
        self.w.set_panel('')
        self.l.set_panel('')
        self.sv.set_panel('')
        self.era.set_panel('')
        self.whip.set_panel('')
        self.k9.set_panel('')
        


    def clear_pitcher(self):
        self.pitcherId = None
        self.name.setText("")
        self._clear_stats()



class StarterPanel(QWidget):

    def __init__(self):
        super().__init__()

        self.pitcherId = None 

        self.name = QLabel()
        self.name.setWordWrap(True)
        font = QFont("Serif", 20)
        font.setBold(True)
        self.name.setFont(font)

        self.gs = IntComponent("GS")
        self.ip = FloatComponent("IP per")

        self.w = IntComponent('W')
        self.w .label.setFixedSize(50,50)

        self.l = IntComponent('L')
        self.l.label.setFixedSize(50,50)

        self.era = FloatComponent("ERA", 2)
        self.era.label.setFixedSize(50,50)

        self.whip = FloatComponent("WHIP", 2)
        self.whip.label.setFixedSize(50,50)

        self.k9 = FloatComponent("K/9", 2)
        self.k9.label.setFixedSize(50,50)

        layout = QHBoxLayout()
        layout.addWidget(self.name, 1)
        layout.addWidget(self.gs)
        layout.addWidget(self.ip)
        layout.addWidget(self.w)
        layout.addWidget(self.l)
        layout.addWidget(self.era)
        layout.addWidget(self.whip)
        layout.addWidget(self.k9)

        self.setLayout(layout)


    def set_starter(self, pitcher):
        
        self.clear_pitcher()
        if pitcher:
            self.name.setText(f"{pitcher[1]}    {pitcher[2]}")
            self.pitcherId = pitcher[0]



    def set_stats(self, session, timeFrame, awayHome):
        store = PitcherStore()
        metrics = AnalyticsStore()
        analytics = {}
        for metric in ("w", "l", "era", "whip", "k9"):
            analytics[metric] = metrics.get_league_metrics("MLB", timeFrame, awayHome, "starter", metric, session)

        stats = store.get_pitcher_stats(self.pitcherId, timeFrame, awayHome, session)
        
        if stats:
            self.gs.set_panel(stats["gs"])
            self.ip.set_panel(stats["ip"])
            self.w.set_panel(stats['w'], analytics["w"])
            self.l.set_panel(stats['l'], analytics["l"])
            self.era.set_panel(stats['era'], analytics["era"])
            self.whip.set_panel(stats['whip'], analytics["whip"])
            self.k9.set_panel(stats['k9'], analytics["k9"])
        else:
            self._clear_stats()


    def _clear_stats(self):
        self.gs.set_panel('')
        self.ip.set_panel('')
        self.w.set_panel('')
        self.l.set_panel('')
        self.era.set_panel('')
        self.whip.set_panel('')
        self.k9.set_panel('')
        


    def clear_pitcher(self):
        self.pitcherId = None
        self.name.setText("")
        self._clear_stats()


class PitcherStats(QWidget):

    def __init__(self):
        super().__init__()

        self.awayHome = None

        self.starterPanel = StarterPanel()
        self.bullpenPanel = BullpenPanel()

        layout = QVBoxLayout()
        layout.addWidget(self.starterPanel)
        layout.addWidget(self.bullpenPanel)
        self.setLayout(layout)


    def set_team(self, awayHome, team):
        self.awayHome = awayHome 

        self.starterPanel.set_starter(team["starter"])
        self.bullpenPanel.set_team(team)


    def set_stats(self, session, timeFrame, awayHome):
        awayHome = self.awayHome if awayHome == "away_home" else awayHome
        self.starterPanel.set_stats(session, timeFrame, awayHome)
        self.bullpenPanel.set_stats(session, timeFrame, awayHome)
        
        






