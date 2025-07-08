from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Computed
from sqlalchemy.orm import relationship

from .database import Base 



##########################################################################
##########################################################################


class BasketballShotType(Base):
    __tablename__ = 'basketball_shot_types'
    shot_type_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    shots = relationship("BasketballShot", back_populates="shot_type")



##########################################################################
##########################################################################


class BasketballTeamStat(Base):
    __tablename__ = 'basketball_team_stats'
    team_id = Column(String, ForeignKey('teams.team_id', ondelete='CASCADE'), primary_key=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    opp_id = Column(String, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    minutes = Column(Integer, nullable=False)
    fga = Column(Integer, nullable=False)
    fgm = Column(Integer, nullable=False)
    fta = Column(Integer, nullable=False)
    ftm = Column(Integer, nullable=False)
    tpa = Column(Integer, nullable=False)
    tpm = Column(Integer, nullable=False)
    pts = Column(Integer, nullable=False)
    oreb = Column(Integer, nullable=False)
    dreb = Column(Integer, nullable=False)
    ast = Column(Integer, nullable=False)
    stl = Column(Integer, nullable=False)
    blk = Column(Integer, nullable=False)
    turnovers = Column(Integer, nullable=False)
    fouls = Column(Integer, nullable=False)
    pts_in_pt = Column(Integer, nullable=True)
    possessions = Column(Integer, Computed('fga + 0.44 * fta - oreb + turnovers'))

    team = relationship("Team", foreign_keys=[team_id])
    game = relationship("Game")
    opponent = relationship("Team", foreign_keys=[opp_id])



##########################################################################
##########################################################################


class BasketballPlayerStat(Base):
    __tablename__ = 'basketball_player_stats'
    player_id = Column(String, ForeignKey('players.player_id', ondelete='CASCADE'), primary_key=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    team_id = Column(String, ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=False)
    opp_id = Column(String, ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=False)
    starter = Column(Boolean, default=False, nullable=False)
    minutes = Column(Float, nullable=False)
    fga = Column(Integer, nullable=False)
    fgm = Column(Integer, nullable=False)
    fta = Column(Integer, nullable=False)
    ftm = Column(Integer, nullable=False)
    tpa = Column(Integer, nullable=False)
    tpm = Column(Integer, nullable=False)
    pts = Column(Integer, nullable=False)
    oreb = Column(Integer, nullable=False)
    dreb = Column(Integer, nullable=False)
    ast = Column(Integer, nullable=False)
    stl = Column(Integer, nullable=False)
    blk = Column(Integer, nullable=False)
    turnovers = Column(Integer, nullable=False)
    fouls = Column(Integer, nullable=False)
    plus_minus = Column(Integer, nullable=True)

    player = relationship("Player")
    team = relationship("Team", foreign_keys=[team_id])
    game = relationship("Game")
    opponent = relationship("Team", foreign_keys=[opp_id])



##########################################################################
##########################################################################



class BasketballShot(Base):
    __tablename__ = 'basketball_shots'
    player_shot_id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), nullable=False)
    player_id = Column(String, ForeignKey('players.player_id', ondelete='CASCADE'), nullable=False)
    team_id = Column(String, ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=False)
    opp_id = Column(String, ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=False)
    period = Column(Integer, nullable=False)
    shot_type_id = Column(Integer, ForeignKey('basketball_shot_types.shot_type_id', ondelete='SET NULL'), nullable=False)
    assist_id = Column(String, ForeignKey('players.player_id', ondelete='SET NULL'), nullable=True)
    shot_made = Column(Boolean, nullable=False)
    points = Column(Integer, nullable=False)
    base_pct = Column(Float, nullable=False)
    side_pct = Column(Float, nullable=False)
    distance = Column(Integer, nullable=False)
    side_of_basket = Column(String, nullable=False)
    clutch = Column(String, nullable=True)
    zone = Column(String, nullable=True)

    game = relationship("Game")
    player = relationship("Player", foreign_keys=[player_id])
    team = relationship("Team", foreign_keys=[team_id])
    opponent = relationship("Team", foreign_keys=[opp_id])
    assist_player = relationship("Player", foreign_keys=[assist_id])
    shot_type = relationship("BasketballShotType", back_populates="shots")




##########################################################################
##########################################################################