import pandas as pd
from typing import List, Any 
from pprint import pprint 

from .analytics import Analytics, get_db_session

from fefelson_sports.database.stores.analytics import AnalyticsStore
from fefelson_sports.database.stores.football import TeamStatStore

class FootballAnalytics(Analytics):

    _gameMinutes = 60

    def __init__(self, leagueId):
        super().__init__(leagueId)


    def _fetch_team_stats(self) -> pd.DataFrame:
        with get_db_session() as session:
            # 1. Main team stats (unchanged - already team-level, correct)
            query = f""" 
                SELECT g.game_id, g.home_id, g.away_id, fts.team_id, fts.opp_id, game_date,
                        fts.pts AS off_pts, 
                        fts.pass_plays AS off_pass_plays,
                        fts.pass_yards AS off_pass_yards, 
                        fts.rush_plays AS off_rush_plays,
                        fts.rush_yards AS off_rush_yards, 
                        fts.penalty_yards AS off_penalty_yards, 
                        fts.int_thrown + fts.fum_lost AS off_turns, 
                        fts.third_att AS off_third_att,
                        fts.third_conv AS off_third_conv, 
                        fts.fourth_att AS off_fourth_att,
                        fts.fourth_conv AS off_fourth_conv,

                        opp_fts.pts AS def_pts, 
                        opp_fts.pass_plays AS def_pass_plays,
                        opp_fts.pass_yards AS def_pass_yards, 
                        opp_fts.rush_plays AS def_rush_plays,
                        opp_fts.rush_yards AS def_rush_yards, 
                        opp_fts.penalty_yards AS def_penalty_yards, 
                        opp_fts.int_thrown + opp_fts.fum_lost AS def_turns, 
                        opp_fts.third_att AS def_third_att,
                        opp_fts.third_conv AS def_third_conv, 
                        opp_fts.fourth_att AS def_fourth_att,
                        opp_fts.fourth_conv AS def_fourth_conv

                FROM football_team_stats AS fts
                INNER JOIN football_team_stats AS opp_fts 
                    ON fts.game_id = opp_fts.game_id AND fts.team_id = opp_fts.opp_id
                INNER JOIN games AS g ON fts.game_id = g.game_id
                WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
            """
            result = pd.read_sql(query, session.bind)

            # 2. Passing + Rushing TDs - FIXED: separate queries, no cross-join
            # Offensive TDs
            query_off_td = f"""
                SELECT p.game_id, p.team_id,
                    SUM(p.pass_att) AS off_pass_att,
                    SUM(p.pass_comp) AS off_pass_comp,
                    SUM(p.pass_td) AS off_pass_td,
                    SUM(ABS(p.sack_yds_lost)) AS off_sack_yds_lost

                FROM passing p
                INNER JOIN games g ON p.game_id = g.game_id
                WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                GROUP BY p.game_id, p.team_id
                ORDER BY p.game_id
            """
            off_pass = pd.read_sql(query_off_td, session.bind)

            # Defensive TDs (allowed = opponent's offensive)
            query_def_td = f"""
                SELECT opp_p.game_id, opp_p.opp_id AS team_id,
                    SUM(opp_p.pass_att) AS def_pass_att,
                    SUM(opp_p.pass_comp) AS def_pass_comp,
                    SUM(opp_p.pass_td) AS def_pass_td,
                    SUM(ABS(opp_p.sack_yds_lost)) AS def_sack_yds_lost
                    
                FROM passing opp_p
                INNER JOIN games g ON opp_p.game_id = g.game_id
                WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                GROUP BY opp_p.game_id, opp_p.opp_id
            """
            def_pass = pd.read_sql(query_def_td, session.bind)

            # 2. Rushing TDs - FIXED: separate queries, no cross-join
            # Offensive TDs
            query_off_rush_td = f"""
                SELECT r.game_id, r.team_id,
                    SUM(r.rush_td) AS off_rush_td
                FROM rushing r
                INNER JOIN games g ON r.game_id = g.game_id
                WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                GROUP BY r.game_id, r.team_id
                ORDER BY r.game_id
            """
            off_rush = pd.read_sql(query_off_rush_td, session.bind)

            # Defensive Rush TDs (allowed = opponent's offensive)
            query_def_rush_td = f"""
                SELECT opp_r.game_id, opp_r.opp_id AS team_id,
                    SUM(opp_r.rush_td) AS def_rush_td
                FROM rushing opp_r
                INNER JOIN games g ON opp_r.game_id = g.game_id
                WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                GROUP BY opp_r.game_id, opp_r.opp_id
            """
            def_rush = pd.read_sql(query_def_rush_td, session.bind)

            # 3. Defender - Uses OPPONENTS STATS FOR OFFENSE
            query_off_defender = f"""
                SELECT opp_d.game_id, opp_d.opp_id AS team_id,
                    SUM(opp_d.pass_def) AS off_pass_def, 
                    SUM(opp_d.qb_hits) AS off_qb_hits,
                    SUM(opp_d.ints) AS off_pass_ints, 
                    SUM(opp_d.sacks) AS off_sacks

                FROM defense opp_d
                INNER JOIN games g ON opp_d.game_id = g.game_id
                WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                GROUP BY opp_d.game_id, opp_d.opp_id
            """
            off_defender = pd.read_sql(query_off_defender, session.bind)

            # Defensive Defenderss (allowed = opponent's offensive)
            query_def_defender = f"""
                SELECT d.game_id, d.team_id,
                    SUM(d.pass_def) AS def_pass_def, 
                    SUM(d.qb_hits) AS def_qb_hits,
                    SUM(d.ints) AS def_pass_ints, 
                    SUM(d.sacks) AS def_sacks

                FROM defense d
                INNER JOIN games g ON d.game_id = g.game_id
                WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                GROUP BY d.game_id, d.team_id
            """
            def_defender = pd.read_sql(query_def_defender, session.bind)


            # 3. Punts - FIXED: separate
            query_off_punts = f"""
                SELECT p.game_id, team_id, 
                    SUM(punts) AS off_punts,
                    SUM(punt_yds) AS off_punt_yards

                FROM punts p
                INNER JOIN games g ON p.game_id = g.game_id
                WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                GROUP BY p.game_id, team_id
            """
            off_punts = pd.read_sql(query_off_punts, session.bind)

            query_def_punts = f"""
                SELECT p.game_id, opp_id AS team_id, 
                    SUM(punts) AS def_punts,
                    SUM(punt_yds) AS def_punt_yards

                FROM punts p
                INNER JOIN games g ON p.game_id = g.game_id
                WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                GROUP BY p.game_id, opp_id
            """
            def_punts = pd.read_sql(query_def_punts, session.bind)

            # 4. Kick Returns - FIXED: separate
            query_off_kr = f"""
                SELECT kr.game_id, team_id, 
                        SUM(kr_yds) AS off_kr_yds,
                        SUM(pr_yds) AS off_pr_yds

                FROM kick_returns kr
                INNER JOIN games g ON kr.game_id = g.game_id
                WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                GROUP BY kr.game_id, team_id
            """
            off_kr = pd.read_sql(query_off_kr, session.bind)

            query_def_kr = f"""
                SELECT kr.game_id, opp_id AS team_id, 
                        SUM(kr_yds) AS def_kr_yds,
                        SUM(pr_yds) AS def_pr_yds

                FROM kick_returns kr
                INNER JOIN games g ON kr.game_id = g.game_id
                WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                GROUP BY kr.game_id, opp_id
            """
            def_kr = pd.read_sql(query_def_kr, session.bind)

            # 4. Field Goals - FIXED: separate
            query_off_fg = f"""
                SELECT k.game_id, team_id, SUM(fga) AS off_fga
                FROM kicks k
                INNER JOIN games g ON k.game_id = g.game_id
                WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                GROUP BY k.game_id, team_id
            """
            off_fg = pd.read_sql(query_off_fg, session.bind)

            query_def_fg = f"""
                SELECT k.game_id, opp_id AS team_id, SUM(fga) AS def_fga
                FROM kicks k
                INNER JOIN games g ON k.game_id = g.game_id
                WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                GROUP BY k.game_id, opp_id
            """
            def_fg = pd.read_sql(query_def_fg, session.bind)

            # 5. Merge all safely
            result = pd.merge(result, off_pass, how="left", on=["game_id", "team_id"])
            result = pd.merge(result, def_pass, how="left", on=["game_id", "team_id"])
            result = pd.merge(result, off_rush, how="left", on=["game_id", "team_id"])
            result = pd.merge(result, def_rush, how="left", on=["game_id", "team_id"])
            result = pd.merge(result, off_punts, how="left", on=["game_id", "team_id"])
            result = pd.merge(result, def_punts, how="left", on=["game_id", "team_id"])
            result = pd.merge(result, off_fg, how="left", on=["game_id", "team_id"])
            result = pd.merge(result, def_fg, how="left", on=["game_id", "team_id"])
            result = pd.merge(result, off_defender, how="left", on=["game_id", "team_id"])
            result = pd.merge(result, def_defender, how="left", on=["game_id", "team_id"])
            result = pd.merge(result, off_kr, how="left", on=["game_id", "team_id"])
            result = pd.merge(result, def_kr, how="left", on=["game_id", "team_id"])


            # Keep your other merges (defense, returns) if needed - they look okay

            # 6. Calculate drives
            drive_cols = [
                'off_pass_td', 'off_rush_td', 'off_turns', 'off_fga', 'off_punts',
                'off_fourth_att', 'off_fourth_conv',
                'def_pass_td', 'def_rush_td', 'def_turns', 'def_fga', 'def_punts',
                'def_fourth_att', 'def_fourth_conv'
            ]
            result[drive_cols] = result[drive_cols].fillna(0)

            result["off_drives"] = (
                result["off_pass_td"] + result["off_rush_td"] + result["off_turns"] +
                result["off_fga"] + result["off_punts"] +
                (result["off_fourth_att"] - result["off_fourth_conv"])
            ).astype(int)

            result["def_drives"] = (
                result["def_pass_td"] + result["def_rush_td"] + result["def_turns"] +
                result["def_fga"] + result["def_punts"] +
                (result["def_fourth_att"] - result["def_fourth_conv"])
            ).astype(int)

            return result


    def _pass_coverage(self, timeFrame, a_h, idType, entityType, dataFrame):
        metricLabel = "def_pass_cover"
        dataFrame = dataFrame.groupby(idType)[["def_pass_def", "def_pass_ints", "def_pass_att", "def_pass_comp", "def_pass_plays"]].apply(
                        lambda x: ((x["def_pass_def"].sum() + x['def_pass_ints'].sum()*3) / x['def_pass_plays'].sum()) - (x["def_pass_comp"].sum() / x["def_pass_att"].sum())
                    ).reset_index(name=metricLabel) 
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame)


    def _pass_protect(self, timeFrame, a_h, idType, entityType, dataFrame):
        metricLabel = "off_pass_protect"
        dataFrame = dataFrame.groupby(idType)[["off_sacks", "off_qb_hits", "off_pass_plays"]].apply(
                        lambda x: ((x["off_sacks"].sum()*2 + x['off_qb_hits'].sum()) / x['off_pass_plays'].sum()) *100
                    ).reset_index(name=metricLabel) 
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame, isMax=False)


    def _pass_rush(self, timeFrame, a_h, idType, entityType, dataFrame):
        metricLabel = "def_pass_rush"
        dataFrame = dataFrame.groupby(idType)[["def_sacks", "def_qb_hits", "def_pass_plays"]].apply(
                        lambda x: ((x["def_sacks"].sum()*2 + x['def_qb_hits'].sum()) / x['def_pass_plays'].sum()) *100
                    ).reset_index(name=metricLabel) 
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame)


    def _kick_return(self, timeFrame, a_h, idType, entityType, dataFrame, isMax=True):
        off_def = "off" if isMax else "def"
        metricLabel = f"{off_def}_return_yds"
        dataFrame = dataFrame.groupby(idType)[[f"{off_def}_kr_yds", f"{off_def}_pr_yds"]].apply(
                        lambda x: x[f"{off_def}_kr_yds"].median()  + x[f"{off_def}_pr_yds"].median()
                    ).reset_index(name=metricLabel) 
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame, isMax=isMax)


    def scheduled_analytics(self):
    
        super().scheduled_analytics()
        teamModels = self.scheduled_team_stats()


        for models in (teamModels,):
            self._store_models(models)

        
    def scheduled_team_stats(self):
        tableRecords = []
        teamStats = self._fetch_team_stats()
        for timeFrame, dataFrame in self._get_time_frames(teamStats):
            for a_h, dataFrame in self._get_away_home_frames(dataFrame):
                teams = super()._get_valid_group("team_id", dataFrame) 

                tableRecords.append(self._item_one_per_another(timeFrame, a_h, "off_pts", "off_drives", "off_pts", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another(timeFrame, a_h, "off_pass_yards", "off_drives", "off_pass_yards", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another(timeFrame, a_h, "off_rush_yards", "off_drives", "off_rush_yards", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another(timeFrame, a_h, "off_sack_yds_lost", "off_drives", "off_sack_yds_lost", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._item_one_per_another(timeFrame, a_h, "off_turns", "off_drives", "off_turns", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._item_one_per_another(timeFrame, a_h, "off_penalty_yards", "off_drives", "off_penalty_yards", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._item_per_sum(timeFrame, a_h, "off_pass_plays", "off_rush_plays", "off_pass_pct", "team_id", "team", teams)) 
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "off_third_conv", "off_third_att", "off_third_pct", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "off_fourth_conv", "off_fourth_att", "off_fourth_pct", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "off_pass_comp", "off_pass_att", "off_comp_pct", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another(timeFrame, a_h, "off_pass_yards", "off_pass_comp", "off_yards_per_comp", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another(timeFrame, a_h, "off_rush_yards", "off_rush_plays", "off_yards_per_car", "team_id", "team", teams))
                tableRecords.append(self._pass_protect(timeFrame, a_h, "team_id", "team", teams))
                tableRecords.append(self._kick_return(timeFrame, a_h, "team_id", "team", teams) )
                tableRecords.append(self._item_per_sum(timeFrame, a_h, "off_fourth_att", "off_fga", "off_go_pct", "team_id", "team", teams))
                

                tableRecords.append(self._item_one_per_another(timeFrame, a_h, "def_pts", "def_drives", "def_pts", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._item_one_per_another(timeFrame, a_h, "def_pass_yards", "def_drives", "def_pass_yards", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._item_one_per_another(timeFrame, a_h, "def_rush_yards", "def_drives", "def_rush_yards", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._item_one_per_another(timeFrame, a_h, "def_sack_yds_lost", "def_drives", "def_sack_yds_lost", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another(timeFrame, a_h, "def_turns", "def_drives", "def_turns", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another(timeFrame, a_h, "def_penalty_yards", "def_drives", "def_penalty_yards", "team_id", "team", teams))
                tableRecords.append(self._item_per_sum(timeFrame, a_h, "def_pass_plays", "def_rush_plays", "def_pass_pct", "team_id", "team", teams)) 
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "def_third_conv", "def_third_att", "def_third_pct", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "def_fourth_conv", "def_fourth_att", "def_fourth_pct", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "def_pass_comp", "def_pass_att", "def_comp_pct", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._item_one_per_another(timeFrame, a_h, "def_pass_yards", "def_pass_comp", "def_yards_per_comp", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another(timeFrame, a_h, "def_rush_yards", "def_rush_plays", "def_yards_per_car", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._pass_rush(timeFrame, a_h, "team_id", "team", teams))
                tableRecords.append(self._pass_coverage(timeFrame, a_h, "team_id", "team", teams))
                tableRecords.append(self._kick_return(timeFrame, a_h, "team_id", "team", teams, isMax=False)  )
                tableRecords.append(self._item_per_sum(timeFrame, a_h, "def_fourth_att", "def_fga", "def_go_pct", "team_id", "team", teams, isMax=False))
                


        return tableRecords  


    def _set_color(self, value, analytics):
        greaterThan = lambda v, a: v > a
        lessThan = lambda v, a: v < a

        colors = ["gold", "forestgreen", "springgreen", "palegoldenrod", "salmon", "red"]
        if analytics["best_value"] > analytics["worst_value"]:
            qList = ["q9", "q8", "q6", "q4", "q2", "q1"]
            func = greaterThan
        else:
            qList = ["q1", "q2", "q4", "q6", "q8", "q9"]
            func = lessThan

        barColor = "black"  # Default color
        for index, color in zip(qList, colors):
            if func(value, analytics[index]):
                barColor = color
                break
        return barColor

    def _set_score(self, value, analytics):
        greaterThan = lambda v, a: v > a
        lessThan = lambda v, a: v < a

        if analytics["best_value"] > analytics["worst_value"]:
            func = greaterThan
            oppFunc = lessThan
            analyticsDiff = analytics["best_value"] - analytics["worst_value"]
            teamDiff = analytics["best_value"] - value
            score = 0.03 if analyticsDiff == 0 else (analyticsDiff - teamDiff) / analyticsDiff + 0.03
        else:
            func = lessThan
            oppFunc = greaterThan
            analyticsDiff = analytics["worst_value"] - analytics["best_value"]
            teamDiff = value - analytics["best_value"]
            score = 0.03 if analyticsDiff == 0 else (analyticsDiff - teamDiff) / analyticsDiff + 0.03

        if func(value, analytics["best_value"]):
            score = 1
        elif oppFunc(value, analytics["worst_value"]):
            score = 0.03
        return score



    def website_stats(self):
        timeFrame = "1Month"
        awayHome = "all"

        query = f"""  
                    SELECT team_id FROM teams WHERE league_id = '{self.leagueId}'
                """
        store = TeamStatStore()
        metrics = AnalyticsStore()
        analytics = {}

        teamStats = []
        with get_db_session() as session:

            for key in ("pts", "comp_pct", "yards_per_comp", "yards_per_car", "time_of_poss", "third_pct",
                        "rush_yards", "pass_yards", "turns", "penalty_yards", "sack_yds_lost", "pass_pct"):
                for def_off in ("def", "off"):
                    metric = f"{def_off}_{key}" if key != 'time_of_poss' else key
                    analytics[metric] = metrics.get_league_metrics(self.leagueId, timeFrame, awayHome, "team", metric, session)

            analytics["def_pass_rush"] = metrics.get_league_metrics(self.leagueId, timeFrame, awayHome, "team", "def_pass_rush", session)
            analytics["def_pass_cover"] = metrics.get_league_metrics(self.leagueId, timeFrame, awayHome, "team", "def_pass_cover", session)
            analytics["off_pass_protect"] = metrics.get_league_metrics(self.leagueId, timeFrame, awayHome, "team", "off_pass_protect", session)
        
            teams = pd.read_sql(query, session.bind) 
            for x, y in teams.iterrows():
     
                stats = store.get_team_stats(y['team_id'], timeFrame, awayHome, session)
                if stats:
                    
                    for key in analytics:
                        stat = stats[key]
                        analytic = analytics[key]

                        temp = {"league":self.leagueId, "name": key, "teamId": int(y["team_id"]), "score": self._set_score(stat, analytic), "color": self._set_color(stat, analytic)}
                        teamStats.append(temp)
        return teamStats