from sqlalchemy import Boolean, CheckConstraint, Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base 


##############################################################################
##############################################################################'


class Game(Base):
    __tablename__ = 'games'
    game_id = Column(String, primary_key=True)
    league_id = Column(String, ForeignKey('leagues.league_id', ondelete='CASCADE'), nullable=False)
    home_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    away_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    winner_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=True)
    loser_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=True)
    stadium_id = Column(String, ForeignKey('stadiums.stadium_id'), nullable=True)
    is_neutral_site = Column(Boolean, default=False)
    game_date = Column(DateTime, nullable=False)
    season = Column(Integer, nullable=False)
    week = Column(Integer, nullable=True)
    game_type = Column(String, CheckConstraint("game_type IN ('season', 'postseason', 'final')"), nullable=False)
    game_result = Column(String, CheckConstraint("game_result IN ('won', 'tied')"), default='won')

    stadium = relationship("Stadium", back_populates="games")


##############################################################################
##############################################################################'


class Period(Base):
    __tablename__ = 'periods'
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id'), primary_key=True)
    opp_id = Column(Integer, ForeignKey('teams.team_id'), nullable=False)
    period = Column(Integer, primary_key=True)
    pts = Column(Integer, nullable=False)


##############################################################################
##############################################################################'


class Player(Base):
    __tablename__ = 'players'
    player_id = Column(Integer, primary_key=True, autoincrement=True)
    league_id = Column(String, ForeignKey('leagues.league_id', ondelete='CASCADE'), nullable=False)  
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    bats = Column(String, nullable=True)
    throws = Column(String, nullable=True)
    pos = Column(String, nullable=True)
    birthdate = Column(Date, nullable=True)
    rookie_season = Column(Integer, nullable=True)


##############################################################################
##############################################################################


class Team(Base):
    __tablename__ = 'teams'
    team_id = Column(Integer, primary_key=True, autoincrement=True)
    league_id = Column(String, ForeignKey('leagues.league_id', ondelete='CASCADE'), nullable=False)  
    org_id = Column(Integer, ForeignKey('organizations.org_id', ondelete='CASCADE'), nullable=False)  
    conference = Column(String, nullable=True)
    division = Column(String, nullable=True)

    organization = relationship("Organization", back_populates="teams")


##############################################################################
##############################################################################'


class Stadium(Base):
    __tablename__ = 'stadiums'
    stadium_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)

    games = relationship("Game", back_populates="stadium")
