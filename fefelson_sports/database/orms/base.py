from sqlalchemy import CheckConstraint, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base 


##############################################################################
##############################################################################


class League(Base):
    __tablename__ = 'leagues'
    league_id = Column(String, primary_key=True)  # e.g., "NBA"
    sport_id = Column(String, ForeignKey('sports.sport_id'), nullable=False)
    name = Column(String, unique=True, nullable=False)
    sched_type = Column(String, CheckConstraint("schedule_type IN ('daily', 'weekly')"), nullable=False)
    curr_season = Column(Integer, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    last_update = Column(Date, nullable=True)


##############################################################################
##############################################################################


class Organization(Base):
    __tablename__ = 'organizations'
    org_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    abrv = Column(String, nullable=False)
    primary_color = Column(String, nullable=True)
    secondary_color = Column(String, nullable=True)
    org_type = Column(String, CheckConstraint("org_type IN ('club', 'school')"), nullable=False)

    teams = relationship("Team", back_populates="organization")


##############################################################################
##############################################################################


class Provider(Base):
    __tablename__ = 'providers'
    name = Column(String, primary_key=True)  
    url = Column(String, nullable=False)
    

##############################################################################
##############################################################################


class ProviderMapping(Base):
    __tablename__ = 'provider_mapping'
    provider = Column(String, ForeignKey('providers.name', ondelete='CASCADE'), primary_key=True)  # e.g., "yahoo", "espn"
    league_id = Column(String, ForeignKey('leagues.league_id', ondelete='CASCADE'), primary_key=True)
    entity_type = Column(String, primary_key=True) # game, player, team
    provider_id = Column(String, primary_key=True) # outside ID
    entity_id = Column(Integer, nullable=False, index=True) # inside ID

##############################################################################
##############################################################################


class Sport(Base):
    __tablename__ = 'sports'
    sport_id = Column(String, primary_key=True)  # e.g., "Basketball"


##############################################################################
##############################################################################


class Week(Base):
    __tablename__ = 'weeks'
    league_id = Column(String, ForeignKey('leagues.league_id', ondelete='CASCADE'), primary_key=True)
    week_num = Column(Integer, primary_key=True) 
    start_date = Column(Date, nullable=False) # inside ID
    end_date = Column(Date, nullable=False)



