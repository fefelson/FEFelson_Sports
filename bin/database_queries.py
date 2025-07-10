import pandas as pd 
from pprint import pprint 


from fefelson_sports.database.models.database import get_db_session




def player_data(playerId):

    with get_db_session() as session:
        query = f"""
                    SELECT first_name, last_name, bats, throws
                    FROM players AS p
                    WHERE player_id = '{playerId}'
                    """
        return  pd.read_sql(query, session.bind)

        
def pitching_stats(playerId, season):

    with get_db_session() as session:
        query = f"""
                    SELECT COUNT(at_bat_id)
                    FROM at_bats AS ab
                    INNER JOIN games AS g
                        ON ab.game_id = g.game_id
                    INNER JOIN ( SELECT COUNT())
                    WHERE pitcher_id = '{playerId}' AND season = {season}
                    """
        return  pd.read_sql(query, session.bind)




def pitching_stats(player_id, season):

    with get_db_session() as session:
        query = f"""
                    SELECT 
                        pitcher_id,
                        SUM(w) AS w,
                        SUM(l) AS l,
                        SUM(sv) AS sv,
                        SUM(full_ip + partial_ip / 3.0) AS ip,
                        CASE 
                            WHEN SUM(full_ip + partial_ip / 3.0) = 0 THEN 0
                            ELSE (SUM(er) * 9.0) / SUM(full_ip + partial_ip / 3.0)
                        END AS era
                    FROM pitching_stats AS ps
                    INNER JOIN games AS g ON ps.game_id = g.game_id
                    WHERE pitcher_id = '{player_id}' AND season = '{season}'
                    GROUP BY pitcher_id

                    """
        return  pd.read_sql(query, session.bind)



def batting_stats(player_id, season):

    with get_db_session() as session:
        query = f"""
                    SELECT 
                        ab.batter_id,
                        COUNT(CASE WHEN att.is_pa THEN 1 END) AS plate_appearances,
                        COUNT(CASE WHEN att.is_ab THEN 1 END) AS at_bats,
                        COUNT(CASE WHEN att.is_ob THEN 1 END) AS times_on_base,
                        COUNT(CASE WHEN att.is_hit THEN 1 END) AS hits,
                        SUM(CASE WHEN att.num_bases IS NOT NULL THEN att.num_bases ELSE 0 END) AS total_bases,
                        COUNT(CASE WHEN att.at_bat_type_name = 'walk' THEN 1 END) AS walks,
                        COUNT(CASE WHEN att.at_bat_type_name = 'hit by pitch' THEN 1 END) AS hit_by_pitch,
                        COUNT(CASE WHEN att.at_bat_type_name = 'home run' THEN 1 END) AS home_runs,
                        COUNT(CASE WHEN att.at_bat_type_name = 'strike out' THEN 1 END) AS strikeouts
                    FROM at_bats ab
                    JOIN at_bat_types att ON ab.at_bat_type_id = att.at_bat_type_id
                    INNER JOIN games AS g ON ab.game_id = g.game_id
                    WHERE season = {season}
                    GROUP BY ab.batter_id
                    ORDER BY ab.batter_id;

                    """
        return  pd.read_sql(query, session.bind)


if __name__ == "__main__":
    pprint(player_data("mlb.p.64011"))
    pprint(pitching_stats("mlb.p.64011", 2025))
    
