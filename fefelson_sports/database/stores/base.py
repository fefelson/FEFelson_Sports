from datetime import date
from sqlalchemy.orm import Session
from typing import Any 

from .store import Store

from ..orms import League, Provider, ProviderMapping, Week
from ..orms.database import get_db_session



###################################################################
###################################################################


class LeagueStore(Store):

    def __init__(self):
        super().__init__()


    def get_by_id(self, leagueId: str, session: Session = None) -> bool:
        session = self._execute_with_session(session)
        return session.query(League).filter_by(league_id=leagueId).first()


    def get_current_season(self, leagueId, session: Session = None) -> date:
        session = self._execute_with_session(session)
        league = self.get_by_id(leagueId, session)
        
        return league.curr_season 

        
    def get_last_update(self, leagueId, session: Session = None) -> date:
        session = self._execute_with_session(session)
        league = self.get_by_id(leagueId, session)
        
        if league.last_update:
            return league.last_update
        else:
            return league.start_date
        
            

    def get_major_dates(self, leagueId, session: Session = None) -> dict:
        session = self._execute_with_session(session)
        league = self.get_by_id(leagueId, session)
        return {"startDate": league.start_date, "endDate": league.end_date}


    def get_weeks(self, leagueId, session: Session = None) -> dict:
        session = self._execute_with_session(session)
        return [{"week_num": week.week_num, "start_date": week.start_date, "end_date": week.end_date} 
                    for week in session.query(Week).filter_by(league_id=leagueId).all()]


    def set_last_update(self, leagueId, lastUpdate, session = None):
        session = self._execute_with_session(session)
        league = self.get_by_id(leagueId, session)
        league.last_update = lastUpdate
        session.commit()


###################################################################
###################################################################


class ProviderStore(Store):

    def __init__(self):
        super().__init__()
    

    def get_providers(self, session: Session = None) -> list[str]:
        """Fetch all provider names, using a provided session or a new one."""
        session = self._execute_with_session(session)
        return [provider.name for provider in session.query(Provider).all()]


    def get_mapping(self, provider, entityType, session: Session = None) -> list[tuple]:
        """Fetch all provider names, using a provided session or a new one."""
        session = self._execute_with_session(session)

        return [
            (mapping.entity_id, mapping.provider_id) for mapping in
                session.query(ProviderMapping).filter_by(provider=provider, entity_type=entityType).all()
        ]



    def get_inside_id(self, provider: str, leagueId: str, entityType: str, providerId: Any,
                         session: Session=None) -> Any:

        session = self._execute_with_session(session)
        mapping = (
            session.query(ProviderMapping)
                    .filter_by(provider=provider, league_id=leagueId, entity_type=entityType, 
                                provider_id=providerId)
                    .first()
        )
        if mapping is None:
            return -1
        return mapping.entity_id


    def get_outside_id(self, provider: str, leagueId: str, entityType: str, entityId: Any,
                         session: Session=None) -> Any:

        session = self._execute_with_session(session)
        mapping = (
            session.query(ProviderMapping)
                    .filter_by(provider=provider, league_id=leagueId, entity_type=entityType, 
                                entity_id=entityId)
                    .first()
        )
        if mapping is None:
            return -1
        return mapping.provider_id


    def insert(self, session: Session, mapping: dict) -> None:
        session.add(ProviderMapping(**mapping))


    def set_provider_id(self, provider: str, leagueId: str, entityType: str, providerId: Any,
                         entityId: int, session: Session=None) -> None:
        session = self._execute_with_session(session)
        mapping = {"provider": provider, "league_id": leagueId, "entity_type": entityType, 
                        "provider_id": providerId, "entity_id": entityId}
        if self.get_inside_id(provider, leagueId, entityType, providerId) == -1:
            self.insert(session, mapping)
            session.flush()

   


   