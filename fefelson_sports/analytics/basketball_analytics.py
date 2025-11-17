import pandas as pd
from typing import List, Any 
from pprint import pprint 

from .analytics import Analytics, get_db_session

from fefelson_sports.database.stores.analytics import AnalyticsStore
from fefelson_sports.database.stores.basketball import TeamStatStore

class BasketballAnalytics(Analytics):

    def __init__(self, leagueId: str):
        super().__init__(leagueId)


    def _fetch_team_stats(self) -> pd.DataFrame:
         with get_db_session() as session:
            query = f""" 
                        SELECT g.game_id, home_id, away_id, bts.team_id, bts.opp_id, game_date, 
                                bts.minutes AS total_time,
                                bts.poss + opp_bts.poss AS pace,
                                
                                bts.poss AS off_poss,
                                bts.fga - bts.tpa AS off_2pa, 
                                bts.fga AS off_fga, 
                                bts.fta AS off_fta,
                                bts.tpa AS off_3pa,
                                bts.fgm - bts.tpm AS off_2pm, 
                                bts.fgm AS off_fgm,
                                bts.ftm AS off_ftm,
                                bts.tpm AS off_3pm,
                                bts.oreb AS off_oreb, 
                                bts.dreb AS off_dreb,
                                bts.pts AS off_pts,
                                bts.ast AS off_ast, 
                                bts.stl AS off_stl, 
                                bts.blk AS off_blk,
                                bts.turns AS off_turns,
                                bts.fouls AS off_fouls, 
                                bts.fb_pts AS off_fb_pts,
                                bts.pts_in_pt AS off_pts_in_pt,

                                opp_bts.poss AS def_poss,
                                opp_bts.fga - opp_bts.tpa AS def_2pa, 
                                opp_bts.fga AS def_fga, 
                                opp_bts.fta AS def_fta,
                                opp_bts.tpa AS def_3pa,
                                opp_bts.fgm - opp_bts.tpm AS def_2pm, 
                                opp_bts.fgm AS def_fgm,
                                opp_bts.ftm AS def_ftm,
                                opp_bts.tpm AS def_3pm,
                                opp_bts.oreb AS def_oreb, 
                                opp_bts.dreb AS def_dreb,
                                opp_bts.pts AS def_pts,
                                opp_bts.ast AS def_ast, 
                                opp_bts.stl AS def_stl, 
                                opp_bts.blk AS def_blk,
                                opp_bts.turns AS def_turns,
                                opp_bts.fouls AS def_fouls, 
                                opp_bts.fb_pts AS def_fb_pts,
                                opp_bts.pts_in_pt AS def_pts_in_pt

                        FROM basketball_team_stats AS bts
                        INNER JOIN basketball_team_stats AS opp_bts ON bts.game_id = opp_bts.game_id AND bts.team_id = opp_bts.opp_id
                        INNER JOIN games AS g ON bts.game_id = g.game_id
                        WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                    """
            
            result = pd.read_sql(query, session.bind) 

            clutch_two_query = f"""
                            SELECT g.game_id, team_id, 
                                    COUNT(g.game_id) AS off_clutch_2pa, 
                                    SUM(CASE WHEN shot_made THEN 1 ELSE 0 END) AS off_clutch_2pm

                            FROM basketball_shots AS bs
                            INNER JOIN games AS g ON bs.game_id = g.game_id
                            WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}' AND clutch = TRUE AND points = 2
                            GROUP BY g.game_id, team_id
                            """
            clutchTwoResult = pd.read_sql(clutch_two_query, session.bind)
            
            clutch_one_query = f"""
                            SELECT g.game_id, team_id, 
                                    COUNT(g.game_id) AS off_clutch_fta, 
                                    SUM(CASE WHEN shot_made THEN 1 ELSE 0 END) AS off_clutch_ftm

                            FROM basketball_shots AS bs
                            INNER JOIN games AS g ON bs.game_id = g.game_id
                            WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}' AND clutch = TRUE AND points = 1
                            GROUP BY g.game_id, team_id
                            """
            clutchFTResult = pd.read_sql(clutch_one_query, session.bind)
            
            clutch_three_query = f"""
                            SELECT g.game_id, team_id, 
                                    COUNT(g.game_id) AS off_clutch_3pa, 
                                    SUM(CASE WHEN shot_made THEN 1 ELSE 0 END) AS off_clutch_3pm

                            FROM basketball_shots AS bs
                            INNER JOIN games AS g ON bs.game_id = g.game_id
                            WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}' AND clutch = TRUE AND points = 3
                            GROUP BY g.game_id, team_id
                            """
            clutchThreeResult = pd.read_sql(clutch_three_query, session.bind)

            clutch_def_two_query = f"""
                            SELECT g.game_id, opp_id AS team_id, 
                                    COUNT(g.game_id) AS def_clutch_2pa, 
                                    SUM(CASE WHEN shot_made THEN 1 ELSE 0 END) AS def_clutch_2pm

                            FROM basketball_shots AS bs
                            INNER JOIN games AS g ON bs.game_id = g.game_id
                            WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}' AND clutch = TRUE AND points = 2
                            GROUP BY g.game_id, opp_id
                            """
            clutchDefTwoResult = pd.read_sql(clutch_def_two_query, session.bind)
            
            clutch_def_one_query = f"""
                            SELECT g.game_id, opp_id AS team_id, 
                                    COUNT(g.game_id) AS def_clutch_fta, 
                                    SUM(CASE WHEN shot_made THEN 1 ELSE 0 END) AS def_clutch_ftm

                            FROM basketball_shots AS bs
                            INNER JOIN games AS g ON bs.game_id = g.game_id
                            WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}' AND clutch = TRUE AND points = 1
                            GROUP BY g.game_id, opp_id
                            """
            clutchDefFTResult = pd.read_sql(clutch_def_one_query, session.bind)
            
            clutch_def_three_query = f"""
                            SELECT g.game_id, opp_id AS team_id, 
                                    COUNT(g.game_id) AS def_clutch_3pa, 
                                    SUM(CASE WHEN shot_made THEN 1 ELSE 0 END) AS def_clutch_3pm

                            FROM basketball_shots AS bs
                            INNER JOIN games AS g ON bs.game_id = g.game_id
                            WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}' AND clutch = TRUE AND points = 3
                            GROUP BY g.game_id, opp_id
                            """
            clutchDefThreeResult = pd.read_sql(clutch_def_three_query, session.bind)
            
            result = pd.merge(result, clutchTwoResult, how="left", on=["game_id", "team_id"])
            result = pd.merge(result, clutchFTResult, how="left", on=["game_id", "team_id"])
            result = pd.merge(result, clutchThreeResult, how="left", on=["game_id", "team_id"])
            result = pd.merge(result, clutchDefTwoResult, how="left", on=["game_id", "team_id"])
            result = pd.merge(result, clutchDefFTResult, how="left", on=["game_id", "team_id"])
            result = pd.merge(result, clutchDefThreeResult, how="left", on=["game_id", "team_id"])

            clutch_cols = [
                'off_clutch_2pa', 'off_clutch_2pm', 'off_clutch_3pa', 'off_clutch_3pm', 
                'off_clutch_fta', 'off_clutch_ftm',
                'def_clutch_2pa', 'def_clutch_2pm', 'def_clutch_3pa', 'def_clutch_3pm', 
                'def_clutch_fta', 'def_clutch_ftm',
            ]
            result[clutch_cols] = result[clutch_cols].fillna(0)

            result["off_clutch_pts"] = (
                result["off_clutch_2pm"]*2 + result["off_clutch_3pm"]*3 + result["off_clutch_fta"]
            ).astype(int)

            result["off_clutch_fga"] = (
                result["off_clutch_2pa"] + result["off_clutch_3pa"]
            ).astype(int)

            result["def_clutch_pts"] = (
                result["def_clutch_2pm"]*2 + result["def_clutch_3pm"]*3 + result["def_clutch_fta"]
            ).astype(int)

            result["def_clutch_fga"] = (
                result["def_clutch_2pa"] + result["def_clutch_3pa"]
            ).astype(int)

            return result


    
    def _set_net_ratings(self, timeFrame, a_h, dataFrame):
        
        teamRecords = []
        efficiency = {}
        for off_def in ("off", "def"):
            metricLabel = f"{off_def}_eff"
            
            efficiency[off_def] = dataFrame.groupby("team_id")[[f"{off_def}_pts", f"{off_def}_poss"]].apply(
                        lambda x: ((x[f"{off_def}_pts"] * 100) / x[f"{off_def}_poss"]).mean()
                    ).reset_index(name=metricLabel)
            
        # Merge the two DataFrames on team_id
        netRating = efficiency["off"].merge(efficiency["def"], left_on='team_id', right_on='team_id')
        # Calculate Net Rating
        netRating['net_rating'] = netRating['off_eff'] - netRating['def_eff']
        
        return self._item_function(timeFrame, a_h, "team", "net_rating", netRating)


    def _set_clutch_ts(self, timeFrame, a_h, dataFrame, isMax=True):
        off_def = "off" if isMax else "def"
        metricLabel = f"{off_def}_clutch_ts"
        dataFrame = dataFrame.groupby("team_id")[[f"{off_def}_clutch_fga", f"{off_def}_clutch_fta", f"{off_def}_clutch_pts"]].apply(
                        lambda x: (x[f"{off_def}_clutch_pts"].sum() / ( 2 * ( x[f"{off_def}_clutch_fga"].sum() + x[f"{off_def}_clutch_fta"].sum()*.44))) * 100
                    ).reset_index(name=metricLabel) 
        return self._item_function(timeFrame, a_h, "team", metricLabel, dataFrame, isMax=isMax)

    
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

                tableRecords.append(self._set_team_minute_adjusted(timeFrame, a_h, "pace", "total_time", teams))
                tableRecords.append(self._set_net_ratings(timeFrame, a_h, teams))

                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "off_pts", "off_poss", "off_eff", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "off_2pm", "off_2pa", "off_2p_pct", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "off_ftm", "off_poss", "off_ft_poss", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "off_3pm", "off_3pa", "off_3p_pct", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "off_ast", "off_fgm", "off_ast_pct", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "off_turns", "off_poss", "off_turn_pct", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._item_per_sum(timeFrame, a_h, "off_oreb", "def_dreb", "off_reb_pct", "team_id", "team", teams))
                tableRecords.append(self._item_per_sum(timeFrame, a_h, "off_2pa", "off_3pa", "off_2_or_3", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "off_fb_pts", "off_poss", "off_fb_pct", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "off_pts_in_pt", "off_poss", "off_pts_in_pt_pct", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "off_3pm", "off_poss", "off_3pm_pct", "team_id", "team", teams))
                tableRecords.append(self._set_clutch_ts(timeFrame, a_h, teams))

                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "def_pts", "def_poss", "def_eff", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "def_2pm", "def_2pa", "def_2p_pct", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "def_ftm", "def_poss", "def_ft_poss", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "def_3pm", "def_3pa", "def_3p_pct", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "def_ast", "def_fgm", "def_ast_pct", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "def_turns", "def_poss", "def_turn_pct", "team_id", "team", teams))
                tableRecords.append(self._item_per_sum(timeFrame, a_h, "off_dreb", "def_oreb", "def_reb_pct", "team_id", "team", teams))
                tableRecords.append(self._item_per_sum(timeFrame, a_h, "def_2pa", "def_3pa", "def_2_or_3", "team_id", "team", teams))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "def_fb_pts", "def_poss", "def_fb_pct", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "def_pts_in_pt", "def_poss", "def_pts_in_pt_pct", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._item_one_per_another_pct(timeFrame, a_h, "def_3pm", "def_poss", "def_3pm_pct", "team_id", "team", teams, isMax=False))
                tableRecords.append(self._set_clutch_ts(timeFrame, a_h, teams, isMax=False))

        return tableRecords





    # def _set_color(self, value, analytics):
    #     greaterThan = lambda v, a: v > a
    #     lessThan = lambda v, a: v < a

    #     colors = ["gold", "forestgreen", "springgreen", "palegoldenrod", "salmon", "red"]
    #     if analytics["best_value"] > analytics["worst_value"]:
    #         qList = ["q9", "q8", "q6", "q4", "q2", "q1"]
    #         func = greaterThan
    #     else:
    #         qList = ["q1", "q2", "q4", "q6", "q8", "q9"]
    #         func = lessThan

    #     barColor = "black"  # Default color
    #     for index, color in zip(qList, colors):
    #         if func(value, analytics[index]):
    #             barColor = color
    #             break
    #     return barColor

    # def _set_score(self, value, analytics):
    #     greaterThan = lambda v, a: v > a
    #     lessThan = lambda v, a: v < a

    #     if analytics["best_value"] > analytics["worst_value"]:
    #         func = greaterThan
    #         oppFunc = lessThan
    #         analyticsDiff = analytics["best_value"] - analytics["worst_value"]
    #         teamDiff = analytics["best_value"] - value
    #         score = 0.03 if analyticsDiff == 0 else (analyticsDiff - teamDiff) / analyticsDiff + 0.03
    #     else:
    #         func = lessThan
    #         oppFunc = greaterThan
    #         analyticsDiff = analytics["worst_value"] - analytics["best_value"]
    #         teamDiff = value - analytics["best_value"]
    #         score = 0.03 if analyticsDiff == 0 else (analyticsDiff - teamDiff) / analyticsDiff + 0.03

    #     if func(value, analytics["best_value"]):
    #         score = 1
    #     elif oppFunc(value, analytics["worst_value"]):
    #         score = 0.03
    #     return score



    # def website_stats(self):
    #     timeFrame = "1Month"
    #     awayHome = "all"

    #     query = f"""  
    #                 SELECT team_id FROM teams WHERE league_id = '{self.leagueId}'
    #             """
    #     store = TeamStatStore()
    #     metrics = AnalyticsStore()
    #     analytics = {}

    #     teamStats = []
    #     with get_db_session() as session:

    #         for key in ("pts", "comp_pct", "yards_per_comp", "yards_per_car", "time_of_poss", "third_pct",
    #                     "rush_yards", "pass_yards", "turns", "penalty_yards", "sack_yds_lost", "pass_pct"):
    #             for def_off in ("def", "off"):
    #                 metric = f"{def_off}_{key}" if key != 'time_of_poss' else key
    #                 analytics[metric] = metrics.get_league_metrics(self.leagueId, timeFrame, awayHome, "team", metric, session)

    #         analytics["def_pass_rush"] = metrics.get_league_metrics(self.leagueId, timeFrame, awayHome, "team", "def_pass_rush", session)
    #         analytics["def_pass_cover"] = metrics.get_league_metrics(self.leagueId, timeFrame, awayHome, "team", "def_pass_cover", session)
    #         analytics["off_pass_protect"] = metrics.get_league_metrics(self.leagueId, timeFrame, awayHome, "team", "off_pass_protect", session)
        
    #         teams = pd.read_sql(query, session.bind) 
    #         for x, y in teams.iterrows():
     
    #             stats = store.get_team_stats(y['team_id'], timeFrame, awayHome, session)
    #             if stats:
                    
    #                 for key in analytics:
    #                     stat = stats[key]
    #                     analytic = analytics[key]

    #                     temp = {"league":self.leagueId, "name": key, "teamId": int(y["team_id"]), "score": self._set_score(stat, analytic), "color": self._set_color(stat, analytic)}
    #                     teamStats.append(temp)
    #     return teamStats