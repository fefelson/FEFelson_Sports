from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base 



##############################################################################
##############################################################################



class GameLine(Base):
    __tablename__ = 'game_lines'
    team_id = Column(String, ForeignKey('teams.team_id', ondelete='CASCADE'), primary_key=True)
    opp_id = Column(String, ForeignKey('teams.team_id', ondelete='CASCADE'), nullable=False)
    game_id = Column(String, ForeignKey('games.game_id', ondelete='CASCADE'), primary_key=True)
    spread = Column(Float, nullable=False)
    spread_line = Column(Integer, default=-110)
    money_line = Column(Integer, nullable=True)
    result = Column(Integer, nullable=False)
    spread_outcome = Column(Integer, nullable=True)
    money_outcome = Column(Integer, nullable=False)

    team = relationship("Team", foreign_keys=[team_id])
    opponent = relationship("Team", foreign_keys=[opp_id])
    game = relationship("Game")



##############################################################################
##############################################################################



class OverUnder(Base):
    __tablename__ = 'over_unders'
    game_id = Column(String, ForeignKey('games.game_id'), primary_key=True)
    over_under = Column(Float, nullable=False)
    over_line = Column(Integer, default=-110)
    under_line = Column(Integer, default=-110)
    total = Column(Integer, nullable=False)
    ou_outcome = Column(Integer, nullable=False)

    game = relationship("Game")