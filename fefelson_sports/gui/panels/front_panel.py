from collections import defaultdict
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QScrollArea, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea


from ..components.label_components import FloatComponent, PctComponent
from ..components.logo_component import LogoComponent
from ..components.oppo_chart import OppositeChart
from ..components.string_components import (PlayDistComponent, CompPctComponent, CompPerComponent, PassProtectComponent,
                                            CarPerComponent, PassRushComponent, PassDefComponent, RushDefComponent)

from ...database.stores.analytics import AnalyticsStore
from ...database.stores.football import TeamStatStore
from ...database.stores.core import GameStore

from pprint import pprint


class FootballFrontPanel(QScrollArea):
    def __init__(self, leagueId, a_h):
        super().__init__()
        self.setWidgetResizable(True)
        scrollPanel = QWidget()
        scrollLayout = QHBoxLayout()
        scrollPanel.setLayout(scrollLayout)  
        self.setWidget(scrollPanel)

        self.leagueId = leagueId
        self.awayHome = a_h
        self.possTime = PctComponent("poss")
        self.oppList = QScrollArea()
        self.oppList.setFixedWidth(115)


        teamLabels = {}
        teamLabels["off"] = QLabel("TEAM")
        teamLabels["off"].setAlignment(Qt.AlignHCenter)

        teamLabels["def"] = QLabel("opponents")
        teamLabels["def"].setAlignment(Qt.AlignHCenter)

        self.tags = defaultdict(dict)
        self.tags["off"]["play_calling"] = PlayDistComponent()
        self.tags["off"]["pass_protect"] = PassProtectComponent()
        self.tags["off"]["comp_pct"] = CompPctComponent()
        self.tags["off"]["yards_per_comp"] = CompPerComponent()
        self.tags["off"]["yards_per_car"] = CarPerComponent()

        self.tags["def"]["def_pass_rush"] = PassRushComponent()
        self.tags["def"]["def_pass_cover"] = PassDefComponent()
        self.tags["def"]["def_rush_def"] = RushDefComponent()

        

        self.ptsChart = OppositeChart(scrollPanel, "points")
        self.rushChart = OppositeChart(scrollPanel, "rushing")
        self.passChart = OppositeChart(scrollPanel, "passing")
        self.sackChart = OppositeChart(scrollPanel, "sack yds lost")
        self.turnChart = OppositeChart(scrollPanel, "turnovers")
        self.penChart = OppositeChart(scrollPanel, "pen yards lost")

        tagLayout = QHBoxLayout()
        offenseLayout = QVBoxLayout()
        playLayout = QHBoxLayout()
        playLayout.addWidget(self.tags["off"]["play_calling"])
        playLayout.addWidget(self.tags["off"]["pass_protect"])
        offenseLayout.addLayout(playLayout)
        passLayout = QHBoxLayout()
        passLayout.addWidget(self.tags["off"]["comp_pct"])
        passLayout.addWidget(self.tags["off"]["yards_per_comp"])
        offenseLayout.addLayout(passLayout)
        offenseLayout.addWidget(self.tags["off"]["yards_per_car"])


        defenseLayout = QVBoxLayout()
        defenseLayout.addWidget(self.tags["def"]["def_pass_rush"])
        defenseLayout.addWidget(self.tags["def"]["def_pass_cover"])
        defenseLayout.addWidget(self.tags["def"]["def_rush_def"])

        tagLayout.addLayout(defenseLayout)
        tagLayout.addLayout(offenseLayout)


        titleLayout = QHBoxLayout()
        for def_off in ("def", 'off'):
            titleLayout.addWidget(teamLabels[def_off])           
        
        chartLayout = QVBoxLayout()
        chartLayout.addWidget(self.ptsChart)
        chartLayout.addWidget(self.rushChart)
        chartLayout.addWidget(self.passChart)
        chartLayout.addWidget(self.sackChart)
        chartLayout.addWidget(self.turnChart)
        chartLayout.addWidget(self.penChart)


        mainLayout = QVBoxLayout()
        mainLayout.addLayout(tagLayout, 0)
        mainLayout.addLayout(titleLayout, 0)
        mainLayout.addLayout(chartLayout, 1)        
        mainLayout.addStretch(1)

        oppLayout = QVBoxLayout()
        oppLayout.addWidget(self.possTime)
        oppLayout.addWidget(self.oppList, 1)

        if self.awayHome == "away":
            scrollLayout.addLayout(oppLayout)
            scrollLayout.addLayout(mainLayout, 1)
        else:
            scrollLayout.addLayout(mainLayout, 1)
            scrollLayout.addLayout(oppLayout)


    def set_team(self, team):
        self.teamId = team["team_id"]


    def set_stats(self, session, timeFrame, awayHome):
        store = TeamStatStore()
        metrics = AnalyticsStore()
        analytics = {}
        for key in ("pts", "comp_pct", "yards_per_comp", "yards_per_car", "time_of_poss",
                    "rush_yards", "pass_yards", "turns", "penalty_yards", "sack_yds_lost", "pass_pct"):
            for def_off in ("def", "off"):
                metric = f"{def_off}_{key}" if key != 'time_of_poss' else key
                analytics[metric] = metrics.get_league_metrics(self.leagueId, timeFrame, awayHome, "team", metric, session)

        analytics["def_pass_rush"] = metrics.get_league_metrics(self.leagueId, timeFrame, awayHome, "team", "def_pass_rush", session)
        analytics["def_pass_cover"] = metrics.get_league_metrics(self.leagueId, timeFrame, awayHome, "team", "def_pass_cover", session)
        analytics["off_pass_protect"] = metrics.get_league_metrics(self.leagueId, timeFrame, awayHome, "team", "off_pass_protect", session)
        
        
        stats = store.get_team_stats(self.teamId, timeFrame, awayHome, session)
        if stats:

            self.tags["off"]["play_calling"].set_panel(stats["off_pass_pct"], analytics["off_pass_pct"])
            self.tags["off"]["pass_protect"].set_panel(stats["off_pass_protect"], analytics["off_pass_protect"])
            self.tags["off"]["comp_pct"].set_panel(stats["off_comp_pct"], analytics["off_comp_pct"])
            self.tags["off"]["yards_per_comp"].set_panel(stats["off_yards_per_comp"], analytics["off_yards_per_comp"])
            self.tags["off"]["yards_per_car"].set_panel(stats["off_yards_per_car"], analytics["off_yards_per_car"])

            self.tags["def"]["def_pass_rush"].set_panel(stats["def_pass_rush"], analytics["def_pass_rush"])
            self.tags["def"]["def_pass_cover"].set_panel(stats["def_pass_cover"], analytics["def_pass_cover"])
            self.tags["def"]["def_rush_def"].set_panel(stats["def_yards_per_car"], analytics["def_yards_per_car"])


            pprint(analytics["time_of_poss"])
            self.possTime.set_panel(stats['time_of_poss'], analytics['time_of_poss'])
            self.ptsChart.set_panel_value("pts", stats, analytics)
            self.rushChart.set_panel_value("rush_yards", stats, analytics)
            self.passChart.set_panel_value("pass_yards", stats, analytics)
            self.turnChart.set_panel_value("turns", stats, analytics)
            self.penChart.set_panel_value("penalty_yards", stats, analytics)
            self.sackChart.set_panel_value("sack_yds_lost", stats, analytics)

        opps = GameStore().get_opps(timeFrame, awayHome, self.teamId, session)
        # Create a new widget for the scroll area
        scrollPanel = QWidget()
        scrollLayout = QVBoxLayout()
        scrollPanel.setLayout(scrollLayout)
        

        # Populate the scroll panel with ThumbPanel widgets
        for game in opps:
            thumbPanel = QWidget()
            label = QLabel(game[1])
            logo = LogoComponent(thumbPanel, 60)
            logo.set_logo(game[0])

            layout = QVBoxLayout()
            layout.addWidget(label)
            layout.addWidget(logo)
            thumbPanel.setLayout(layout)

            scrollLayout.addWidget(thumbPanel)

        # Add a stretch to push content to the top
        scrollLayout.addStretch(1)

        # Set the new widget in the scroll area
        self.oppList.setWidget(scrollPanel)
