from datetime import datetime, date
from pandas import read_sql, merge, to_datetime
from sqlalchemy.orm import joinedload, Session
from typing import List

from .store import Store

from ..orms import Game, Period, Player, Stadium, Team



###################################################################
###################################################################


class GameStore(Store):
    
    def __init__(self):
        super().__init__()


    def get_opps(self, timeFrame, awayHome, teamId, session):
        if not teamId:
            return None 

        session = self._execute_with_session(session)
        andGD = self._and_gameDate(timeFrame)

        query = f"""
                SELECT org_id, game_date
                FROM football_team_stats AS fts
                INNER JOIN games AS g ON fts.game_id = g.game_id
                INNER JOIN teams AS t ON fts.opp_id = t.team_id
                INNER JOIN leagues AS l ON g.league_id = l.league_id
                WHERE fts.team_id = {teamId} {andGD}
                ORDER BY game_date DESC
                """
        result = read_sql(query, session.bind) 
        if awayHome != "all":
            result = result[(result['team_id'] == result[f"{awayHome}_id"])]
        
        games = []
        for _,row in result.iterrows():
            games.append((row["org_id"], to_datetime(row["game_date"]).strftime("%b %d")))

        return games


    def create_gameId(self, leagueId, homeId, gameDate):
        gameDate = datetime.fromisoformat(gameDate)
        gameId = f"{leagueId}_{gameDate.strftime('%Y%m%d')}_{homeId:04d}"
        return gameId


    def get_by_id(self, gameId: str, session: Session = None) -> Game:

        session = self._execute_with_session(session)
        return session.query(Game).filter_by(game_id=gameId).first()


    def insert(self, session: Session, gameData: dict) -> None:
        if not self.get_by_id(gameData["game_id"], session):
            session.add(Game(**gameData))
            


###################################################################
###################################################################


class PeriodStore(Store):

    def __init__(self):
        super().__init__()


    def get_by_id(self, period: dict, session: Session = None) -> Period:
        session = self._execute_with_session(session)
        return session.query(Period).filter_by(game_id=period["game_id"], 
                                                team_id=period["team_id"],
                                                period=period["period"]).first()


    def insert(self, session: Session, period: dict) -> None:
        if not self.get_by_id(period, session):
            session.add(Period(**period))
            
    
###################################################################
###################################################################


class PlayerStore(Store):

    def __init__(self):
        super().__init__()


    def get_by_id(self, player: dict, session: Session = None) -> Player:
        session = self._execute_with_session(session)
        return session.query(Player).filter_by(player_id=player["player_id"]).first()


    def insert(self, session: Session, player: dict) -> int:
        newPlayer = Player(**player)
        session.add(newPlayer)
        session.flush()
        return newPlayer.player_id


    def update_player(self, playerId, data, session = None):
        session = self._execute_with_session(session)
        player = session.query(Player).filter_by(player_id=playerId).first()
        player.bats = data["bats"]
        player.throws = data["throws"]
        player.birthdate = data["birthdate"]
        player.rookie_season = data["rookie_season"]


    def get_info(self, playerId, session = None):
        session = self._execute_with_session(session)
        player = session.query(Player).filter_by(player_id=playerId).first()
        return {
                "player_id": player.player_id,
                "first_name": player.first_name, 
                "last_name": player.last_name,
                "bats": player.bats, 
                "throws": player.throws, 
                "pos": player.pos
            }



    def get_mlb_players_with_null_bats_and_throws(self, session: Session = None) -> List[int]:
        """
        Retrieve player IDs for MLB players with NULL bats and throws using ORM.
        
        """
        session = self._execute_with_session(session)
        result = session.query(Player.player_id).filter(
            Player.league_id == 'MLB',
            Player.bats == None,
            Player.throws == None
        ).all()
        return [r.player_id for r in result]
        
    
###################################################################
###################################################################


class StadiumStore(Store):
    
    def __init__(self):
        super().__init__()


    def get_by_id(self, stadium_id: str, session: Session = None) -> Stadium:
        session = self._execute_with_session(session)
        return session.query(Stadium).filter_by(stadium_id=stadium_id).first()


    def insert(self, session: Session, stadium_data: dict) -> None:
        if not self.get_by_id(stadium_data["stadium_id"], session):
            session.add(Stadium(**stadium_data))


###################################################################
###################################################################


class TeamStore(Store):

    def __init__(self):
        super().__init__()


    def get_by_id(self, teamId: int, session: Session = None) -> Team:
        session = self._execute_with_session(session)
        return session.query(Team).filter_by(team_id=teamId).options(joinedload(Team.organization)).first()
    

    def get_team_info(self, teamId: int, session: Session = None) -> str:
        
        with self._execute_with_session(session) as session:
            
            team = self.get_by_id(teamId, session)
            if team is None:
                return None
            return {
                    "team_id": team.team_id,
                    "first_name": team.organization.first_name, 
                    "last_name": team.organization.last_name,
                    "org_id": team.org_id,
                    "conference": team.conference,
                    "abrv": team.organization.abrv,
                    "primaryColor": team.organization.primary_color,
                    "secondaryColor": team.organization.secondary_color,
                    "type": team.organization.org_type
                    }


   