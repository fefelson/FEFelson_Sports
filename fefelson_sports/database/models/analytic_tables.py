from sqlalchemy import Column, ForeignKey, Integer, String, Numeric, Date

from .database import Base

class StatMetric(Base):
    __tablename__ = 'stat_metrics'
    league_id = Column(String, ForeignKey('leagues.league_id', ondelete='CASCADE'), primary_key=True)
    entity_type = Column(String, primary_key=True) # player, game, team
    entity_id = Column(String, primary_key=True)  # e.g., 'player123'
    timeframe = Column(String, primary_key=True)  # e.g., 'daily', '7d', 'all-time'
    metric_name = Column(String, primary_key=True)            # e.g., 'avg_points'
    value = Column(Numeric)                 # The average value
    reference_date = Column(Date)           # e.g., '2025-03-22'

   


class LeagueMetric(Base):
    __tablename__ = 'league_metrics'
    league_id = Column(String, ForeignKey('leagues.league_id', ondelete='CASCADE'), primary_key=True)
    entity_type = Column(String, primary_key=True)  # e.g., 'player', 'game'
    timeframe = Column(String, primary_key=True)  # e.g., 'daily', '7d', 'all-time'
    metric_name = Column(String, primary_key=True)            # e.g., 'avg_points'
    best_value = Column(Numeric)                 # The average value
    worst_value = Column(Numeric)                 # The average value
    q1 = Column(Numeric)                 # quantile1
    q2 = Column(Numeric)                 # quantile2
    q4 = Column(Numeric)                 # quantile4
    q6 = Column(Numeric)                 # quantile6
    q8 = Column(Numeric)                 # quantile8
    q9 = Column(Numeric)                 # quantile9
    reference_date = Column(Date)           # e.g., '2025-03-22'