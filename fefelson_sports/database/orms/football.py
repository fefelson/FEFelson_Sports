from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship

from .database import Base 


##########################################################################
##########################################################################


class FootballTeamStat(Base):
    __tablename__ = 'football_team_stats'
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), primary_key=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    pts = Column(Integer, nullable=False)
    drives = Column(Integer, nullable=True)
    yards = Column(Integer, nullable=False)
    pass_plays = Column(Integer, nullable=False)
    pass_yards = Column(Integer, nullable=False)
    rush_plays = Column(Integer, nullable=False)
    rush_yards = Column(Integer, nullable=False)
    int_thrown = Column(Integer, nullable=False)
    fum_lost = Column(Integer, nullable=False)
    times_sacked = Column(Integer, nullable=True)
    sack_yds_lost = Column(Integer, nullable=True)
    penalties = Column(Integer, nullable=False)
    penalty_yards = Column(Integer, nullable=False)
    time_of_poss = Column(Float, nullable=False)
    third_att = Column(Integer, nullable=False)
    third_conv = Column(Integer, nullable=False)
    fourth_att = Column(Integer, nullable=False)
    fourth_conv = Column(Integer, nullable=False)
    rz_att = Column(Integer, nullable=True)
    rz_conv = Column(Integer, nullable=True)

    game = relationship("Game", foreign_keys=[game_id])
    team = relationship("Team", foreign_keys=[team_id])
    opp = relationship("Team", foreign_keys=[opp_id])



##########################################################################
##########################################################################


class PassPlay(Base):
    __tablename__ = 'pass_plays'
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    play_num = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    period = Column(Integer, nullable=False)
    down = Column(Integer, nullable=False)
    distance = Column(Integer, nullable=False)
    clock = Column(Float, nullable=False)
    yards_to_endzone = Column(Integer, nullable=False)
    quarterback = Column(Integer, ForeignKey('players.player_id', ondelete='SET NULL'), nullable=False)
    target = Column(Integer, ForeignKey('players.player_id', ondelete='SET NULL'), nullable=True)
    yards = Column(Integer, nullable=False)
    direction = Column(Integer, nullable=False)
    completed = Column(Boolean, nullable=False)
    touchdown = Column(Boolean, nullable=False)
    intercepted = Column(Boolean, nullable=False)

    qb = relationship("Player", foreign_keys=[quarterback])
    wr = relationship("Player", foreign_keys=[target])
   
    
##########################################################################
##########################################################################


class RushPlay(Base):
    __tablename__ = 'rush_plays'
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    play_num = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    period = Column(Integer, nullable=False)
    down = Column(Integer, nullable=False)
    distance = Column(Integer, nullable=False)
    clock = Column(Float, nullable=False)
    yards_to_endzone = Column(Integer, nullable=False)
    rusher = Column(Integer, ForeignKey('players.player_id', ondelete='SET NULL'), nullable=False)
    yards = Column(Integer, nullable=False)
    direction = Column(Integer, nullable=False)
    touchdown = Column(Boolean, nullable=False)

    rb = relationship("Player", foreign_keys=[rusher])

##########################################################################
##########################################################################


class KickPlay(Base):
    __tablename__ = 'kick_plays'
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    play_num = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    period = Column(Integer, nullable=False)
    down = Column(Integer, nullable=False)
    distance = Column(Integer, nullable=False)
    clock = Column(Float, nullable=False)
    kicker = Column(Integer, ForeignKey('players.player_id', ondelete='SET NULL'), nullable=False)
    yards = Column(Integer, nullable=False)
    kick_good = Column(Boolean, nullable=False)
    kick_blocked = Column(Boolean, nullable=False)

    k = relationship("Player", foreign_keys=[kicker])


##########################################################################
##########################################################################


class FootballPassing(Base):
    __tablename__ = 'passing'
    player_id = Column(Integer, ForeignKey('players.player_id', ondelete='CASCADE'), primary_key=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    pass_att = Column(Integer, nullable=False)
    pass_comp = Column(Integer, nullable=False)
    pass_yds = Column(Integer, nullable=False)
    pass_td = Column(Integer, nullable=False)
    pass_int = Column(Integer, nullable=False)
    sacks = Column(Integer, nullable=False)
    sack_yds_lost = Column(Integer, nullable=False)


##########################################################################
##########################################################################


class FootballRushing(Base):
    __tablename__ = 'rushing'
    player_id = Column(Integer, ForeignKey('players.player_id', ondelete='CASCADE'), primary_key=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    rush_att = Column(Integer, nullable=False)
    rush_yds = Column(Integer, nullable=False)
    rush_td = Column(Integer, nullable=False)


##########################################################################
##########################################################################


class FootballReceiving(Base):
    __tablename__ = 'receiving'
    player_id = Column(Integer, ForeignKey('players.player_id', ondelete='CASCADE'), primary_key=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    tgt = Column(Integer, nullable=True)
    rec = Column(Integer, nullable=False)
    rec_yds = Column(Integer, nullable=False)
    rec_td = Column(Integer, nullable=False)
    yac = Column(Integer, nullable=True)
    rec_1d = Column(Integer, nullable=True)


##########################################################################
##########################################################################


class FootballFumbles(Base):
    __tablename__ = 'fumbles'
    player_id = Column(Integer, ForeignKey('players.player_id', ondelete='CASCADE'), primary_key=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    fum_lost = Column(Integer, nullable=False)


##########################################################################
##########################################################################


class FootballKicking(Base):
    __tablename__ = 'kicks'
    player_id = Column(Integer, ForeignKey('players.player_id', ondelete='CASCADE'), primary_key=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    fga = Column(Integer, nullable=False)
    fgm = Column(Integer, nullable=False)
    


##########################################################################
##########################################################################


class FootballPunting(Base):
    __tablename__ = 'punts'
    player_id = Column(Integer, ForeignKey('players.player_id', ondelete='CASCADE'), primary_key=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    punts = Column(Integer, nullable=False)
    punt_yds = Column(Integer, nullable=False)
    in20 = Column(Integer, nullable=True)
    touchback = Column(Integer, nullable=True)


##########################################################################
##########################################################################



class FootballReturns(Base):
    __tablename__ = 'kick_returns'
    player_id = Column(Integer, ForeignKey('players.player_id', ondelete='CASCADE'), primary_key=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    kr = Column(Integer, nullable=False)
    kr_yds = Column(Integer, nullable=False)
    kr_td = Column(Integer, nullable=False)
    pr = Column(Integer, nullable=False)
    pr_yds = Column(Integer, nullable=False)
    pr_td = Column(Integer, nullable=False)
    

##########################################################################
##########################################################################


class FootballDefense(Base):
    __tablename__ = 'defense'
    player_id = Column(Integer, ForeignKey('players.player_id', ondelete='CASCADE'), primary_key=True)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    opp_id = Column(Integer, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    tackles = Column(Integer, nullable=False)
    sacks = Column(Float, nullable=False)
    ints = Column(Integer, nullable=False)
    pass_def = Column(Integer, nullable=False)
    qb_hits = Column(Integer, nullable=False)
    

##########################################################################
########################################################################## 