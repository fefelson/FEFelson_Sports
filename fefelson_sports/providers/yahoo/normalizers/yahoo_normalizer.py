from datetime import datetime
from pytz import timezone
from typing import Any, List

from ....utils.logging_manager import get_logger

# for debugging
from pprint import pprint


##########################################################################
##########################################################################


est = timezone('America/New_York')


def select_betting_section(bettingType, bettingJson):

    for item in bettingJson:
        if item["type"] == bettingType:
            return item

    # fallthrough
    return None


##########################################################################
##########################################################################


class YahooNormalizer:
    """ normalizer for Yahoo data."""

    def __init__(self, leagueId: str):

        self.leagueId = leagueId

        self.gameId = None
        self.teamIds = None
        self.oppIds = None
        

    def normalize_boxscore(self, webData: dict) -> dict:
        gameStats = webData["gameStats"]
        gameDetails = webData["gameDetails"]

        self.gameId = gameDetails["gameId"]
        self.teamIds = {"away": gameDetails["awayTeamId"], "home": gameDetails["homeTeamId"]}
        self.oppIds = {"away": self.teamIds["home"], 
                        "home": self.teamIds["away"], 
                        self.teamIds["home"]: self.teamIds["away"],
                        self.teamIds["away"]: self.teamIds["home"]}

        return {
            "provider": "yahoo",
            "game": self._set_game_info(gameDetails),
            "teamStats": self._set_team_stats(gameDetails),
            "playerStats": self._set_player_stats(webData),
            "periods": self._set_period_data(gameDetails),
            "gameLines": self._set_game_lines(gameDetails),
            "overUnder": self._set_over_under(gameDetails), 
            "lineups": self._set_lineups(gameStats),
            "teams": self._set_teams(gameDetails),
            "players": self._set_players(gameDetails),
            "stadium": self._set_stadium(gameDetails["venue"]),
            "misc": self._set_misc(gameDetails)
        }


    def normalize_matchup(self, webData: dict) -> dict:
        # pprint(webData)
        gameData = webData["game"]

        try:
            pitchers = [gameData[f"{a_h}StartingPitcher"] for a_h in ("away", "home")]
        except KeyError:
            pitchers = None
                    
        return {
            "provider": "yahoo",
            "gameId": gameData["gameId"],
            "leagueId": self.leagueId,
            "homeId": gameData["homeTeamId"],
            "awayId": gameData["awayTeamId"],
            "gameTime": str(datetime.strptime(gameData["startTime"], "%Y-%m-%dT%H:%M:%S%z").astimezone(est)), 
            "season": gameData["season"],
            "week": gameData["week"],
            "statusType": gameData["status"].lower(),
            "gameType": gameData["seasonPhase"].lower(),
            "odds": gameData["bets"],
            "pitchers": pitchers,
            "lineups": [gameData[f"{a_h}TeamLineup"] for a_h in ("away", "home")],
            "teams": self._set_teams(gameData),
            "injuries": [gameData[f"{a_h}Team"]["injuredPlayers"] for a_h in ("away", "home")],
            "stadiumId": gameData["venue"]["venueId"],
            # "isNuetral": webData["tournamentId"],
        }


    def normalize_player(self, data: dict) -> dict:
        #self.logger.debug("Normalize Yahoo player")
                
        return {
                "bats": data["battingSide"][0],
                "throws": data["throwingHand"][0],
                "birthdate": str(datetime.strptime(data["birthDate"], "%Y-%m-%d").date()),
                "rookie_season": data["firstYear"]
        }


    def normalize_scoreboard(self, webData: dict) -> dict:
        #self.logger.debug("Normalize Yahoo scoreboard")

        games = []
        for gameId, game in webData["GamesStore"]["games"].items():
            if gameId.split(".")[0] == self.leagueId.lower():
            
                try:
                    odds = []
                    for o in game["odds"].values():
                        o["timestamp"] = str(datetime.now().astimezone(est))
                        odds.append(o)
                except KeyError:
                    odds = []

                try:
                    url= game["navigation_links"]["boxscore"]["url"]
                except (TypeError, KeyError):
                    url = None
                
                games.append({
                        "gameId": game["gameid"],
                        "homeId": game["home_team_id"],
                        "awayId": game["away_team_id"],
                        "url": url,
                        "gameTime": str(datetime.strptime(game["start_time"], "%a, %d %b %Y %H:%M:%S %z").astimezone(est)), 
                        "season": game["season"],
                        "week": game.get("week_number", None),
                        "status": game["status_type"].lower(),
                        "gameType": game["game_type"].split(".")[-1].lower() if game["game_type"] else None,
                        "odds": odds
                    })      
        return {"provider": "yahoo",
                "league_id": self.leagueId,
                "games": games
                } 


    def normalize_team(self, raw_data: dict) -> dict:
        raise NotImplementedError


    def _set_game_info(self, game: dict) -> dict:
        
        winnerId = game.get("winningTeamId")
        loserId = None
        if winnerId:
            loserId = game["homeTeamId"] if winnerId == game["awayTeamId"] else game["awayTeamId"]
        
        gameInfo = {
            "game_id": self.gameId,
            "league_id": self.leagueId,
            "home_id": game["homeTeamId"],
            "away_id": game["awayTeamId"],
            "winner_id": winnerId,
            "loser_id": loserId,
            "stadium_id": game["venue"]["venueId"].split(".")[-1],
            # "is_neutral_site": bool(game["tournamentId"]),
            "game_date": str(datetime.strptime(game["startTime"], "%Y-%m-%dT%H:%M:%S%z").astimezone(est)), 
            "season": game["season"],
            "week": game["week"],
            "game_type": game["seasonPhase"],
            "game_result": game["displayResult"]
        }

        # pprint(gameInfo)
        # raise
        return gameInfo

        
    def _set_game_lines(self, data: dict) -> List[dict]:
     
        gameLines = []

        if not data["bets"]:
            return gameLines

        teamPts = {data[f"{a_h}TeamId"]: data[f"{a_h}Score"] for a_h in ("away", "home")}

        for i in range(2):
            
            try:
                moneyLine = select_betting_section("MONEY_LINE", data["bets"])["options"][i]
                spread = select_betting_section("SPREAD", data["bets"])["options"][i]

                teamId = moneyLine["teams"][0]["teamId"]
                oppId = self.oppIds[teamId]
                    
                result = teamPts[teamId] - teamPts[oppId]
                spreadOutcome = (result + float(spread["shortName"])>0) - (result + float(spread["shortName"]) < 0)
                moneyOutcome = (teamPts[teamId] > teamPts[oppId]) - (teamPts[teamId] < teamPts[oppId])  # Boolean, automatically 1 (win) or 0 (loss)
                
                
                gameLines.append({
                    "team_id": teamId,
                    "opp_id": oppId,
                    "game_id": self.gameId,
                    "spread": spread["shortName"],
                    "spread_line": spread["americanOdds"],
                    "spread_wager_pct": spread["wagerPercentage"],
                    "spread_stake_pct": spread["stakePercentage"],
                    "money_line": moneyLine["americanOdds"], 
                    "money_wager_pct": moneyLine["wagerPercentage"],
                    "money_stake_pct": moneyLine["stakePercentage"],
                    "result": result,
                    "spread_outcome": spreadOutcome,
                    "money_outcome": moneyOutcome
                })
            except Exception as e:
                get_logger().warning(f"_set_game_lines - {e}")
                pprint(data["bets"])
                raise
               
        # pprint(gameLines)
        # raise
        return gameLines
    

    def _set_misc(self, webData: dict) -> Any:
        raise NotImplementedError


    def _set_over_under(self, data: dict) -> dict:
        
        overUnder = None

        if not data["bets"]:
            return overUnder

        try:
            total = int(data["awayScore"]) + int(data["homeScore"])
            oU = float(select_betting_section("OVER_UNDER", data["bets"])["options"][0]["optionDetails"][0]["value"])
            
            overUnder = {
                    "game_id": self.gameId,
                    "over_under": oU,
                    "over_line": select_betting_section("OVER_UNDER", data["bets"])["options"][0]["americanOdds"],
                    "under_line": select_betting_section("OVER_UNDER", data["bets"])["options"][1]["americanOdds"],
                    "total": total,
                    "ou_outcome": (float(total) > oU) - (float(total) < oU)
                }
        except Exception as e:
            get_logger().warning(f"_set_over_under - {e}")
            pprint(data["bets"])
            raise
       
       
        # pprint(overUnder)
        # raise 

        return overUnder


    def _set_period_data(self, data: dict) -> List[dict]:

        periods = []
        for a_h in ("away", "home"):
            for period in data[f"{a_h}LineScore"]:
                # pprint(period)
                # raise                
                periods.append({
                    "game_id": self.gameId,
                    "team_id": self.teamIds[a_h],
                    "opp_id": self.oppIds[a_h],
                    "period": period["period"]["period"],
                    "pts": period["score"]
                })
        # pprint(periods)
        # raise
        
        return periods


    def _set_players(self, data: dict) -> List[dict]:

        players = []

        for a_h in ("away", "home"):
            for player in data[f"{a_h}TeamLineup"]:
                # pprint(player)
                try:
                    pos = player["player"]["positionIds"][0]
                except IndexError:
                    pos = "n/a"
                
                players.append({
                    "player_id": player["player"]["playerId"],
                    "first_name": player["player"]["firstName"],
                    "last_name": player["player"]["lastName"],
                    "bats": player["player"].get("battingSide"),
                    "throws": player["player"].get("throwingHand"),
                    "pos": pos
                })
        # pprint(players)
        # raise
        return players


    def _set_stadium(self, data: dict) -> dict:
        return {
            "stadium_id": data["venueId"].split(".")[-1],
            "name": data["displayName"]
        }


    def _set_teams(self, data: dict) -> List[dict]:
        teams = []
        for a_h in ("away", "home"):
            team = data[f"basic{a_h.capitalize()}Team"]
            teams.append({
                "team_id": team["teamId"],
                "league_id": self.leagueId,
                "display_name": team["displayName"],
                "last_name": team["nickname"],
                "abrv": team["abbreviation"],
                "primary_color": team["primaryColor"],
                "secondary_color": team["secondaryColor"]
                })
        
        # pprint(teams)
        # raise

        return teams  
    

    def _set_lineup_data(self, data: dict) -> List[dict]:
        raise NotImplementedError


    def _set_team_stats(self, data: dict) -> List[dict]:
        raise NotImplementedError


    def _set_player_stats(self, data: dict) -> List[dict]:
        raise NotImplementedError           

        
