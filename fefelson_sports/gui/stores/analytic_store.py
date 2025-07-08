import pandas as pd

from ...database.models.database import get_db_session



class AnalyticStore:

    def get_stat_metrics(leagueId, timeframe):
        with get_db_session() as session:
            query = f"""
                    SELECT *
                    FROM stat_metrics
                    WHERE entity_type = 'team' AND league_id = '{leagueId}' AND timeframe = '{timeframe}'
                    """
            return pd.read_sql(query, session.bind)  

