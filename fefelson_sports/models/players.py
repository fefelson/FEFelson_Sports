from typing import Any, Dict

from ..providers import get_download_agent, get_normal_agent
from ..utils.logging_manager import get_logger


######################################################################
######################################################################




######################################################################
######################################################################



class Player:


    def __init__(self, leagueId: str):
        super().__init__()

        self.leagueId = leagueId


    def download(self, playerId: str) -> Dict[str, Any]:
        downloadAgent = get_download_agent(self.leagueId)
        return downloadAgent.fetch_player(self.leagueId, playerId)


    def normalize(self, webData: dict) -> Dict[str, Any]:
        if webData is None:
            return None
        normalAgent = get_normal_agent(self.leagueId, webData["provider"])
        return normalAgent.normalize_player(webData)


    def process(self, playerId: str) :
        get_logger().debug(f"processing Player {playerId}")
        webData = self.download(playerId)
        player = self.normalize(webData)
        return player        


    
