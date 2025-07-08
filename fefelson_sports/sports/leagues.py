from ..config.config_manager import LeagueConfig
from ..analytics.analytics import NBAAnalytics, NCAABAnalytics, MLBAnalytics
from ..models.leagues import League
from ..models.schedules import DailySchedule
from ..capabilities.databaseable import SQLAlchemyDatabaseAgent, MLBAlchemy



####################################################################
####################################################################


class NBA(League):

    _leagueId = "NBA"
    _dbAgent = SQLAlchemyDatabaseAgent
    _leagueConfig = LeagueConfig(_leagueId)
    _analytics = NBAAnalytics()    
    _schedule = DailySchedule



####################################################################
####################################################################


class NCAAB(League):

    _leagueId = "NCAAB"
    _dbAgent = SQLAlchemyDatabaseAgent
    _leagueConfig = LeagueConfig(_leagueId)   
    _analytics = NCAABAnalytics()  
    _schedule = DailySchedule


####################################################################
####################################################################


class MLB(League):

    _leagueId = "MLB"
    _dbAgent = MLBAlchemy
    _leagueConfig = LeagueConfig(_leagueId)
    _analytics = MLBAnalytics()    
    _schedule = DailySchedule

