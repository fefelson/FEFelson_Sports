import pandas as pd
from typing import List, Any 
from pprint import pprint 

from .analytics import Analytics, get_db_session

class MLBAnalytics(Analytics):

    def __init__(self):
        super().__init__("MLB") 


    def _era(self, timeFrame, a_h, idType, entityType, dataFrame):
        metricLabel = "era"
        dataFrame = dataFrame.groupby(idType)[["er", "full_ip", "partial_ip"]].apply(
                        lambda x:  (x['er'].sum() * 9) / (x["full_ip"].sum() + x["partial_ip"].sum() / 3)
                    ).reset_index(name=metricLabel) 
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame, False)


    def _fetch_batter_stats(self) -> pd.DataFrame:
        with get_db_session() as session:
             query = f""" 
                        SELECT g.game_id, g.away_id, g.home_id, bs.team_id, bs.opp_id, game_date, 
                                player_id, ab, bb, r, h, hr, rbi, sb 
                        FROM batting_stats AS bs
                        INNER JOIN games AS g ON bs.game_id = g.game_id
                        WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                    """
             bsResults = pd.read_sql(query, session.bind) 

             query = f""" 
                        SELECT ab.game_id, batter_id AS player_id, COALESCE(SUM(num_bases), 0) AS num_bases
                        FROM at_bats AS ab
                        INNER JOIN at_bat_types AS abt on ab.at_bat_type_id = abt.at_bat_type_id
                        INNER JOIN games AS g on ab.game_id = g.game_id
                        WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                        GROUP BY ab.game_id, batter_id
                    """
             abResults = pd.read_sql(query, session.bind) 
        return pd.merge(bsResults, abResults, how='left', on=['game_id', 'player_id'])


    def _fetch_starter_stats(self) -> pd.DataFrame:
        with get_db_session() as session:
            query = f""" 
                        SELECT g.game_id, g.away_id, g.home_id, ps.team_id, ps.opp_id, game_date, 
                                ps.player_id, w, l, sv, bba, ha, k, er, full_ip, partial_ip
                        FROM pitching_stats AS ps
                        INNER JOIN games AS g ON ps.game_id = g.game_id
                        INNER JOIN baseball_bullpen AS bb ON ps.game_id = bb.game_id AND ps.team_id = bb.team_id
                        WHERE g.season = {self.season} AND bb.pitch_order = 1 AND g.league_id = '{self.leagueId}'
                    """
            return pd.read_sql(query, session.bind) 


    def _fetch_bullpen_stats(self) -> pd.DataFrame:
        with get_db_session() as session:
            query = f""" 
                        SELECT g.game_id, g.away_id, g.home_id, ps.team_id, ps.opp_id, game_date, 
                                ps.player_id, w, l, sv, bba, ha, k, er, full_ip, partial_ip
                        FROM pitching_stats AS ps
                        INNER JOIN games AS g ON ps.game_id = g.game_id
                        INNER JOIN baseball_bullpen AS bb ON ps.game_id = bb.game_id AND ps.player_id = bb.player_id
                        WHERE g.season = {self.season} AND bb.pitch_order > 1 AND g.league_id = '{self.leagueId}'
                    """
            return pd.read_sql(query, session.bind) 


    def _fetch_team_stats(self) -> pd.DataFrame:
        with get_db_session() as session:
             query = f""" 
                        SELECT g.game_id, g.home_id, g.away_id, bts.team_id, bts.opp_id, game_date, 
                                ab, bb, r, h, hr, rbi, sb, lob, errors,
                                full_ip, partial_ip, bba, ha, k, er
                        FROM baseball_team_stats AS bts
                        INNER JOIN games AS g ON bts.game_id = g.game_id
                        WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                    """
             bsResults = pd.read_sql(query, session.bind) 

             query = f""" 
                        SELECT ab.game_id, team_id, COALESCE(SUM(num_bases), 0) AS num_bases
                        FROM at_bats AS ab
                        INNER JOIN at_bat_types AS abt on ab.at_bat_type_id = abt.at_bat_type_id
                        INNER JOIN games AS g on ab.game_id = g.game_id
                        WHERE g.season = {self.season} AND g.league_id = '{self.leagueId}'
                        GROUP BY ab.game_id, team_id
                    """
             abResults = pd.read_sql(query, session.bind) 
        return pd.merge(bsResults, abResults, how='left', on=['game_id', 'team_id'])


    def _get_valid_group(self, entityId: str, metric, dataFrame: pd.DataFrame) -> pd.DataFrame:
        # Count the number of games per entity
        game_counts = dataFrame.groupby(entityId)[metric].sum().reset_index(name='metric_count')
        # Find the maximum game count
        max_games = game_counts['metric_count'].max()

        # Keep only entities that have at least 60% of the max game count
        valid_group = game_counts[game_counts['metric_count'] >= 0.6 * max_games]

        # Merge back with the original filtered dataset to only keep valid teams
        return dataFrame[dataFrame[entityId].isin(valid_group[entityId])]


    def _ip(self, timeFrame, a_h, idType, entityType, dataFrame, isMax=True):
        metricLabel = "ip"
        dataFrame = dataFrame.groupby(idType)[["partial_ip", "full_ip"]].apply(
                        lambda x: (x['full_ip'].sum() + x['partial_ip'].sum() / 3) 
                    ).reset_index(name=metricLabel) 
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame, isMax)


    def _k9(self, timeFrame, a_h, idType, entityType, dataFrame):
        metricLabel = "k9"
        dataFrame = dataFrame.groupby(idType)[["k", "full_ip", "partial_ip"]].apply(
                        lambda x:  (x['k'].sum() * 9)/(x["full_ip"].sum()+x["partial_ip"].sum()/3) 
                    ).reset_index(name=metricLabel) 
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame)


    def _lob(self, timeFrame, a_h, idType, entityType, dataFrame):
        metricLabel = "lob"
        dataFrame = dataFrame.groupby(idType)[["lob", "rbi",]].apply(
                        lambda x: (x["lob"].sum() / (x['lob'].sum() + x['rbi'].sum())) *100
                    ).reset_index(name=metricLabel) 
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame, False)


    def _obp(self, timeFrame, a_h, idType, entityType, dataFrame):
        metricLabel = "obp"
        dataFrame = dataFrame.groupby(idType)[["ab", "bb", "h"]].apply(
                        lambda x: (x["bb"].sum() + x['h'].sum()) / (x['ab'].sum() + x['bb'].sum())
                    ).reset_index(name=metricLabel) 
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame)


    def _whip(self, timeFrame, a_h, idType, entityType, dataFrame):
        metricLabel = "whip"
        dataFrame = dataFrame.groupby(idType)[["bba", "ha", "full_ip", "partial_ip"]].apply(
                        lambda x: (x["bba"].sum() + x['ha'].sum()) / (x["full_ip"].sum() + x["partial_ip"].sum() / 3)
                    ).reset_index(name=metricLabel) 
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame, isMax=False)


    def scheduled_analytics(self):
    
        super().scheduled_analytics()
        teamModels = self.scheduled_team_stats()
        teamBullpen = self.scheduled_team_bullpen_stats()
        starterModels = self.scheduled_starter_stats()
        # bullpenModels = self.scheduled_bullpen_stats()
        batterModels = self.scheduled_batter_stats()

        for models in (teamModels, teamBullpen, starterModels, batterModels):
            self._store_models(models)


    def scheduled_team_bullpen_stats(self):
        tableRecords = []
        teamStats = self._fetch_bullpen_stats()
        for timeFrame, dataFrame in self._get_time_frames(teamStats):
            for a_h, dataFrame in self._get_away_home_frames(dataFrame):
                teams = super()._get_valid_group("team_id", dataFrame)

                [tableRecords.append(x) for x in self._ip(timeFrame, a_h, "team_id", "bullpen", teams, isMax=False)]
                [tableRecords.append(x) for x in self._item_sum(timeFrame, a_h, "w", "team_id", "bullpen", teams)]
                [tableRecords.append(x) for x in self._item_sum(timeFrame, a_h, "l", "team_id", "bullpen", teams, isMax=False)]
                [tableRecords.append(x) for x in self._era(timeFrame, a_h, "team_id", "bullpen", teams)]
                [tableRecords.append(x) for x in self._whip(timeFrame, a_h, "team_id", "bullpen", teams)]
                [tableRecords.append(x) for x in self._k9(timeFrame, a_h, "team_id", "bullpen", teams)]
        return tableRecords 


    def scheduled_team_stats(self):
        tableRecords = []
        teamStats = self._fetch_team_stats()
        for timeFrame, dataFrame in self._get_time_frames(teamStats):
            for a_h, dataFrame in self._get_away_home_frames(dataFrame):
                teams = super()._get_valid_group("team_id", dataFrame)

                [tableRecords.append(x) for x in self._item_mean(timeFrame, a_h, "r", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._item_mean(timeFrame, a_h, "h", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._item_one_per_another(timeFrame, a_h, "ab", "hr", "hr", "team_id", "team", teams, isMax=False)]
                [tableRecords.append(x) for x in self._item_mean(timeFrame, a_h, "sb", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._item_per_sum(timeFrame, a_h, "lob", "rbi", "lob", "team_id", "team", teams, isMax=False)]
                [tableRecords.append(x) for x in self._item_one_per_another(timeFrame, a_h, "h", "ab", "avg", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._obp(timeFrame, a_h, "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._item_one_per_another(timeFrame, a_h, "num_bases", "ab", "slg", "team_id", "team", teams)]
                [tableRecords.append(x) for x in self._item_mean(timeFrame, a_h, "errors", "team_id", "team", teams, isMax=False)]

        return tableRecords   

    def scheduled_starter_stats(self):
        tableRecords = []
        pitcherStats = self._fetch_starter_stats()
        for timeFrame, dataFrame in self._get_time_frames(pitcherStats):
            for a_h, dataFrame in self._get_away_home_frames(dataFrame):
                starters = self._get_valid_group("player_id", "full_ip", dataFrame)

                [tableRecords.append(x) for x in self._ip(timeFrame, a_h, "player_id", "starter", starters, isMax=False)]
                [tableRecords.append(x) for x in self._item_sum(timeFrame, a_h, "w", "player_id", "starter", starters)]
                [tableRecords.append(x) for x in self._item_sum(timeFrame, a_h, "l", "player_id", "starter", starters, isMax=False)]
                [tableRecords.append(x) for x in self._era(timeFrame, a_h, "player_id", "starter", starters)]
                [tableRecords.append(x) for x in self._whip(timeFrame, a_h, "player_id", "starter", starters)]
                [tableRecords.append(x) for x in self._k9(timeFrame, a_h, "player_id", "starter", starters)]

        return tableRecords  


    def scheduled_batter_stats(self):
        tableRecords = []
        batterStats = self._fetch_batter_stats()
        for timeFrame, dataFrame in self._get_time_frames(batterStats):
            for a_h, dataFrame in self._get_away_home_frames(dataFrame):
                batters = self._get_valid_group("player_id", "ab", dataFrame)

                [tableRecords.append(x) for x in self._item_sum(timeFrame, a_h, "r", "player_id", "player", batters)]
                [tableRecords.append(x) for x in self._item_sum(timeFrame, a_h, "hr", "player_id", "player", batters)]
                [tableRecords.append(x) for x in self._item_sum(timeFrame, a_h, "rbi", "player_id", "player", batters)]
                [tableRecords.append(x) for x in self._item_sum(timeFrame, a_h, "sb", "player_id", "player", batters)]
                [tableRecords.append(x) for x in self._item_one_per_another(timeFrame, a_h, "h", "ab", "avg", "player_id", "player", batters)]
                [tableRecords.append(x) for x in self._obp(timeFrame, a_h, "player_id", "player", batters)]
                [tableRecords.append(x) for x in self._item_one_per_another(timeFrame, a_h, "num_bases", "ab", "slg", "player_id", "player", batters)]
        return tableRecords       



    


    


    


    


    


    


    


    


    


    


   


   

