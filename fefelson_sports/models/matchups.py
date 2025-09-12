from collections import defaultdict
from copy import deepcopy
from datetime import date, datetime, timedelta
from os import environ, remove, listdir
from os.path import exists
from pytz import timezone

from ..database.stores.base import ProviderStore
from ..database.stores.core import TeamStore, PlayerStore
from ..providers import get_download_agent, get_normal_agent
from ..utils.file_agent import JSONAgent
from ..utils.logging_manager import get_logger

# for debugging
# from pprint import pprint

######################################################################
######################################################################

BASE_PATH = f"{environ['HOME']}/FEFelson/FEFelson_Sports/matchups"

est = timezone('America/New_York')

 # Current time
now = datetime.now().astimezone(est)

# Get 5 AM today
today_5am = datetime.now().astimezone(est).replace(hour=5, minute=0, second=0, microsecond=0)


matchupTemplate = {
    "title": None,
    "leagueId": None,
    "homeId": None,
    "awayId": None,
    "gameTime": None,
    "odds": [],
    "pitchers": None,
    "players": None,
    "lineups": None,
    "injuries": None,
    "futures": None,
    "propBets": None,
    "urls": None,
    "teams": None,
    "lastUpdate": None
    }


######################################################################
######################################################################


class Matchup:




    def __init__(self, leagueId: str):
        super().__init__()

        self.leagueId = leagueId
        self.providerStore = ProviderStore()
        self.teamStore = TeamStore()
        self.playerStore = PlayerStore()


    def _write(self, filePath, matchup):
        JSONAgent.write(filePath, matchup)


    def clean_files(self):
        for filePath in [f"{BASE_PATH}/{fileName}" for fileName in listdir(f"{BASE_PATH}")]:
            data = JSONAgent.read(filePath)
            data["gameTime"] = datetime.fromisoformat(data["gameTime"])
            if data["leagueId"] == self.leagueId and data["gameTime"].date() < date.today():
                remove(filePath)


    def download(self, provider: str, url: str) -> dict:
        downloadAgent = get_download_agent(self.leagueId, provider)
        try:
            webData = downloadAgent.fetch_matchup(url)
        except KeyError:
            webData = None
        return webData 


    def normalize(self, webData: dict) -> dict:
        normalAgent = get_normal_agent(self.leagueId, webData["provider"])
        return normalAgent.normalize_matchup(webData)


    def _getFile(self, filePath, game):
        matchup = None
        if exists(filePath):
            matchup = JSONAgent.read(filePath)
        else:
            matchup = deepcopy(matchupTemplate)
            for item in ("title", "leagueId", "homeId", "awayId", "gameTime", "urls"):
                matchup[item] = game[item]

        return matchup


    def _needs_update(self, lastUpdate, gameTime, matchup):
        if not lastUpdate:
            return True 
        if lastUpdate < today_5am:
            return True 
        if (gameTime - now < timedelta(hours=3) and not matchup.get("lineups")):
            return True 
        if self.leagueId == "MLB" and  (not matchup['pitchers']['away'] or not matchup['pitchers']['home']):
            return True
        return False 
        


    def process(self, game: dict, session = None) -> dict:
        get_logger().debug(f"process Matchup - {game['title']}")

        filePath = f"{BASE_PATH}/{game['title']}.json"
        matchup = self._getFile(filePath, game)

        gameTime = datetime.fromisoformat(matchup["gameTime"])
        if matchup["lastUpdate"]:
            lastUpdate = datetime.fromisoformat(matchup["lastUpdate"])
        else:
            lastUpdate = None

        if not lastUpdate or (now - lastUpdate) > timedelta(minutes=45):
            try:
                matchup["odds"].append(game["odds"][0])
                self._write(filePath, matchup)
            except IndexError:
                pass 

        if self._needs_update(lastUpdate, gameTime, matchup):
            try:
                self._update(session, filePath, matchup, game)
            except TypeError:
                pass


    def _update(self, session, filePath, matchup, game):
        
        info = {}
        for provider, url in game["urls"].items():
            webData = self.download(provider, url)
            info[provider] = self.normalize(webData)

        try:
            futures = info["espn"].get("futures")
            if futures:
                for bet in futures["odds"]:
                    bet["teamId"] = self.providerStore.get_inside_id("espn", self.leagueId, "team", bet.pop("teamId"), session)
            matchup["futures"] = futures 

            propBets = {"playerProps":{}, "teamProps": {}}
            espnProps = info["espn"].get("propBets")
            if espnProps:
                for espnId, bets in espnProps["playerProps"].items():
                    playerId = self.providerStore.get_inside_id("espn", self.leagueId, "player", espnId, session)
                    if playerId != -1:
                        propBets["playerProps"][playerId] = espnProps["playerProps"][espnId]

                for espnId, bets in espnProps["teamProps"].items():
                    teamId = self.providerStore.get_inside_id("espn", self.leagueId, "team", espnId, session)
                    if teamId != -1:
                        propBets["teamProps"][teamId] = espnProps["teamProps"][espnId]
            matchup["propBets"] = propBets
                    

            matchup["predictor"] = info["espn"].get("predictor")
        except KeyError:
            get_logger().warning(f"No ESPN for - {game['title']}")
        

        
        players = defaultdict(dict)      
        yahooPlayers = info["yahoo"].get("players")
        teamPlayers = {}

        if yahooPlayers:
            for key in yahooPlayers:
                teamId = self.providerStore.get_inside_id("yahoo", self.leagueId, "team", key, session)
                
                if teamId != -1:
                    for yahooId in yahooPlayers[key]:
                        teamPlayers[yahooId] = teamId 
            
                        playerId = self.providerStore.get_inside_id("yahoo", self.leagueId, "player", yahooId, session)
                        if playerId != -1:
                            player = self.playerStore.get_info(playerId, session)
                            players[teamId][playerId] = player
        matchup["players"] = players
        
        injuries = defaultdict(list)
        yahooInjury = info["yahoo"].get("injuries")
        if yahooInjury:
            for injury in yahooInjury:
                playerId = self.providerStore.get_inside_id("yahoo", self.leagueId, "player", injury['player_id'], session)
                if playerId != -1:
                    teamId = teamPlayers[injury['player_id']]
                    injuries[teamId].append({"player_id": playerId, "date": injury["date"], "type": injury["type"], "comment": injury["comment"]})
        matchup["injuries"] = injuries


        pitchers = {"away": None, "home": None}
        yahooPitchers = info["yahoo"].get("pitchers")
        if yahooPitchers:
            for a_h in ("away", "home"):
                playerId = self.providerStore.get_inside_id("yahoo", self.leagueId, "player", yahooPitchers[f"{a_h}_pitcher"], session)
                if playerId != -1:
                    player = self.playerStore.get_info(playerId, session)
                    pitchers[a_h] = (playerId, f"{player['first_name']} {player['last_name']}", player["throws"])
        matchup["pitchers"] = pitchers
        
        lineups = defaultdict(list)
        yahooLineups = info["yahoo"].get("lineups")
        if yahooLineups:
            for a_h in ("away", "home"):
                for batter in yahooLineups[a_h]["B"]:
                    playerId = self.providerStore.get_inside_id("yahoo", self.leagueId, "player", batter[1], session)
                    if playerId != -1:
                        player = self.playerStore.get_info(playerId, session)
                        lineups[a_h].append((playerId, f"{player['last_name']}", player["bats"], batter[-1]))
        matchup["lineups"] = lineups

        teams = {"away":None, "home":None}
        yahooTeams = info["yahoo"].get("teams")

        for i, h_a in enumerate(("home", "away")):
            teamId = self.providerStore.get_inside_id("yahoo", self.leagueId, "team", yahooTeams[i]["team_id"], session)
            if teamId != -1:
                teams[h_a] = self.teamStore.get_team_info(teamId, session)
            else:
                yahooTeams[i]["team_id"] = -1
                teams[h_a] = yahooTeams[i]

        matchup["teams"] = teams

        
        
        matchup["lastUpdate"] = str(now)
        
        self._write(filePath, matchup)

   
    

