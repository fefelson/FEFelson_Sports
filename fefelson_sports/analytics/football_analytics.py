import pandas as pd
from typing import List, Any 
from pprint import pprint 

from .analytics import Analytics, get_db_session

class FootballAnalytics(Analytics):

    _gameMinutes = 60

    def __init__(self, leagueId):
        super().__init__(leagueId)


    def _fetch_team_stats(self) -> pd.DataFrame:
        with get_db_session() as session:
            query = f""" 
                        SELECT g.game_id, g.home_id, g.away_id, fts.team_id, fts.opp_id, game_date,
                                CASE WHEN fts.time_of_poss + opp_fts.time_of_poss < 60 THEN 60 ELSE fts.time_of_poss + opp_fts.time_of_poss END AS total_time,
                                fts.pts AS off_pts, fts.drives AS off_drives, fts.pass_plays AS off_pass_plays,
                                fts.pass_yards AS off_pass_yards, fts.rush_plays AS off_rush_plays,
                                fts.rush_yards AS off_rush_yards, fts.penalties AS off_penalties, 
                                fts.penalty_yards AS off_penalty_yards, fts.time_of_poss AS off_time_of_poss,
                                fts.int_thrown + fts.fum_lost AS off_turns, 
                                fts.sack_yds_lost AS off_sack_yds_lost, fts.third_att AS off_third_att,
                                fts.third_conv AS off_third_conv, fts.fourth_att AS off_fourth_att,
                                fts.fourth_conv As off_fourth_conv,

                                opp_fts.pts AS def_pts, opp_fts.drives AS def_drives, opp_fts.pass_plays AS def_pass_plays,
                                opp_fts.pass_yards AS def_pass_yards, opp_fts.rush_plays AS def_rush_plays,
                                opp_fts.rush_yards AS def_rush_yards, opp_fts.penalties AS def_penalties, 
                                opp_fts.penalty_yards AS def_penalty_yards, opp_fts.time_of_poss AS def_time_of_poss,
                                opp_fts.int_thrown + opp_fts.fum_lost AS def_turns, 
                                opp_fts.sack_yds_lost AS def_sack_yds_lost, opp_fts.third_att AS def_third_att,
                                opp_fts.third_conv AS def_third_conv, opp_fts.fourth_att AS def_fourth_att,
                                opp_fts.fourth_conv As def_fourth_conv

                        FROM football_team_stats AS fts
                        INNER JOIN football_team_stats AS opp_fts ON fts.game_id = opp_fts.game_id AND fts.team_id = opp_fts.opp_id
                        INNER JOIN games AS g ON fts.game_id = g.game_id
                        WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                    """
            result = pd.read_sql(query, session.bind) 

            query = f""" 
                    SELECT g.game_id, p.team_id,
                        SUM(p.pass_att) AS off_pass_att, SUM(p.pass_comp) AS off_pass_comp,
                        SUM(opp_p.pass_att) AS def_pass_att, SUM(opp_p.pass_comp) AS def_pass_comp

                    FROM passing AS p
                    INNER JOIN passing AS opp_p ON p.game_id = opp_p.game_id AND p.team_id = opp_p.opp_id
                    INNER JOIN games AS g ON p.game_id = g.game_id
                    INNER JOIN leagues AS l ON g.league_id = l.league_id
                    WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                    GROUP BY g.game_id, p.team_id
                """
            passResult =  pd.read_sql(query, session.bind) 
            result = pd.merge(result, passResult, how="left", on=["game_id", "team_id"])

            query = f""" 
                    SELECT g.game_id, d.team_id,

                        SUM(opp_d.pass_def) AS off_pass_def, SUM(opp_d.qb_hits) AS off_qb_hits,
                        SUM(opp_d.ints) AS off_pass_ints, SUM(opp_d.sacks) AS off_sacks,

                        SUM(d.pass_def) AS def_pass_def, SUM(d.qb_hits) AS def_qb_hits,
                        SUM(d.ints) AS def_pass_ints, SUM(d.sacks) AS def_sacks

                    FROM defense AS d
                    INNER JOIN defense AS opp_d ON d.game_id = opp_d.game_id AND d.team_id = opp_d.opp_id
                    INNER JOIN games AS g ON d.game_id = g.game_id
                    INNER JOIN leagues AS l ON g.league_id = l.league_id
                    WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                    GROUP BY g.game_id, d.team_id
                """
            defResult =  pd.read_sql(query, session.bind) 
            result = pd.merge(result, defResult, how="left", on=["game_id", "team_id"])
            return result


    def _pass_coverage(self, timeFrame, a_h, idType, entityType, dataFrame):
        metricLabel = "def_pass_cover"
        dataFrame = dataFrame.groupby(idType)[["def_pass_def", "def_pass_ints", "def_pass_att", "def_pass_comp", "def_pass_plays"]].apply(
                        lambda x: ((x["def_pass_def"].sum() + x['def_pass_ints'].sum()) / x['def_pass_plays'].sum()) - (x["def_pass_comp"].sum() / x["def_pass_att"].sum())
                    ).reset_index(name=metricLabel) 
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame)


    def _pass_protect(self, timeFrame, a_h, idType, entityType, dataFrame):
        metricLabel = "off_pass_protect"
        dataFrame = dataFrame.groupby(idType)[["off_sacks", "off_qb_hits", "off_pass_plays"]].apply(
                        lambda x: ((x["off_sacks"].sum() + x['off_qb_hits'].sum()) / x['off_pass_plays'].sum()) *100
                    ).reset_index(name=metricLabel) 
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame)


    def _pass_rush(self, timeFrame, a_h, idType, entityType, dataFrame):
        metricLabel = "def_pass_rush"
        dataFrame = dataFrame.groupby(idType)[["def_sacks", "def_qb_hits", "def_pass_plays"]].apply(
                        lambda x: ((x["def_sacks"].sum() + x['def_qb_hits'].sum()) / x['def_pass_plays'].sum()) *100
                    ).reset_index(name=metricLabel) 
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame)


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
                    
                [tableRecords.append(x) for x in self._set_team_minute_adjusted(timeFrame, a_h, "off_pts", "total_time", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._item_per_sum(timeFrame, a_h, "off_pass_plays", "off_rush_plays", "off_pass_pct", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._item_one_per_another_pct(timeFrame, a_h, "off_time_of_poss", "total_time", "time_of_poss", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._set_team_minute_adjusted(timeFrame, a_h, "off_pass_yards", "total_time", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._set_team_minute_adjusted(timeFrame, a_h, "off_rush_yards", "total_time", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._set_team_minute_adjusted(timeFrame, a_h, "off_sack_yds_lost", "total_time", "team_id", "team", teams, isMax=False)]
                [tableRecords.append(x) for x in self._set_team_minute_adjusted(timeFrame, a_h, "off_turns", "total_time", "team_id", "team", teams, isMax=False)]
                [tableRecords.append(x) for x in self._set_team_minute_adjusted(timeFrame, a_h, "off_penalty_yards", "total_time", "team_id", "team", teams, isMax=False)]
                [tableRecords.append(x) for x in self._item_one_per_another_pct(timeFrame, a_h, "off_third_conv", "off_third_att", "off_third_pct", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._item_one_per_another_pct(timeFrame, a_h, "off_fourth_conv", "off_fourth_att", "off_fourth_pct", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._item_one_per_another_pct(timeFrame, a_h, "off_pass_comp", "off_pass_att", "off_comp_pct", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._item_one_per_another(timeFrame, a_h, "off_pass_yards", "off_pass_comp", "off_yards_per_comp", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._item_one_per_another(timeFrame, a_h, "off_rush_yards", "off_rush_plays", "off_yards_per_car", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._pass_protect(timeFrame, a_h, "team_id", "team", teams)]


                [tableRecords.append(x) for x in self._set_team_minute_adjusted(timeFrame, a_h, "def_pts", "total_time", "team_id", "team", teams, isMax=False)]
                [tableRecords.append(x) for x in self._item_per_sum(timeFrame, a_h, "def_pass_plays", "def_rush_plays", "def_pass_pct", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._set_team_minute_adjusted(timeFrame, a_h, "def_pass_yards", "total_time", "team_id", "team", teams, isMax=False)]
                [tableRecords.append(x) for x in self._set_team_minute_adjusted(timeFrame, a_h, "def_rush_yards", "total_time", "team_id", "team", teams, isMax=False)]
                [tableRecords.append(x) for x in self._set_team_minute_adjusted(timeFrame, a_h, "def_sack_yds_lost", "total_time", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._set_team_minute_adjusted(timeFrame, a_h, "def_turns", "total_time", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._set_team_minute_adjusted(timeFrame, a_h, "def_penalty_yards", "total_time", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._item_one_per_another_pct(timeFrame, a_h, "def_third_conv", "def_third_att", "def_third_pct", "team_id", "team", teams, isMax=False)]
                [tableRecords.append(x) for x in self._item_one_per_another_pct(timeFrame, a_h, "def_fourth_conv", "def_fourth_att", "def_fourth_pct", "team_id", "team", teams, isMax=False)]
                [tableRecords.append(x) for x in self._item_one_per_another_pct(timeFrame, a_h, "def_pass_comp", "def_pass_att", "def_comp_pct", "team_id", "team", teams, isMax=False)]
                [tableRecords.append(x) for x in self._item_one_per_another(timeFrame, a_h, "def_pass_yards", "def_pass_comp", "def_yards_per_comp", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._item_one_per_another(timeFrame, a_h, "def_rush_yards", "def_rush_plays", "def_yards_per_car", "team_id", "team", teams, isMax=False)]
                [tableRecords.append(x) for x in self._pass_rush(timeFrame, a_h, "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._pass_coverage(timeFrame, a_h, "team_id", "team", teams)]
                


        return tableRecords  

