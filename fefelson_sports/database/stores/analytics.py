from pandas import read_sql

from .store import Store

from ..orms.analytic_tables import LeagueMetric


class AnalyticsStore(Store):

    def __init__(self):
        super().__init__()
        


    def get_league_metrics(self,  leagueId, timeFrame, awayHome, entityType, metric, session=None):
        session = self._execute_with_session(session)
        query = f""" 
                SELECT * FROM league_metrics AS lm
                WHERE league_id = '{leagueId}' AND timeframe = '{timeFrame}' AND away_home = '{awayHome}' AND entity_type = '{entityType}' ANd metric_name = '{metric}'
            """
        result = read_sql(query, session.bind) 
        return {
            "best_value": result["best_value"].iloc[0],
            "worst_value": result["worst_value"].iloc[0],
            "q1": result["q1"].iloc[0],
            "q2": result["q2"].iloc[0],
            "q4": result["q4"].iloc[0],
            "q6": result["q6"].iloc[0],
            "q8": result["q8"].iloc[0],
            "q9": result["q9"].iloc[0]
        } 