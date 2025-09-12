from .boxscores import Boxscore
from .matchups import Matchup
from .schedules import DailySchedule, WeeklySchedule
from .scoreboards import Scoreboard

from ..analytics import MLBAnalytics, NBAAnalytics, NCAABAnalytics, NCAAFAnalytics, NFLAnalytics
from ..database.agents import MLBAlchemy, NBAAlchemy, NCAABAlchemy, NCAAFAlchemy, NFLAlchemy
from ..database.orms.database import get_db_session
from ..utils.logging_manager import get_logger

# for debugging
# from pprint import pprint 

################################################################################
################################################################################

 
class League:


    def __init__(self, leagueId, dbAgent, schedule, analytics):
        
        self.leagueId = leagueId 

        self.analytics = analytics()
        self.boxscore = Boxscore(leagueId) 
        self.dbAgent = dbAgent()
        self.matchup = Matchup(leagueId) 
        self.schedule = schedule(leagueId)
        self.scoreboard = Scoreboard(leagueId)



    def process_game_date(self, gameDate: str):
        get_logger().info(f"{self.leagueId} processing {gameDate}")
    
        with get_db_session() as session:
            for game in self.scoreboard.process(gameDate).values():
                if game["status"] == "pregame":
                    self.matchup.process(game, session)
                elif game["status"] == "final":
                    bScore = self.boxscore.process(game, session)
                    if bScore:
                        self.dbAgent.insert_boxscore(bScore, session)
        
                            
    def update(self):
        if self.schedule.is_active():
            if not self.schedule.is_up_to_date():
                get_logger().info(f"Updating {self.leagueId}") 
                for gameDate in self.schedule.get_back_dates():
                    self.process_game_date(gameDate)
                    self.schedule.current_until(gameDate)
                    get_logger().info(f"{self.leagueId} current up until {gameDate}")

                self.analytics.scheduled_analytics()    

            for gameDate in self.schedule.get_future_dates(2):
                self.process_game_date(gameDate)
                get_logger().debug(f"{self.leagueId} matchups processed for {gameDate}")
            
            self.matchup.clean_files()

            get_logger().debug(f"{self.leagueId} is up to date")


####################################################################
####################################################################


class MLB(League):


    def __init__(self):
        super().__init__("MLB", MLBAlchemy, DailySchedule, MLBAnalytics)



####################################################################
####################################################################


class NBA(League):


    def __init__(self):
        super().__init__("NBA", NBAAlchemy, DailySchedule, NBAAnalytics)



####################################################################
####################################################################


class NCAAB(League):


    def __init__(self):
        super().__init__("NCAAB", NCAABAlchemy, DailySchedule, NCAABAnalytics)



####################################################################
####################################################################


class NCAAF(League):


    def __init__(self):
        super().__init__("NCAAF", NCAAFAlchemy, WeeklySchedule, NCAAFAnalytics)



####################################################################
####################################################################


class NFL(League):


    def __init__(self):
        super().__init__("NFL", NFLAlchemy, WeeklySchedule, NFLAnalytics)



####################################################################
####################################################################

