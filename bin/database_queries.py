import pandas as pd 
from pprint import pprint 

from fefelson_sports.database.orms.database import get_db_session



def printDB(tableName):

    with get_db_session() as session:
        query = f"""
                    SELECT time_of_poss
                    
                    FROM {tableName} as fts
                    INNER JOIN games as g On fts.game_id = g.game_id
                     WHERE league_id = 'NFL' 
                """
        return  pd.read_sql(query, session.bind)













if __name__ == "__main__":
    
    for tableName in ("football_team_stats", ):
        pprint(printDB(tableName).head(25))
    
