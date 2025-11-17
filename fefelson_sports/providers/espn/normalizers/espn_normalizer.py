from collections import defaultdict
from datetime import datetime
from pytz import timezone
from re import sub 
from typing import Any, List

from ....utils.logging_manager import get_logger

# for debugging
# from pprint import pprint

##########################################################################
##########################################################################


est = timezone('America/New_York')


##########################################################################
##########################################################################


class ESPNNormalizer:
    """ normalizer for ESPN data."""

    def __init__(self, leagueId: str):

        self.leagueId = leagueId


    # ['gmStrp', 'gmInfo', 'shtChrt', 'gmStry',''scrSumm', 'lnScr', 'plys', 'wnPrb', 'bxscr']
    # ['pbp']

    def normalize_boxscore(self, webData: dict) -> dict:      
        
        return {
            "provider": "espn",
            "game": self._set_game_info(webData["boxData"]["gmStrp"]),
            "teamStats": self._set_team_stats(webData),
            "playerStats": self._set_player_stats(webData["boxData"]),
            "stadium": self._set_stadium(webData["boxData"]["gmInfo"]),
            "misc": self._set_misc(webData),
            "teams": self._set_teams(webData["boxData"]),
            "players": self._set_players(webData["boxData"])
        }   


    def normalize_matchup(self, webData: dict) -> dict:

        futureData = {}
        try:
            futureData["title"] = webData["oddsData"]['futureData'][0]["title"]
            futureData["odds"] = []
            for row in sorted(webData["oddsData"]['futureData'][0]["rows"], key=lambda x: int(x['odds'])):
                futureData["odds"].append({"teamId": row["id"], "abrv": row["primaryText"], "odds": row["odds"]})
        except TypeError:
            pass

        propBets = {"playerProps": {}, "teamProps": {}}
        try:
            for category in webData["oddsData"]["propBets"]:
                propType = "teamProps" if category["displayName"] == "Game Props" else "playerProps"
                
                for betType in category["odds"]:
                    betName = betType["displayName"]

                    key, label = ("teams", "teamId") if propType == "teamProps" else ("athletes", "playerId")
                    
                    for propBet in betType[key]:
                        entityId = propBet["id"]
                        propBets[propType][entityId] = propBets[propType].get(entityId, defaultdict(dict))
                        try:
                            propBets[propType][entityId][betName]["line"] = sub('^[ou]', '', propBet["values"][0]["line"])
                            for bet in propBet["values"]:
                                propBets[propType][entityId][betName][bet["type"]] = bet["odds"] if bet["odds"] != "Even" else "+100"
                        except KeyError:
                            pass             
        except TypeError:
            pass 

        try:
            pitchers = webData["gameData"]["prbblPtchrs"].pop("athletes")
        except KeyError:
            pitchers = None

        
        temp = webData["gameData"]["mtchpPrdctr"].pop("teams")
        pred = [(x["tmName"], x["value"]) for x in temp]
        
        

        return {
            "provider": "espn",
            "gameId": webData["gameData"]["gmStrp"]["gid"],
            "homeId": webData["gameData"]["gmStrp"]["tms"][0]['id'],
            "awayId": webData["gameData"]["gmStrp"]["tms"][1]["id"],
            "odds": webData["gameData"]["gmStrp"]["odds"],
            "injurys": webData["gameData"]["injrs"],
            "predictor": pred,
            "pitchers": pitchers,
            "futures": futureData,
            "propBets": propBets
        }   


    def normalize_player(self, webData: dict) -> dict:
        # pprint(webData)
        raise NotImplementedError      


    def normalize_scoreboard(self, webData: dict) -> dict:
        games = []
        for game in webData["page"]["content"]["scoreboard"]["evts"]:  

            games.append({
                "gameId": game["id"],
                "all_star_game": game["allStr"],
                "homeId": game["teams"][0]["id"],
                "awayId": game["teams"][1]["id"], 
                "url": game['link'],
                "gameTime": str(datetime.fromisoformat(game["date"].replace("Z", "+00:00")).astimezone(est)), 
                "season": webData["page"]["content"]["scoreboard"]["season"]["displayName"].split("-")[0],
                "week": game.get("week", None),
                "status": game["status"]["description"].lower(),
                "gameType": game.get("note").lower() if game.get("note") else None,
            })
                            
        return {"provider": "espn",
                "league_id": self.leagueId,
                "games": games
                }   

    
    def normalize_team(self, raw_data: dict) -> dict:
        raise NotImplementedError


    def _set_game_info(self, game: dict) -> dict: 

        zeroIsHome = game["tms"][0]['isHome']
        zeroIsWinner = game["tms"][0].get('winner', False)
        return {
            "league_id": self.leagueId,
            "game_id": game["gid"],
            "home_id": game['tms'][0 if zeroIsHome else 1]['id'],
            "away_id": game['tms'][1 if zeroIsHome else 0]['id'],
            "winner_id": game['tms'][0 if zeroIsWinner else 1]['id'],
            "loser_id": game['tms'][1 if zeroIsWinner else 0]['id'],
            "game_date": str(datetime.fromisoformat(game["dt"].replace("Z", "+00:00")).astimezone(est))
        }

    
    def _set_misc(self, webData: dict) -> Any:
        raise NotImplementedError


    def _set_players(self, data: dict) -> List[dict]:
        players = []
        try:
            for player in [ath["athlt"] for team in data["bxscr"] for r in team["stats"] for ath in r['athlts']]:
                if player not in players:
                    players.append(player)
        except KeyError:
            pass
        
        return players  


    def _set_player_stats(self, data: dict) -> List[dict]:
        raise NotImplementedError


    def _set_stadium(self, data: dict) -> dict:
        # pprint(data)
        return {"name": data["loc"]} if data.get("loc") else None


    def _set_teams(self, data: dict) -> List[dict]:

        teams = []
        for team in data["gmStrp"]["tms"]:
            try:
                lastName = team["nickname"]
            except:
                lastName = team["shortDisplayName"]
            teams.append({
                "team_id": f"{self.leagueId.lower()}.t.{team['id']}",
                "abrv": team["abbrev"],
                "first_name": team["location"],
                "last_name": lastName,
                "primary_color": team["teamColor"],
                "secondary_color": team["altColor"],
            })
         
        return teams  


    def _set_team_stats(self, data: dict) -> List[dict]:
        raise NotImplementedError


    

    
    


    
    

    
