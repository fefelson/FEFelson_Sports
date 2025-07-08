from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base 


class PitchResultType(Base):
    __tablename__ = "pitch_result_types"
    pitch_result_name = Column(String, primary_key=True)
    pitch_result_id = Column(Integer, unique=True, nullable=False)
    is_strike = Column(Boolean, nullable=False)
    is_swing = Column(Boolean, nullable=False)
    is_contact = Column(Boolean, nullable=False)


class PitchType(Base):
    __tablename__ = "pitch_types"
    pitch_type_name = Column(String, primary_key=True)
    pitch_type_id = Column(Integer, unique=True, nullable=False)


class ContactType(Base):
    __tablename__ = "contact_types"
    contact_type_id = Column(Integer, primary_key=True)
    at_bat_type_id = Column(Integer, ForeignKey('at_bat_types.at_bat_type_id', ondelete='CASCADE'), nullable=False)

    atBatTypes = relationship("AtBatType", foreign_keys=[at_bat_type_id])


class SwingResult(Base):
    __tablename__ = "swing_results"
    swing_result_id = Column(Integer, primary_key=True)
    pitch_result_name = Column(String, ForeignKey('pitch_result_types.pitch_result_name', ondelete='CASCADE'), nullable=False)

    pitchResultTypes = relationship("PitchResultType", foreign_keys=[pitch_result_name])    
    

class AtBatType(Base):
    __tablename__ = 'at_bat_types'
    at_bat_type_id = Column(Integer, primary_key=True)
    at_bat_type_name = Column(String, nullable=False)
    is_pa = Column(Boolean, nullable=False)
    is_ab = Column(Boolean, nullable=False)
    is_ob = Column(Boolean, nullable=False)
    is_hit = Column(Boolean, nullable=False)
    num_bases = Column(Integer, nullable=False)

    atBats = relationship("AtBat", back_populates="atbatResult")


##########################################################################
##########################################################################


class Pitch(Base):
    __tablename__ = 'pitches'
    pitch_id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), nullable=False)
    pitcher_id = Column(String, ForeignKey('players.player_id', ondelete='CASCADE'), nullable=False)
    batter_id = Column(String, ForeignKey('players.player_id', ondelete='CASCADE'), nullable=False)
    team_id = Column(String, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    opp_id = Column(String, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    play_num = Column(String, nullable=False)
    pitch_count = Column(Integer, nullable=False)
    sequence = Column(Integer, nullable=False)
    balls = Column(Integer, nullable=False)
    strikes = Column(Integer, nullable=False)
    velocity = Column(Integer, nullable=False)
    pitch_x = Column(Integer, nullable=False)
    pitch_y = Column(Integer, nullable=False)
    pitch_location = Column(Integer, nullable=False)
    hit_x = Column(Integer, nullable=True)
    hit_y = Column(Integer, nullable=True)
    pitch_type_name=  Column(String, ForeignKey('pitch_types.pitch_type_name', ondelete='CASCADE'), nullable=False)
    ab_result_name = Column(String, nullable=True)
    pitch_result_name = Column(String, ForeignKey('pitch_result_types.pitch_result_name', ondelete='CASCADE'), nullable=False)
    
    game = relationship("Game")
    team = relationship("Team", foreign_keys=[team_id])
    opponent = relationship("Team", foreign_keys=[opp_id])
    batter = relationship("Player", foreign_keys=[batter_id])
    pitcher = relationship("Player", foreign_keys=[pitcher_id])
    pitch_types = relationship("PitchType", foreign_keys=[pitch_type_name])
    pitch_results = relationship("PitchResultType", foreign_keys=[pitch_result_name])
    

##########################################################################
##########################################################################


class AtBat(Base):
    __tablename__ = 'at_bats'
    at_bat_id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), nullable=False)
    team_id = Column(String, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    opp_id = Column(String, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    play_num = Column(String, nullable=False)
    pitcher_id = Column(String, ForeignKey('players.player_id', ondelete='CASCADE'), nullable=False)
    batter_id = Column(String, ForeignKey('players.player_id', ondelete='CASCADE'), nullable=False)
    at_bat_type_id = Column(Integer, ForeignKey('at_bat_types.at_bat_type_id', ondelete='CASCADE'), nullable=False)
    hit_hardness = Column(Integer, nullable=True)
    hit_style =  Column(Integer, nullable=True)
    hit_distance = Column(Integer, nullable=True)
    hit_angle =  Column(Integer, nullable=True)
    period = Column(Integer, nullable=False)

    game = relationship("Game")
    team = relationship("Team", foreign_keys=[team_id])
    opponent = relationship("Team", foreign_keys=[opp_id])
    batter = relationship("Player", foreign_keys=[batter_id])
    pitcher = relationship("Player", foreign_keys=[pitcher_id])
    atbatResult = relationship("AtBatType", back_populates="atBats")


##########################################################################
##########################################################################


class BattingOrder(Base):
    __tablename__ = 'baseball_lineup'
    lineup_id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), nullable=False)
    player_id = Column(String, ForeignKey('players.player_id', ondelete='CASCADE'), nullable=False)
    team_id = Column(String, ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=False)
    opp_id = Column(String, ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=False)
    batt_order = Column(Integer, nullable=False)
    sub_order = Column(Integer, nullable=True)
    pos = Column(String, nullable=True)

    game = relationship("Game")
    player = relationship("Player", foreign_keys=[player_id])
    team = relationship("Team", foreign_keys=[team_id])
    opponent = relationship("Team", foreign_keys=[opp_id])


##########################################################################
##########################################################################


class Bullpen(Base):
    __tablename__ = 'baseball_bullpen'
    lineup_id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), nullable=False)
    player_id = Column(String, ForeignKey('players.player_id', ondelete='CASCADE'), nullable=False)
    team_id = Column(String, ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=False)
    opp_id = Column(String, ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=False)
    pitch_order = Column(Integer, nullable=False)

    game = relationship("Game")
    player = relationship("Player", foreign_keys=[player_id])
    team = relationship("Team", foreign_keys=[team_id])
    opponent = relationship("Team", foreign_keys=[opp_id])



##########################################################################
##########################################################################


class BaseballTeamStat(Base):
    __tablename__ = 'baseball_team_stats'
    team_id = Column(String, ForeignKey('teams.team_id', ondelete='CASCADE'), primary_key=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    opp_id = Column(String, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    runs = Column(Integer, nullable=False)
    hits = Column(Integer, nullable=False)
    errors = Column(Integer, nullable=False)
    
    team = relationship("Team", foreign_keys=[team_id])
    game = relationship("Game")
    opponent = relationship("Team", foreign_keys=[opp_id])


##########################################################################
##########################################################################

