from copy import deepcopy
from re import sub 
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import json

#from ...utils.logging_manager import get_logger

# for debugging
from pprint import pprint 


######################################################################
######################################################################


BASE_URL = "https://sports.yahoo.com"


yahooSlugs = {"NBA": "nba", "NCAAB": "college-basketball", "MLB": "mlb", 
                "NCAAF": "college-football", "NFL": "nfl"}


######################################################################
######################################################################

#logger = get_logger()

class YahooDownloadAgent:

    def __init__(self, leagueId):
        self.leagueId = leagueId


    def _fetch_url(self, url: str, sleepTime: int = 10, attempts: int = 3) -> Dict[str, Any]:
        """
        Recursive function to download yahoo url and isolate json
        Or write to errorFile
        """
        try:
            html = urlopen(url)
            for line in [x.decode("utf-8") for x in html.readlines()]:
                if "root.App.main" in line:
                    item = json.loads(";".join(line.split("root.App.main = ")[1].split(";")[:-1]))
                    item = item["context"]["dispatcher"]["stores"]
        
        except (URLError, HTTPError, ValueError) as e:
            #logger.error(e)
            # time.sleep(sleepTime)
            YahooDownloadAgent._fetch_url(url, sleepTime, attempts)
        return item


    def _find_closing_bracket(self, s, start=0):
        if s[start] != '[':
            return -1
        count = 1
        for i in range(start + 1, len(s)):
            if s[i] == '[':
                count += 1
            elif s[i] == ']':
                count -= 1
                if count == 0:
                    return i
        return -1
    
 
    def fetch_scoreboard(self, gameDate: str) -> dict:
        confId = "confId"
        url = f"{BASE_URL}/{yahooSlugs[self.leagueId]}/scoreboard"

        if gameDate is not None:
            
            dateRange= f"&dateRange={gameDate}"
            url = f"{url}/?confId{dateRange}"       

        item = self._fetch_url(url)
        item["provider"] = "yahoo"
        return item 


    def fetch_player(self, leagueId:str, playerId: str):
        slugId = yahooSlugs[leagueId]
        url = f"{BASE_URL}/{slugId}/players/{playerId.split('.')[-1]}/"
        html = urlopen(url)
        data = None
        for line in [x.decode("utf-8").encode().decode("unicode_escape") for x in html.readlines()]:
            if "playerData" in line:
                for script in line.split("<script>")[1:]:
                    # pprint(script)
                    # print()
                    if 'self.__next_f.push([1,"51:' in script:
                        i = self._find_closing_bracket(script[27:])
                        data = json.loads(script[27:28+i])
                        # pprint(data)
                        data = data[-1]["children"][-1]["children"][-1]["children"][-1]["playerData"]        
                        data["provider"] = "yahoo"
        return data
    

    def fetch_boxscore(self, url: str) -> dict:
        if BASE_URL not in url:
            url = f"{BASE_URL}{url}"
        data = self._fetch_url(url)
        
        webData = {}
        webData["provider"] = "yahoo"
        gameId = data["PageStore"]["pageData"]["entityId"]
        webData["gameData"] = data["GamesStore"]["games"][gameId]
        webData["teamData"] = data["TeamsStore"]
        webData["playerData"] = data["PlayersStore"]
        webData["statsData"] = data["StatsStore"]
        
        return deepcopy(webData)


    def fetch_matchup(self, url: str) -> dict:
        return self.fetch_boxscore(url)


######################################################################
######################################################################


class YahooNFLDownloadAgent(YahooDownloadAgent):

    def __init__(self, leagueId):
        super().__init__(leagueId)


    def fetch_scoreboard(self, gameDate: str) -> dict:
        
        url = f"{BASE_URL}/{yahooSlugs[self.leagueId]}/scoreboard"

        if gameDate is not None:
            confId = "confId"
            dateRange= f"&dateRange={gameDate.split('_')[-1]}"
            scoreboardSeason= f"&scoreboardSeason={gameDate.split('_')[0]}"
            if int(gameDate.split('_')[-1]) <= 18:
                schedState="&schedState=2"
            else:
                schedState="&schedState=3"

            url = f"{url}?{confId}{dateRange}{schedState}{scoreboardSeason}"       
        
        item = self._fetch_url(url)
        item["provider"] = "yahoo"
        return item 


######################################################################
######################################################################


class YahooNCAAFDownloadAgent(YahooDownloadAgent):

    def __init__(self, leagueId):
        super().__init__(leagueId)


    def fetch_scoreboard(self, gameDate: str) -> dict:
        
        confId = "confId=1%2C4%2C6%2C7%2C8%2C11%2C71%2C72%2C87%2C90%2C122"
        url = f"{BASE_URL}/{yahooSlugs[self.leagueId]}/scoreboard?{confId}"

        if gameDate is not None:
            
            dateRange= f"&dateRange={gameDate.split('_')[-1]}"
            scoreboardSeason= f"&scoreboardSeason={gameDate.split('_')[0]}"
            if int(gameDate.split('_')[-1]) <= 16:
                schedState="&schedState=2"
            else:
                schedState="&schedState=3"

            url = f"{url}{dateRange}{schedState}{scoreboardSeason}"       

        item = self._fetch_url(url)
        item["provider"] = "yahoo"
        return item 


######################################################################
######################################################################


class YahooNCAABDownloadAgent(YahooDownloadAgent):

    def __init__(self, leagueId):
        super().__init__(leagueId)


    def fetch_scoreboard(self, gameDate: str) -> dict:
        
        confId = "confId=all"
        url = f"{BASE_URL}/{yahooSlugs[self.leagueId]}/scoreboard?{confId}"

        if gameDate is not None:
            
            dateRange= f"&dateRange={gameDate}"
            url = f"{url}{dateRange}"       
        item = self._fetch_url(url)
        item["provider"] = "yahoo"
        return item 
        


        

       

    
