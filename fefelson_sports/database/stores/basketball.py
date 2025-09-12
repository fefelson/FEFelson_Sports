from sqlalchemy.orm import Session

from .store import Store

from ..orms import BasketballTeamStat, BasketballPlayerStat, BasketballShot



###################################################################
###################################################################


class TeamStatStore(Store):
    
    def __init__(self):
        super().__init__()


    def get_by_id(self, statsData: dict, session: Session = None) -> BasketballTeamStat:
        session = self._execute_with_session(session)
        return session.query(BasketballTeamStat).filter_by(game_id=statsData["game_id"], 
                                                            team_id=statsData["team_id"]).first()


    def insert(self, session: Session, statsData: dict) -> None:
        if not self.get_by_id(statsData, session):
            session.add(BasketballTeamStat(**statsData))


###################################################################
###################################################################


class PlayerStatStore(Store):

    def __init__(self):
        super().__init__()


    def get_by_id(self, statsData: dict, session: Session = None) -> BasketballPlayerStat:
        session = self._execute_with_session(session)
        return session.query(BasketballPlayerStat).filter_by(game_id=statsData["game_id"], 
                                                    player_id=statsData["player_id"]).first()


    def insert(self, session: Session, statsData:dict) -> None:
        if not self.get_by_id(statsData, session):
            session.add(BasketballPlayerStat(**statsData))



###################################################################
###################################################################


class PlayerShotStore(Store):

    def __init__(self):
        super().__init__()


    def get_by_id(self, statsData: dict, session: Session = None) -> BasketballShot:
        session = self._execute_with_session(session)
        return session.query(BasketballShot).filter_by(game_id=statsData["game_id"], 
                                                    play_num=statsData["play_num"]).first()


    def insert(self, session: Session, statsData:dict) -> None:
        if not self.get_by_id(statsData, session):
            session.add(BasketballShot(**statsData))
