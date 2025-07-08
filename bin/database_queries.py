import pandas as pd 
from pprint import pprint 

from src.database.models.database import get_db_session

pitch_query = """
                SELECT COUNT(at_bat_id) FROM at_bats
                """

ab_query = """
           WITH total AS (
    SELECT COUNT(*) AS total_count FROM pitches
)
SELECT
    pt.pitch_type_name,
    pt.pitch_type_id,
    COUNT(*) AS pitch_count,
    ROUND(COUNT(*) * 1.0 / t.total_count, 6) AS frequency,
    ROUND(1.0 / (COUNT(*) * 1.0 / t.total_count), 6) AS inverse_frequency_weight
FROM
    pitches p
    JOIN pitch_types pt ON p.pitch_type_name = pt.pitch_type_name
    CROSS JOIN total t
GROUP BY
    pt.pitch_type_name, pt.pitch_type_id, t.total_count
ORDER BY
    pt.pitch_type_id;



            """

def run_query(query):

    with get_db_session() as session:
        return  pd.read_sql(query, session.bind)   

        
        


if __name__ == "__main__":
    pprint(run_query(ab_query))
    
