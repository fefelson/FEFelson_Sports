from copy import deepcopy
from datetime import datetime
from re import sub 

from ..database.stores.base import ProviderStore
from ..database.stores.core import TeamStore
from ..providers import get_download_agent, get_normal_agent # factory methods

# for debugging
from pprint import pprint 


####################################################################
####################################################################

gameTemplate = {
    "title": None,
    "leagueId": None,
    "homeId": None,
    "awayId": None,
    "gameTime": None,
    "gameType": None,
    "status": None,
    "odds": None,
    "season": None,
    "week": None,
    "gameIds": {},
    "urls": {},
    "all_star_game": None
    }


class Scoreboard:

    def __init__(self, leagueId: str):
        self.leagueId = leagueId
        self.providerStore = ProviderStore()
        self.teamStore = TeamStore()


    def download(self, gameDate: str, provider: str) -> dict:
        downloadAgent = get_download_agent(self.leagueId, provider)
        return downloadAgent.fetch_scoreboard(gameDate)


    def normalize(self, webData: dict) -> dict:
        normalAgent = get_normal_agent(self.leagueId, webData["provider"])
        return normalAgent.normalize_scoreboard(webData)


    def process(self, gameDate: str=None) -> dict:
        
        scoreboard = {}    
        for provider in self.providerStore.get_providers():

            webData = self.download(gameDate, provider)
            scoreBoardData = self.normalize(webData)

            for game in scoreBoardData["games"]:

                awayId = self.providerStore.get_inside_id(provider, self.leagueId, "team", game["awayId"])
                homeId = self.providerStore.get_inside_id(provider, self.leagueId, "team", game["homeId"])

                awayTeam = self.teamStore.get_team_info(awayId)
                awayName = " ".join([awayTeam[key] for key in ("first_name", "last_name")])  if awayTeam else "NA"
                homeTeam = self.teamStore.get_team_info(homeId)
                homeName = " ".join([homeTeam[key] for key in ("first_name", "last_name")]) if homeTeam else "NA"
                gameTime = datetime.fromisoformat(game["gameTime"])
                label = f"{self.leagueId}_{gameTime.strftime('%b_%d_%Y')}_{awayName}_at_{homeName}"
                #fixing first name spaces in label
                label = sub(' ', '_', label)

                newGame = scoreboard.get(label, deepcopy(gameTemplate))
                newGame["title"] = label
                newGame["leagueId"] = self.leagueId
                newGame["awayId"] = awayId
                newGame["homeId"] = homeId
                newGame["gameIds"][provider] = game["gameId"]
                newGame["urls"][provider] = game["url"]

                for item in ("all_star_game", "gameTime", "gameType", "status", "odds", "season", "week"):
                    if newGame[item] is None and game.get(item) != None:
                        newGame[item] = game[item]
                scoreboard[label] = newGame
        # pprint(scoreboard)
        return scoreboard


    

    
