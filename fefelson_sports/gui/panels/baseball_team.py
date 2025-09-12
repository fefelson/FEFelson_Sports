from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea
from PySide6.QtGui import QFont

from ..components.label_components import FloatComponent, PctComponent, IntComponent

from ...database.stores.analytics import AnalyticsStore
from ...database.stores.baseball import BatterStore, TeamStatStore


class BaseballTeamStats(QScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)

        scrollPanel = QWidget()
        scrollLayout = QVBoxLayout()
        scrollPanel.setLayout(scrollLayout)    

        self.teamId = None

        self.r = FloatComponent('R')
        self.r.label.setFixedHeight(75)

        self.h = FloatComponent('H')
        self.h.label.setFixedHeight(75)

        self.errors = FloatComponent('E')
        self.errors.label.setFixedHeight(75)

        self.hr = FloatComponent("HR")
        self.hr.label.setFixedHeight(50)

        self.sb = FloatComponent("SB")
        self.sb.label.setFixedHeight(50)

        self.lob = PctComponent('LOB')
        self.lob.label.setFixedHeight(50)

        self.avg = FloatComponent("AVG", 3)
        self.avg.label.setFixedHeight(50)

        self.obp = FloatComponent("OBP", 3)
        self.obp.label.setFixedHeight(50)

        self.slg = FloatComponent("SLG", 3)
        self.slg.label.setFixedHeight(50)

        

        self.lineup = BattingOrderArea()

        headline = QHBoxLayout()
        headline.addWidget(self.r)
        headline.addWidget(self.h)
        headline.addWidget(self.errors)

        lineLayout = QHBoxLayout()
        lineLayout.addWidget(self.avg)
        lineLayout.addWidget(self.obp)
        lineLayout.addWidget(self.slg)
        lineLayout.addWidget(self.hr)
        lineLayout.addWidget(self.lob)
        lineLayout.addWidget(self.sb)

        scrollLayout.addLayout(headline, 2)
        scrollLayout.addLayout(lineLayout, 1)
        scrollLayout.addWidget(self.lineup)

        self.setWidget(scrollPanel)


    def set_team(self, awayHome, team):
        self.awayHome = awayHome
        self.teamId = team["team"]["team_id"]
        self.lineup.set_lineup(team["lineup"])


    def set_stats(self, session, timeFrame, awayHome):
        awayHome = self.awayHome if awayHome == "away_home" else awayHome
        self.lineup.set_stats(session, timeFrame, awayHome)

        metrics = AnalyticsStore()
        analytics = {}
        for metric in ("r", "h", "hr", "sb", "lob", "avg", "obp", "slg", "errors"):
            analytics[metric] = metrics.get_league_metrics("MLB", timeFrame, awayHome, "team", metric, session)
        stats = TeamStatStore().get_team_stats(self.teamId, timeFrame, awayHome, session)
        if stats:
            self.r.set_panel(stats['r'], analytics['r'])
            self.h.set_panel(stats['h'], analytics['h'])
            self.hr.set_panel(stats['hr'], analytics['hr'])
            self.sb.set_panel(stats['sb'], analytics['sb'])
            self.lob.set_panel(stats['lob'], analytics['lob'])
            self.avg.set_panel(stats['avg'], analytics['avg'])
            self.obp.set_panel(stats['obp'], analytics['obp'])
            self.slg.set_panel(stats['slg'], analytics['slg'])
            self.errors.set_panel(stats['errors'], analytics['errors'])
        else:
            self.r.set_panel("")
            self.h.set_panel("")
            self.hr.set_panel("")
            self.sb.set_panel("")
            self.lob.set_panel("")
            self.avg.set_panel("")
            self.obp.set_panel("")
            self.slg.set_panel("")
            self.errors.set_panel("")


class BatterArea(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.batterId = None

        self.n = QLabel()

        self.name = QLabel()
        self.name.setFixedWidth(200)
        font = QFont("Serif", 12)
        font.setBold(True)
        self.name.setFont(font)

        self.ab = FloatComponent("AB")
        self.r = IntComponent('R')
        self.hr = IntComponent("HR")
        self.rbi = IntComponent("RBI")
        self.sb = IntComponent("SB")
        self.avg = FloatComponent("AVG", 3)
        self.obp = FloatComponent("OBP", 3)
        self.slg = FloatComponent("SLG", 3)

        layout = QHBoxLayout()
        layout.addWidget(self.n)
        layout.addWidget(self.name, 1)
        layout.addWidget(self.ab)
        layout.addWidget(self.r)
        layout.addWidget(self.hr)
        layout.addWidget(self.rbi)
        layout.addWidget(self.sb)
        layout.addWidget(self.avg)
        layout.addWidget(self.obp)
        layout.addWidget(self.slg)

        self.setLayout(layout)


    def set_batter(self, batter):
        self.batterId = batter[0]
        self.name.setText(f"{batter[1]} {batter[3]}   {batter[2]}")


    def set_stats(self, session, timeFrame, awayHome):
        store = BatterStore()
        metrics = AnalyticsStore()
        analytics = {}
        for metric in ("r", "hr", "rbi", "sb", "avg", "obp", "slg"):
            analytics[metric] = metrics.get_league_metrics("MLB", timeFrame, awayHome, "player", metric, session)
        stats = store.get_batter_stats(self.batterId, timeFrame, awayHome, session)
        if stats:
            self.ab.set_panel(stats["ab"])
            self.r.set_panel(stats['r'], analytics['r'])
            self.hr.set_panel(stats['hr'], analytics['hr'])
            self.rbi.set_panel(stats['rbi'], analytics['rbi'])
            self.sb.set_panel(stats['sb'], analytics['sb'])
            self.avg.set_panel(stats['avg'], analytics['avg'])
            self.obp.set_panel(stats['obp'], analytics['obp'])
            self.slg.set_panel(stats['slg'], analytics['slg'])


    def clear_batter(self):
        self.batterId = None
        self.name.setText("")
        self.ab.set_panel('')
        self.r.set_panel('')
        self.hr.set_panel('')
        self.rbi.set_panel('')
        self.sb.set_panel('')
        self.avg.set_panel('')
        self.obp.set_panel('')
        self.slg.set_panel('')


class BattingOrderArea(QWidget):
    def __init__(self):
        super().__init__()

        self.batters = []

        scrollLayout = QVBoxLayout()
        self.setLayout(scrollLayout)

        # Populate the scroll panel with ThumbPanel widgets
        for i in range(9):
            batterPanel = BatterArea(self)
            batterPanel.n.setText(str(i+1))
            scrollLayout.addWidget(batterPanel)
            self.batters.append(batterPanel)


    def set_lineup(self, battOrder):
        self.clear_lineup()
        if battOrder:
            for player, batter in zip(battOrder, self.batters):
                batter.set_batter(player)


    def set_stats(self, session, timeFrame, awayHome):
        for batter in self.batters:
            batter.set_stats(session, timeFrame, awayHome)


    def clear_lineup(self):
        for batter in self.batters:
            batter.clear_batter()












