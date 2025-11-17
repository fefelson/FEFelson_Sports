import pandas as pd 
from pprint import pprint 

from fefelson_sports.database.orms.database import get_db_session



def printDB(tableName):

    with get_db_session() as session:
        query = f"""
                    SELECT *
                    
                    FROM {tableName} 
                """
        return  pd.read_sql(query, session.bind)













if __name__ == "__main__":
    
    for tableName in ("rushing",):
        pprint(printDB(tableName))
    
