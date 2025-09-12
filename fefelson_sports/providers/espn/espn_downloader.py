from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import json
import re 
from time import sleep

from ...utils.logging_manager import get_logger

# for debugging
from pprint import pprint 


######################################################################
######################################################################


BASE_URL = "https://www.espn.com"


espnSlugs = {"NBA": "nba", "NCAAB": "mens-college-basketball", "MLB": "mlb", 
                "NCAAF": "college-football", "NFL": "nfl"}


######################################################################
######################################################################

#logger = get_logger()

class ESPNDownloadAgent:

    def __init__(self, leagueId):
        self.leagueId = leagueId

   
    def _fetch_url(self, url: str, sleepTime: int = 10, attempts: int = 3) -> Dict[str, Any]:
        """
        Recursive function to download yahoo url and isolate json
        Or write to errorFile
        """
        item = {}
        try:
            html = urlopen(url)
            for line in [x.decode("utf-8") for x in html.readlines()]:
                if "window['__CONFIG__']=" in line:
                    item = json.loads("".join(line.split("window['__espnfitt__']=")[1].split(";</script>")[:-1]))
        
        except (URLError, HTTPError, ValueError) as e:
            #logger.error(e)
            # time.sleep(sleepTime)
            if 'odds' not in url:
                get_logger().error(f"{url} {e}")
        return item
    

    def fetch_scoreboard(self, gameDate: str) -> dict:
        url = f"{BASE_URL}/{espnSlugs[self.leagueId]}/scoreboard"
               
        if gameDate is not None:
            date = f"date/{''.join(gameDate.split('-'))}"
            url = f"{url}/_/{date}"  
  
        data = self._fetch_url(url)
        data["provider"] = "espn"
        return data
    

    def fetch_boxscore(self, url: str) -> dict:
        if BASE_URL not in url:
            url = f"{BASE_URL}{url}"
        
        pbpUrl = re.sub("game", "playbyplay", url, 1)
        boxUrl = re.sub("game", "boxscore", url, 1)
        matchUrl = re.sub("game", "matchup", url, 1)
        game = self._fetch_url(url)["page"]["content"]["gamepackage"]
        pbp = self._fetch_url(pbpUrl)["page"]["content"]["gamepackage"]
        box = self._fetch_url(boxUrl)["page"]["content"]["gamepackage"]
        match = self._fetch_url(matchUrl)["page"]["content"]["gamepackage"]
        data = {"boxData":box, "pbpData":pbp, "gameData":game, "matchData":match, "provider":"espn"}

        return data


    def fetch_matchup(self, url: str) -> dict:
        if BASE_URL not in url:
            url = f"{BASE_URL}{url}"
        
        oddsUrl = re.sub("game", "odds", url, 1)

        game = self._fetch_url(url)["page"]["content"]["gamepackage"]
        try:
            odds = self._fetch_url(oddsUrl)["page"]["content"]["gamepackage"]
        except:
            odds = None
    
        data = {"oddsData":odds, "gameData":game, "provider":"espn"}

        return data
        


class ESPNNFLDownloadAgent(ESPNDownloadAgent):

    def __init__(self, leagueId):
        super().__init__(leagueId)


    def fetch_scoreboard(self, gameDate: str) -> dict:
        url = f"{BASE_URL}/{espnSlugs[self.leagueId]}/scoreboard"
               
        if gameDate is not None:
            w = int(gameDate.split('_')[-1])
            s = 2
            if w > 18:
                w = w-18
                seasonType = 3
            week = f"week/{w}"
            seasonType = f"seasontype/{s}"
            year = f"year/{gameDate.split('_')[0]}"
            url = f"{url}/_/{week}/{year}/{seasonType}"  
 
        data = self._fetch_url(url)
        data["provider"] = "espn"
        return data


class ESPNNCAAFDownloadAgent(ESPNDownloadAgent):

    def __init__(self, leagueId):
        super().__init__(leagueId)


    def fetch_scoreboard(self, gameDate: str) -> dict:
        url = f"{BASE_URL}/{espnSlugs[self.leagueId]}/scoreboard/_/group/80"
               
        if gameDate is not None:
            w = int(gameDate.split('_')[-1])
            s = 2
            if w > 16:
                w = w-16
                s = 3
            week = f"week/{w}"
            seasonType = f"seasontype/{s}"
            year = f"year/{gameDate.split('_')[0]}"
            url = f"{url}/{week}/{year}/{seasonType}" 

        data = self._fetch_url(url)
        data["provider"] = "espn"
        return data


class ESPNNCAABDownloadAgent(ESPNDownloadAgent):

    def __init__(self, leagueId):
        super().__init__(leagueId)


    def fetch_scoreboard(self, gameDate: str) -> dict:
        url = f"{BASE_URL}/{espnSlugs[self.leagueId]}/scoreboard/_/group/50"
               
        if gameDate is not None:
            date = f"date/{''.join(gameDate.split('-'))}/"
            url = f"{url}/{date}" 
        
        data = self._fetch_url(url)
        data["provider"] = "espn"
        return data

       

    
