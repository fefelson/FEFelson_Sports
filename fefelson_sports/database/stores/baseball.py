from datetime import date
from pandas import read_sql, merge
from sqlalchemy.orm import Session
from typing import Any 

from .store import Store

from ..orms import BaseballTeamStat, BattingStat, PitchingStat, BattingOrder, Bullpen, AtBat, Pitch

# for debugging
# from pprint import pprint 


###################################################################
###################################################################


class TeamStatStore(Store):
    
    def __init__(self):
        super().__init__()


    def get_team_stats(self, teamId, timeFrame, awayHome, session = None):
        if not teamId:
            return None 

        session = self._execute_with_session(session)
        andGD = self._and_gameDate(timeFrame)
        query = f""" 
                SELECT g.game_id, bts.team_id, bts.opp_id,g.home_id, g.away_id, ab, bb, r, h, hr, rbi, sb, lob, errors 
                    FROM baseball_team_stats AS bts
                    INNER JOIN games AS g ON bts.game_id = g.game_id
                    INNER JOIN leagues AS l ON g.league_id = l.league_id
                    WHERE team_id = {teamId} {andGD}
            """
        result = read_sql(query, session.bind) 
        query = f""" 
                SELECT ab.game_id, SUM(num_bases) AS num_bases FROM at_bats AS ab
                    INNER JOIN games AS g ON ab.game_id = g.game_id
                    INNER JOIN leagues AS l ON g.league_id = l.league_id
                    INNER JOIN at_bat_types AS abt ON ab.at_bat_type_id = abt.at_bat_type_id
                    WHERE team_id = {teamId} {andGD}
                    GROUP BY ab.game_id
            """
        abResults = read_sql(query, session.bind) 
        result = merge(result, abResults, how="left", on="game_id")
        if awayHome != "all":
            result = result[(result['team_id'] == result[f"{awayHome}_id"])]

        
        return {
            "r": result['r'].sum() / result['game_id'].count(),
            "h": result['h'].sum() / result['game_id'].count(),
            "hr": result['ab'].sum() / result['hr'].sum(),
            "sb": result['sb'].sum() / result['game_id'].count(),
            "lob": (result['lob'].sum() / (result['lob'].sum() + result['rbi'].sum()))*100,
            "avg": result['h'].sum() / result['ab'].sum(),
            "obp": (result['bb'].sum() + result['h'].sum()) / (result['bb'].sum() + result['ab'].sum()),
            "slg": result['num_bases'].sum() / result['ab'].sum(),

            "errors": result['errors'].sum() / result['game_id'].count()
        } 


    def get_by_id(self, statsData: dict, session: Session = None) -> BaseballTeamStat:
        session = self._execute_with_session(session)
        return session.query(BaseballTeamStat).filter_by(game_id=statsData["game_id"], 
                                                            team_id=statsData["team_id"]).first()


    def insert(self, session: Session, statsData: dict) -> None:
        if not self.get_by_id(statsData, session):
            session.add(BaseballTeamStat(**statsData))


###################################################################
###################################################################

class BatterStore(Store):

    def __init__(self):
        super().__init__()


    def get_batter_stats(self, playerId, timeFrame, awayHome, session = None):
        if not playerId:
            return None 

        session = self._execute_with_session(session)
        andGD = self._and_gameDate(timeFrame)
        query = f""" 
                SELECT g.game_id, bts.team_id, bts.opp_id, g.home_id, g.away_id, ab, bb, r, h, hr, rbi, sb 
                    FROM batting_stats AS bts
                    INNER JOIN games AS g ON bts.game_id = g.game_id
                    INNER JOIN leagues AS l on g.league_id = l.league_id
                    WHERE player_id = {playerId} {andGD}
            """
        bsResults = read_sql(query, session.bind) 
        query = f""" 
                SELECT ab.game_id, SUM(num_bases) AS num_bases FROM at_bats AS ab
                    INNER JOIN games AS g ON ab.game_id = g.game_id
                    INNER JOIN leagues AS l ON g.league_id = l.league_id
                    INNER JOIN at_bat_types AS abt ON ab.at_bat_type_id = abt.at_bat_type_id
                    WHERE batter_id = {playerId} {andGD}
                    GROUP BY ab.game_id
            """
        abResults = read_sql(query, session.bind)
        result = merge(bsResults, abResults, how="left", on="game_id")
        if awayHome != "all":
            result = result[(result['team_id'] == result[f"{awayHome}_id"])]


        return {
            "ab": result['ab'].sum(),
            "r": result['r'].sum(),
            "h": result['h'].sum() ,
            "hr": result['hr'].sum(),
            "rbi": result['rbi'].sum(),
            "sb": result['sb'].sum(),
            "avg": result['h'].sum() / result['ab'].sum(),
            "obp": (result['bb'].sum() + result['h'].sum()) / (result['bb'].sum() + result['ab'].sum()),
            "slg": result['num_bases'].sum() / result['ab'].sum(),        } 


class PitcherStore(Store):

    def __init__(self):
        super().__init__()


    def get_bullpen_stats(self, teamId, timeFrame, awayHome, session=None):
        if not teamId:
            return None 

        session = self._execute_with_session(session)
        andGD = self._and_gameDate(timeFrame)
        query = f""" 
            SELECT ps.team_id, g.away_id, g.home_id, full_ip, partial_ip, w, l, sv, blsv, er, bba, ha, k
            FROM pitching_stats AS ps
            INNER JOIN games AS g ON ps.game_id = g.game_id
            INNER JOIN baseball_bullpen AS bb ON ps.game_id = bb.game_id AND ps.player_id = bb.player_id 
            INNER JOIN leagues AS l ON g.league_id = l.league_id
            WHERE pitch_order > 1 AND ps.team_id = {teamId} {andGD}
        """
        result = read_sql(query, session.bind) 
        if awayHome != "all":
            result = result[(result['team_id'] == result[f"{awayHome}_id"])]
        try:
            stats = {
                "ip": (result["full_ip"].sum() + result["partial_ip"].sum() / 3),
                "w": sum(result['w']),
                "l": sum(result['l']),
                "sv": sum(result['sv']) / (sum(result['sv']) + sum(result['blsv'])) * 100 if (sum(result['sv']) + sum(result['blsv'])) > 0 else 0,
                "era": (sum(result['er']) * 9) / (sum(result['full_ip']) + (sum(result['partial_ip']) / 3)) if (sum(result['full_ip']) + (sum(result['partial_ip']) / 3)) > 0 else 0,
                "whip": (sum(result['bba']) + sum(result['ha'])) / (sum(result['full_ip']) + (sum(result['partial_ip']) / 3)) if (sum(result['full_ip']) + (sum(result['partial_ip']) / 3)) > 0 else 0,
                "k9": (sum(result['k']) * 9) / (sum(result['full_ip']) + (sum(result['partial_ip']) / 3)) if (sum(result['full_ip']) + (sum(result['partial_ip']) / 3)) > 0 else 0
            }
        except ZeroDivisionError:
            stats = None 
        return stats
        


    def get_pitcher_stats(self, playerId, timeFrame, awayHome, session = None):
        if not playerId:
            return None 

        session = self._execute_with_session(session)
        andGD = self._and_gameDate(timeFrame)
        query = f""" 
                SELECT * FROM pitching_stats AS ps
                    INNER JOIN games AS g ON ps.game_id = g.game_id
                    INNER JOIN leagues AS l on g.league_id = l.league_id
                    WHERE player_id = {playerId} {andGD}
            """
        result = read_sql(query, session.bind) 
        if awayHome != "all":
            result = result[(result['team_id'] == result[f"{awayHome}_id"])]
        try:
            stats = {
            "gs": result["full_ip"].count(),
            "ip": (result["full_ip"].sum() + result["partial_ip"].sum()/3) / result["full_ip"].count(),
            "w": sum(result['w']),
            "l": sum(result['l']),
            "sv": sum(result['sv']),
            "era": (sum(result['er']) * 9) / (sum(result['full_ip']) + (sum(result['partial_ip'])/3)),
            "whip": (sum(result['bba']) + sum(result['ha'])) / (sum(result['full_ip']) + (sum(result['partial_ip'])/3)),
            "k9": (sum(result['k']) * 9) / (sum(result['full_ip']) + (sum(result['partial_ip'])/3))
        }
        except ZeroDivisionError:
            stats = None 
        return stats
        



class PlayerStatStore(Store):

    def __init__(self):
        super().__init__()


    def get_by_id(self, statsData: dict, statClass: Any, session: Session = None) -> Any:
        session = self._execute_with_session(session)
        return session.query(statClass).filter_by(player_id=statsData["player_id"],
                                                    game_id=statsData["game_id"]).first()


    def insert(self, session: Session, statClass: Any, statsData:dict) -> None:
        if not self.get_by_id(statsData, statClass, session):
            session.add(statClass(**statsData))


    def insert_batting(self, session: Session, statsData: dict) -> None:
        self.insert(session, BattingStat, statsData)
        

    def insert_pitching(self, session: Session, statsData: dict) -> None:
        self.insert(session, PitchingStat, statsData)


    def insert_lineup(self, session: Session, statsData: dict) -> None:
        self.insert(session, BattingOrder, statsData)


    def insert_bullpen(self, session: Session, statsData: dict) -> None:
        self.insert(session, Bullpen, statsData)




###################################################################
###################################################################


class PlayerPlayStore(Store):

    def __init__(self):
        super().__init__()


    def get_by_id(self, statsData: dict, statClass: Any, session: Session = None) -> Any:
        session = self._execute_with_session(session)
        return session.query(statClass).filter_by(game_id=statsData["game_id"], 
                                                    play_num=statsData["play_num"]).first()


    def insert(self, session: Session, statClass: Any, statsData:dict) -> None:
        if not self.get_by_id(statsData, statClass, session):
            session.add(statClass(**statsData))



    def insert_pitch(self, session: Session, statsData: dict) -> None:
        self.insert(session, Pitch, statsData)


    def insert_at_bat(self, session: Session, statsData: dict) -> None:
        self.insert(session, AtBat, statsData)

