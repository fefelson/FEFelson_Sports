from typing import List
from ..capabilities.fileable import JSONAgent
from ..capabilities import Downloadable, Normalizable, Processable
from ..providers import get_download_agent, get_normal_agent # factory methods
from ..utils.logging_manager import get_logger


####################################################################
####################################################################


class Scoreboard(Downloadable, Normalizable, Processable):

    def __init__(self, leagueId: str):
        self.leagueId = leagueId
        self.logger = get_logger()


    def normalize(self, webData: dict) -> dict:
        normalAgent = get_normal_agent(self.leagueId, webData["provider"])
        return normalAgent.normalize_scoreboard(webData)


    def process(self, gameDate: str) -> List[dict]:
        self.logger.debug(f"{self.leagueId} Scoreboard processing {gameDate}")
        
        workbook = {}    
        for provider in ("yahoo", "espn"):
            webData = self.download(gameDate, provider)
            workbook[provider] = self.normalize(webData)

        scoreboard = {}
        for game in workbook["yahoo"]["games"]:
            gameId = game["gameId"].split(".")[-1]
            if game['gameType'] != "preseason":
                scoreboard[gameId] = {}
                scoreboard[gameId]["yahoo"] = game 
                for espnGame in workbook["espn"]["games"]:
                    if espnGame["homeId"] == game["homeId"].split(".")[-1] and espnGame["awayId"] == game["awayId"].split(".")[-1] and espnGame["gameTime"] == game["gameTime"]:
                        scoreboard[gameId]["espn"] = espnGame 
                        

        # from pprint import pprint 
        # pprint(scoreboard)
        # raise 
        return scoreboard


    def download(self, gameDate, provider):
        downloadAgent = get_download_agent(self.leagueId, provider)
        return downloadAgent.fetch_scoreboard(self.leagueId, gameDate)

    
