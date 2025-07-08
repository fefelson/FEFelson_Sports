from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from .database import Base 


##############################################################################
##############################################################################


class Sport(Base):
    __tablename__ = 'sports'
    sport_id = Column(String, primary_key=True)  # e.g., "Basketball"
    name = Column(String, unique=True, nullable=False)

    leagues = relationship("League", back_populates="sport")
    players = relationship("Player", back_populates="sport")


##############################################################################
##############################################################################



class League(Base):
    __tablename__ = 'leagues'
    league_id = Column(String, primary_key=True)  # e.g., "NBA"
    sport_id = Column(String, ForeignKey('sports.sport_id'), nullable=False)
    name = Column(String, unique=True, nullable=False)

    sport = relationship("Sport", back_populates="leagues")
    teams = relationship("Team", back_populates="league")
    games = relationship("Game", back_populates="league")



##############################################################################
##############################################################################



class School(Base):
    __tablename__ = 'schools'
    school_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)

    teams = relationship("Team", back_populates="school")



##############################################################################
##############################################################################



class Team(Base):
    __tablename__ = 'teams'
    team_id = Column(String, primary_key=True)
    league_id = Column(String, ForeignKey('leagues.league_id', ondelete='CASCADE'), nullable=False)
    school_id = Column(String, ForeignKey('schools.school_id'), nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    abrv = Column(String, nullable=False)
    conference = Column(String, nullable=True)
    division = Column(String, nullable=True)
    primary_color = Column(String, nullable=True)
    secondary_color = Column(String, nullable=True)

    league = relationship("League", back_populates="teams")
    school = relationship("School", back_populates="teams")
    draft_players = relationship("Player", foreign_keys="Player.draft_team_id", back_populates="draft_team")
    home_games = relationship("Game", foreign_keys="Game.home_id", back_populates="home_team")
    away_games = relationship("Game", foreign_keys="Game.away_id", back_populates="away_team")
    won_games = relationship("Game", foreign_keys="Game.winner_id", back_populates="winner")
    lost_games = relationship("Game", foreign_keys="Game.loser_id", back_populates="loser")



##############################################################################
##############################################################################'


class Player(Base):
    __tablename__ = 'players'
    player_id = Column(String, primary_key=True)
    sport_id = Column(String, ForeignKey('sports.sport_id', ondelete='CASCADE'), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    height = Column(Integer, nullable=True)
    weight = Column(Integer, nullable=True)
    bats = Column(String, nullable=True)
    throws = Column(String, nullable=True)
    position = Column(String, nullable=True)
    birthdate = Column(Date, nullable=True)
    current_team_id = Column(String, ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=True)
    uniform_number = Column(String, nullable=True)
    college = Column(String, nullable=True)
    draft_year = Column(Integer, nullable=True)
    draft_round = Column(Integer, nullable=True)
    draft_pick = Column(Integer, nullable=True)
    draft_team_id = Column(String, ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=True)
    graduation_yr = Column(String, nullable=True)
    rookie_season = Column(Integer, nullable=True)

    sport = relationship("Sport", back_populates="players")
    draft_team = relationship("Team", foreign_keys=[draft_team_id], back_populates="draft_players")



##############################################################################
##############################################################################'


class Game(Base):
    __tablename__ = 'games'
    game_id = Column(String, primary_key=True)
    league_id = Column(String, ForeignKey('leagues.league_id', ondelete='CASCADE'), nullable=False)
    home_id = Column(String, ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=False)
    away_id = Column(String, ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=False)
    winner_id = Column(String, ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=True)
    loser_id = Column(String, ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=True)
    stadium_id = Column(String, ForeignKey('stadiums.stadium_id'), nullable=True)
    is_neutral_site = Column(Boolean, default=False)
    game_date = Column(DateTime, nullable=False)
    season = Column(Integer, nullable=False)
    week = Column(Integer, nullable=True)
    game_type = Column(String, CheckConstraint("game_type IN ('season', 'postseason', 'final')"), nullable=False)
    game_result = Column(String, CheckConstraint("game_result IN ('won', 'tied')"), default='won')

    league = relationship("League", back_populates="games")
    home_team = relationship("Team", foreign_keys=[home_id], back_populates="home_games")
    away_team = relationship("Team", foreign_keys=[away_id], back_populates="away_games")
    winner = relationship("Team", foreign_keys=[winner_id], back_populates="won_games")
    loser = relationship("Team", foreign_keys=[loser_id], back_populates="lost_games")
    stadium = relationship("Stadium", back_populates="games")


##############################################################################
##############################################################################'


class Stadium(Base):
    __tablename__ = 'stadiums'
    stadium_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)

    games = relationship("Game", back_populates="stadium")



##############################################################################
##############################################################################'


class Period(Base):
    __tablename__ = 'periods'
    game_id = Column(String, ForeignKey('games.game_id'), primary_key=True)
    team_id = Column(String, ForeignKey('teams.team_id'), primary_key=True)
    opp_id = Column(String, ForeignKey('teams.team_id'), nullable=False)
    period = Column(Integer, primary_key=True)
    pts = Column(Integer, nullable=False)

    game = relationship("Game")
    team = relationship("Team", foreign_keys=[team_id])
    opponent = relationship("Team", foreign_keys=[opp_id])



##############################################################################
##############################################################################


class ProviderMapping(Base):
    __tablename__ = 'provider_mapping'
    provider = Column(String, primary_key=True)  # e.g., "yahoo", "espn"
    entity_type = Column(String, primary_key=True) # game, player, team
    entity_id = Column(String, primary_key=True) # inside ID
    provider_id = Column(String, nullable=False) # outside ID
