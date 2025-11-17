from collections import defaultdict
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QScrollArea, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea


from ..components.label_components import FloatComponent, PctComponent
from ..components.logo_component import LogoComponent
from ..components.oppo_chart import OppositeChart
from ..components.string_components import (PaceComponent, ShotPctComponent, B2BComponent)

from ...database.stores.analytics import AnalyticsStore
from ...database.stores.basketball import TeamStatStore
from ...database.stores.core import GameStore

from pprint import pprint


class BasketballFrontPanel(QScrollArea):
    def __init__(self, leagueId, a_h):
        super().__init__()
        self.setWidgetResizable(True)
        scrollPanel = QWidget()
        scrollLayout = QHBoxLayout()
        scrollPanel.setLayout(scrollLayout)  
        self.setWidget(scrollPanel)

        self.leagueId = leagueId
        self.awayHome = a_h
        self.oppList = QScrollArea()
        self.oppList.setFixedWidth(115)

        teamLabels = {}
        teamLabels["off"] = QLabel("TEAM")
        teamLabels["off"].setAlignment(Qt.AlignHCenter)

        teamLabels["def"] = QLabel("opponents")
        teamLabels["def"].setAlignment(Qt.AlignHCenter)

        self.tags = defaultdict(dict)
        self.tags["b2b"] = B2BComponent()
        self.tags["b2b"].hide()
        self.tags["off"]["pace"] = PaceComponent()
        self.tags["off"]["2_or_3"] = ShotPctComponent()
        self.tags["off"]["clutch_ft"] = PctComponent("clutch ft%")

        self.tags["def"]["2_or_3"] = ShotPctComponent("maroon")


        

        self.ptsChart = OppositeChart(scrollPanel, "points")
        self.paintChart = OppositeChart(scrollPanel, "paint")
        self.ftmChart = OppositeChart(scrollPanel, "FTM")
        self.tpmChart = OppositeChart(scrollPanel, "3PM")
        self.turnChart = OppositeChart(scrollPanel, "turnovers")
        self.rebChart = OppositeChart(scrollPanel, "rebounds")
        self.fbChart = OppositeChart(scrollPanel, "fast break")
        self.clutchChart = OppositeChart(scrollPanel, "clutch")



        topLayout = QHBoxLayout()
        topLayout.addWidget(self.tags["b2b"], 1)
        topLayout.addWidget(self.tags["off"]["pace"], 3)
        
        offenseLayout = QVBoxLayout()        
        offenseLayout.addWidget(self.tags["off"]["2_or_3"])
        offenseLayout.addWidget(self.tags["off"]["clutch_ft"])
        
        defenseLayout = QVBoxLayout()
        defenseLayout.addWidget(self.tags["def"]["2_or_3"])

        bottomLayout = QHBoxLayout()
        bottomLayout.addLayout(defenseLayout)
        bottomLayout.addLayout(offenseLayout)


        tagLayout = QVBoxLayout()
        tagLayout.addLayout(topLayout)
        tagLayout.addLayout(bottomLayout)
        


        titleLayout = QHBoxLayout()
        for def_off in ("def", 'off'):
            titleLayout.addWidget(teamLabels[def_off])           
        
        chartLayout = QVBoxLayout()
        chartLayout.addWidget(self.ptsChart)
        chartLayout.addWidget(self.rebChart)
        chartLayout.addWidget(self.turnChart)
        chartLayout.addWidget(self.clutchChart)
        chartLayout.addWidget(self.tpmChart)
        chartLayout.addWidget(self.paintChart)
        chartLayout.addWidget(self.fbChart)
        chartLayout.addWidget(self.ftmChart)
        
        


        mainLayout = QVBoxLayout()
        mainLayout.addLayout(tagLayout, 0)
        mainLayout.addLayout(titleLayout, 0)
        mainLayout.addLayout(chartLayout, 1)        
        mainLayout.addStretch(1)

        oppLayout = QVBoxLayout()
        oppLayout.addWidget(self.oppList, 1)

        if self.awayHome == "away":
            scrollLayout.addLayout(oppLayout)
            scrollLayout.addLayout(mainLayout, 1)
        else:
            scrollLayout.addLayout(mainLayout, 1)
            scrollLayout.addLayout(oppLayout)


    def set_team(self, team):
        self.teamId = team["team_id"]


    def clear(self):
        self.tags["off"]["pace"].clear()
        self.tags["off"]["2_or_3"].clear()
        self.tags["off"]["clutch_ft"].clear()

        self.tags["def"]["2_or_3"].clear()

        self.ptsChart.clear()
        self.paintChart.clear()
        self.ftmChart.clear()
        self.turnChart.clear()
        self.tpmChart.clear()
        self.rebChart.clear()
        self.fbChart.clear()
        self.clutchChart.clear()



    def set_stats(self, session, timeFrame, awayHome):
        self.clear()
        store = TeamStatStore()
        metrics = AnalyticsStore()
        analytics = {}
        awayHome = awayHome if awayHome == "all" else self.awayHome
        
        self.tags["b2b"].hide()
        if store.get_b2b(self.teamId, session):
            self.tags["b2b"].show()
        
        for key in ("eff", "2p_pct", "ft_poss", "3p_pct","3pm_pct", "pts_in_pt_pct",
                    "ast_pct", "turn_pct", "reb_pct", '2_or_3', "fb_pct", "clutch_ts"):
            for def_off in ("def", "off"):
                metric = f"{def_off}_{key}"
                analytics[metric] = metrics.get_league_metrics(self.leagueId, timeFrame, awayHome, "team", metric, session)
        analytics["pace"] = metrics.get_league_metrics(self.leagueId, timeFrame, awayHome, "team", "pace", session)
        
        stats = store.get_team_stats(self.teamId, timeFrame, awayHome, session)
        if stats:
            self.tags["off"]["pace"].set_panel(stats["pace"], analytics["pace"])
            self.tags["off"]["2_or_3"].set_panel(stats["off_2_or_3"], analytics["off_2_or_3"])
            self.tags["off"]["clutch_ft"].set_panel(stats["off_clutch_ft"])
            # self.tags["off"]["comp_pct"].set_panel(stats["off_comp_pct"], analytics["off_comp_pct"])
            # self.tags["off"]["yards_per_comp"].set_panel(stats["off_yards_per_comp"], analytics["off_yards_per_comp"])
            # self.tags["off"]["yards_per_car"].set_panel(stats["off_yards_per_car"], analytics["off_yards_per_car"])
            # self.tags["off"]["third_pct"].set_panel(stats["off_third_pct"], analytics["off_third_pct"])

            self.tags["def"]["2_or_3"].set_panel(stats["def_2_or_3"], analytics["def_2_or_3"])
            # self.tags["def"]["def_pass_cover"].set_panel(stats["def_pass_cover"], analytics["def_pass_cover"])
            # self.tags["def"]["def_rush_def"].set_panel(stats["def_yards_per_car"], analytics["def_yards_per_car"])
            # self.tags["def"]["third_pct"].set_panel(stats["def_third_pct"], analytics["def_third_pct"])

            # self.possTime.set_panel(stats['time_of_poss'], analytics['time_of_poss'])
            self.ptsChart.set_panel_value("eff", stats, analytics)
            self.paintChart.set_panel_value("pts_in_pt_pct", stats, analytics)
            self.ftmChart.set_panel_value("ft_poss", stats, analytics)
            self.turnChart.set_panel_value("turn_pct", stats, analytics)
            self.tpmChart.set_panel_value("3pm_pct", stats, analytics)
            self.rebChart.set_panel_value("reb_pct", stats, analytics)
            self.fbChart.set_panel_value("fb_pct", stats, analytics)
            self.clutchChart.set_panel_value("clutch_ts", stats, analytics)

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
 