from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship

from .database import Base 


##########################################################################
##########################################################################


class BaseballTeamStat(Base):
    __tablename__ = 'baseball_team_stats'
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), primary_key=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    ab = Column(Integer, nullable=False)
    bb = Column(Integer, nullable=False)
    r = Column(Integer, nullable=False)
    h = Column(Integer, nullable=False)
    hr = Column(Integer, nullable=False)
    rbi = Column(Integer, nullable=False)
    sb = Column(Integer, nullable=False)
    lob = Column(Integer, nullable=False)
    full_ip = Column(Integer, nullable=False)
    partial_ip = Column(Integer, nullable=False)
    bba = Column(Integer, nullable=False)
    ha = Column(Integer, nullable=False)
    ra = Column(Integer, nullable=False)
    hra = Column(Integer, nullable=False)
    er = Column(Integer, nullable=False)
    k = Column(Integer, nullable=False)
    errors = Column(Integer, nullable=False)
    
    game = relationship("Game", foreign_keys=[game_id])
    team = relationship("Team", foreign_keys=[team_id])  
    opp = relationship("Team", foreign_keys=[opp_id])



##########################################################################
##########################################################################


class PitchResultType(Base):
    __tablename__ = "pitch_result_types"
    pitch_result_name = Column(String, primary_key=True)
    pitch_result_id = Column(Integer, unique=True, nullable=False)
    is_strike = Column(Boolean, nullable=False)
    is_swing = Column(Boolean, nullable=False)
    is_contact = Column(Boolean, nullable=False)  
    

class AtBatType(Base):
    __tablename__ = 'at_bat_types'
    at_bat_type_id = Column(Integer, primary_key=True)
    at_bat_type_name = Column(String, nullable=False)
    is_pa = Column(Boolean, nullable=False)
    is_ab = Column(Boolean, nullable=False)
    is_ob = Column(Boolean, nullable=False)
    is_hit = Column(Boolean, nullable=False)
    num_bases = Column(Integer, nullable=False)


##########################################################################
##########################################################################


class Pitch(Base):
    __tablename__ = 'pitches'
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    play_num = Column(String, primary_key=True)
    pitcher_id = Column(Integer, ForeignKey('players.player_id', ondelete='CASCADE'), nullable=False)
    batter_id = Column(Integer, ForeignKey('players.player_id', ondelete='CASCADE'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    pitch_count = Column(Integer, nullable=False)
    sequence = Column(Integer, nullable=False)
    balls = Column(Integer, nullable=False)
    strikes = Column(Integer, nullable=False)
    velocity = Column(Integer, nullable=False)
    pitch_x = Column(Integer, nullable=False)
    pitch_y = Column(Integer, nullable=False)
    pitch_location = Column(Integer, nullable=False)
    pitch_type_name=  Column(String, nullable=False)
    ab_result_name = Column(String, nullable=True)
    pitch_result_name = Column(String, ForeignKey('pitch_result_types.pitch_result_name', ondelete='CASCADE'), nullable=False)
    

##########################################################################
##########################################################################


class AtBat(Base):
    __tablename__ = 'at_bats'
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    play_num = Column(String, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    pitcher_id = Column(Integer, ForeignKey('players.player_id', ondelete='CASCADE'), nullable=False)
    batter_id = Column(Integer, ForeignKey('players.player_id', ondelete='CASCADE'), nullable=False)
    at_bat_type_id = Column(Integer, ForeignKey('at_bat_types.at_bat_type_id', ondelete='CASCADE'), nullable=False)
    hit_hardness = Column(Integer, nullable=True)
    hit_style =  Column(Integer, nullable=True)
    hit_distance = Column(Integer, nullable=True)
    hit_angle =  Column(Integer, nullable=True)
    period = Column(Integer, nullable=False)


##########################################################################
##########################################################################


class BattingOrder(Base):
    __tablename__ = 'baseball_lineup'
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    player_id = Column(Integer, ForeignKey('players.player_id', ondelete='CASCADE'), primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    batt_order = Column(Integer, nullable=False)
    sub_order = Column(Integer, nullable=True)
    pos = Column(String, nullable=True)


##########################################################################
##########################################################################


class Bullpen(Base):
    __tablename__ = 'baseball_bullpen'
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    player_id = Column(Integer, ForeignKey('players.player_id', ondelete='CASCADE'), primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=False)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=False)
    pitch_order = Column(Integer, nullable=False)


##########################################################################
##########################################################################


class BattingStat(Base):
    __tablename__ = 'batting_stats'
    player_id = Column(Integer, ForeignKey('players.player_id', ondelete='CASCADE'), primary_key=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    ab = Column(Integer, nullable=False)
    bb = Column(Integer, nullable=False)
    r = Column(Integer, nullable=False)
    h = Column(Integer, nullable=False)
    hr = Column(Integer, nullable=False)
    rbi = Column(Integer, nullable=False)
    sb = Column(Integer, nullable=False)
    so = Column(Integer, nullable=False)


##########################################################################
##########################################################################


class PitchingStat(Base):
    __tablename__ = 'pitching_stats'
    player_id = Column(Integer, ForeignKey('players.player_id', ondelete='CASCADE'), primary_key=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    full_ip = Column(Integer, nullable=False)
    partial_ip = Column(Integer, nullable=False)
    bba  = Column(Integer, nullable=False)
    ha  = Column(Integer, nullable=False)
    hra  = Column(Integer, nullable=False)
    k = Column(Integer, nullable=False)
    ra  = Column(Integer, nullable=False)
    er = Column(Integer, nullable=False)
    w = Column(Integer, nullable=False)
    l  = Column(Integer, nullable=False)
    sv = Column(Integer, nullable=False)


##########################################################################
##########################################################################

