from ..database.stores.base import ProviderStore
from ..database.stores.core import GameStore
from ..providers import get_download_agent, get_normal_agent
from ..utils.logging_manager import get_logger

# for debugging
# from pprint import pprint 

######################################################################
######################################################################


class Boxscore():

    def __init__(self, leagueId: str):
        super().__init__()

        self.leagueId = leagueId
        self.gameStore = GameStore()
        self.providerStore = ProviderStore()


    def download(self, provider: str, url: str) -> dict:
        downloadAgent = get_download_agent(self.leagueId, provider)
        try:
            webData = downloadAgent.fetch_boxscore(url)
        except KeyError:
            webData = None
        return webData


    def normalize(self, webData: dict) -> dict:
        if webData is None:
            return None
        normalAgent = get_normal_agent(self.leagueId, webData["provider"])
        return normalAgent.normalize_boxscore(webData)


    def process(self, game: dict, session = None) -> dict:
        # pprint(game)

        gameId = self.gameStore.create_gameId(self.leagueId, game["homeId"], game["gameTime"])
        if (game["gameType"] in ("preseason", "spring training", "all-star") 
            or game["status"] in ("postponed",)
            or int(game["homeId"]) == -1 or int(game["awayId"]) == -1
            or self.gameStore.get_by_id(gameId, session)):
            return None 

        get_logger().debug(f"processing Boxscore {game['title']}")
        
        boxScores = {}        
        boxScores["game_id"] = gameId
        boxScores["home_id"] = game["homeId"]
        boxScores["away_id"] = game["awayId"]
        
        for provider, url in game["urls"].items():
            webData = self.download(provider, url)
            boxScores[provider] = self.normalize(webData)
        return boxScores
 




       
          



    
