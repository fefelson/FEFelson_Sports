import pandas as pd

from ...database.models.database import get_db_session



##############################################################################
##############################################################################

basketballQuery = """ 
                       SELECT g.game_id, 
                                bts.minutes,
                                bts.possessions AS team_poss, opp.possessions AS opp_poss,
                                bts.pts AS team_pts, opp.pts AS opp_pts,
                                bts.fga AS team_fga, opp.fga AS opp_fga,
                                bts.fgm AS team_fgm, opp.fgm AS opp_fgm,
                                bts.fta AS team_fta, opp.fta AS opp_fta,
                                bts.ftm AS team_ftm, opp.ftm AS opp_ftm,
                                bts.tpa AS team_tpa, opp.tpa AS opp_tpa,
                                bts.tpm AS team_tpm, opp.tpm AS opp_tpm,
                                bts.oreb AS team_oreb, opp.oreb AS opp_oreb,
                                bts.dreb AS team_dreb, opp.dreb AS opp_dreb,
                                bts.ast AS team_ast, opp.ast AS opp_ast,
                                bts.turnovers AS team_trn, opp.turnovers AS opp_trn

                        FROM basketball_team_stats AS bts
                        INNER JOIN games AS g
                            ON bts.game_id = g.game_id
                        INNER JOIN basketball_team_stats AS opp
                            ON bts.game_id = opp.game_id AND bts.team_id = opp.opp_id
                        WHERE bts.team_id = '{0[teamId]}' AND league_id = '{0[leagueId]}' AND season = {0[season]}
                    """



class TeamStore:


    def get_team(leagueId, teamId):
         with get_db_session() as session:
            query = f"SELECT * FROM teams WHERE league_id = '{leagueId}' AND team_id = '{teamId}'"
            return pd.read_sql(query, session.bind) 
         

    def get_team_gaming(leagueId, teamId, season):
        with get_db_session() as session:
            query = f"""
                        SELECT gl.game_id,
                                gl.spread as pts_spread,
                                gl.result,
                                gl.result + gl.spread AS ats,
                                gl.money_line,
                                g.home_team_id = gl.team_id AS is_home,
                                g.winner_id = gl.team_id AS is_winner,
                                gl.money_outcome AS is_money,
                                gl.spread_outcome AS is_cover,
                                ou.over_under,
                                ou.total,
                                ou.total - ou.over_under AS att,
                                ou.ou_outcome = 1 AS is_over,
                                ou.ou_outcome = -1 AS is_under,
                                
                                -- Spread ROI
                                CASE 
                                    WHEN gl.spread_outcome = 1 AND gl.spread_line < 0 THEN (10000/(gl.spread_line*-1.0)) + 100
                                    WHEN gl.spread_outcome = 1 AND gl.spread_line > 0 THEN gl.spread_line + 100
                                    WHEN gl.spread_outcome = 0 THEN 100
                                    ELSE 0 
                                END AS spread_roi,

                                -- Moneyline ROI
                                CASE 
                                    WHEN gl.money_outcome = 1 AND gl.money_line > 0 THEN 100 + gl.money_line
                                    WHEN gl.money_outcome = 1 AND gl.money_line < 0 THEN (10000/(gl.money_line*-1.0)) + 100
                                    ELSE 0 
                                END AS money_roi,

                                -- Over ROI
                                CASE 
                                    WHEN ou.ou_outcome = 1 AND ou.over_line > 0 THEN 100 + ou.over_line
                                    WHEN ou.ou_outcome = 1 AND ou.over_line < 0 THEN (10000/(ou.over_line*-1.0)) + 100
                                    WHEN ou.ou_outcome = 0 THEN 100
                                    ELSE 0 
                                END over_roi,

                                -- Under ROI
                                CASE 
                                    WHEN ou.ou_outcome = -1 AND ou.under_line > 0 THEN 100 + ou.under_line
                                    WHEN ou.ou_outcome = -1 AND ou.under_line < 0 THEN (10000/(ou.under_line*-1.0)) + 100
                                    WHEN ou.ou_outcome = 0 THEN 100
                                    ELSE 0 
                                END under_roi

                            FROM game_lines AS gl
                            INNER JOIN games AS g
                                ON gl.game_id = g.game_id
                            LEFT JOIN over_unders AS ou
                                ON gl.game_id = ou.game_id
                            WHERE  g.league_id = '{leagueId}' AND gl.team_id = '{teamId}' AND season = {season}
                    """
            return pd.read_sql(query, session.bind)  
         

    def get_team_gamelog(leagueId, teamId, season):
        with get_db_session() as session:
            query = f"""
                        SELECT g.league_id,
                                ts.game_id,
                                g.game_date,
                                ts.team_id,
                                ts.opp_id,
                                ts.team_id = g.home_team_id as is_home,
                                ts.team_id = g.winner_id as is_winner,
                                ts.pts as team_pts,
                                opp.pts as opp_pts,
                                gl.spread as pts_spread,
                                gl.money_line,
                                ou.over_under,
                                gl.money_outcome AS is_money,
                                gl.spread_outcome as is_cover,
                                ou.ou_outcome = 1 AS is_over,
                                ou.ou_outcome = -1 AS is_under
                                
                            FROM basketball_team_stats AS ts
                            INNER JOIN basketball_team_stats AS opp
                                ON ts.game_id = opp.game_id AND ts.team_id = opp.opp_id
                            INNER JOIN games AS g
                                ON ts.game_id = g.game_id
                            LEFT JOIN game_lines AS gl
                                ON ts.game_id = gl.game_id AND ts.team_id = gl.team_id
                            LEFT JOIN over_unders AS ou
                                ON ts.game_id = ou.game_id
                            WHERE g.league_id = '{leagueId}' AND ts.team_id = '{teamId}' AND season = {season}
                    """
            dataFrame = pd.read_sql(query, session.bind)
            dataFrame['game_date'] = pd.to_datetime(dataFrame['game_date'])
            return dataFrame


    def get_team_stats(leagueId, teamId, season):
        query = {"NBA": basketballQuery, "NCAAB": basketballQuery}[leagueId] 
        with get_db_session() as session:
            return pd.read_sql(query.format({"leagueId":leagueId, "teamId":teamId, "season":season}), session.bind)
        