from pandas import read_sql
from sqlalchemy.orm import Session

from .store import Store

from ..orms import GameLine, OverUnder

# for debugging
# from pprint import pprint 



class GamingStore(Store):
    def __init__(self):
        super().__init__()


    def get_gaming_results(self, teamId, timeFrame, awayHome, session = None):
        if not teamId:
            return None 

        session = self._execute_with_session(session)
        andGD = self._and_gameDate(timeFrame)
        query = f"""
                        SELECT gl.game_id,
                                gl.team_id,
                                g.home_id,
                                g.away_id,
                                gl.spread as pts_spread,
                                gl.result,
                                gl.result + gl.spread AS ats,
                                gl.money_line,
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
                                    WHEN gl.money_outcome = 1 AND gl.money_line IS NULL THEN 100
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
                            INNER JOIN leagues AS l
                                ON g.league_id = l.league_id
                            LEFT JOIN over_unders AS ou
                                ON gl.game_id = ou.game_id
                            WHERE  gl.team_id = '{teamId}' {andGD}
                    """
        result = read_sql(query, session.bind) 
        if awayHome != "all":
            result = result[(result['team_id'] == result[f"{awayHome}_id"])]

        return {
            "gp": result["game_id"].count(),
            "pts_spread": result["pts_spread"].median(),
            "result": result["result"].mean(),
            "ats": result["ats"].mean(),
            "ML": result["money_line"].median(),
            "wins": result["is_winner"].sum(),
            "loses": result["game_id"].count() - result["is_winner"].sum(),
            "wins_ats": result["is_cover"].sum(),
            "loss_ats": result["game_id"].count() - result["is_cover"].sum(),
            "o/u": result["over_under"].mean(),
            "total": result["total"].mean(),
            "att": result["att"].mean(),
            "overs": result["is_over"].sum(),
            "unders": result["is_under"].sum(),
            "money_roi": (result["money_roi"].sum() - (result["game_id"].count()*100))/(result["game_id"].count()*100),
            "spread_roi": (result["spread_roi"].sum() - (result["game_id"].count()*100))/(result["game_id"].count()*100),
            "over_roi": (result["over_roi"].sum() - (result["game_id"].count()*100))/(result["game_id"].count()*100),
            "under_roi": (result["under_roi"].sum() - (result["game_id"].count()*100))/(result["game_id"].count()*100)
                    } 




###################################################################
###################################################################


class GameLineStore(Store):
    
    def __init__(self):
        super().__init__()


    def get_by_id(self, glData: dict, session: Session = None) -> GameLine:
        session = self._execute_with_session(session)
        return session.query(GameLine).filter_by(game_id=glData["game_id"], 
                                                    team_id=glData["team_id"]).first()


    def insert(self, session: Session, glData: dict) -> None:
        if not self.get_by_id(glData, session):
            session.add(GameLine(**glData))


###################################################################
###################################################################


class OverUnderStore(Store):

    def __init__(self):
        super().__init__()


    def get_by_id(self, ouData: dict, session: Session = None) -> OverUnder:
        session = self._execute_with_session(session)
        return session.query(OverUnder).filter_by(game_id=ouData["game_id"]).first()


    def insert(self, session: Session, ouData: dict) -> None:
        if not self.get_by_id(ouData, session):
            session.add(OverUnder(**ouData))
            
    
