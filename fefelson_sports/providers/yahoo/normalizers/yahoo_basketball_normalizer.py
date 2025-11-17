from datetime import datetime
from pytz import timezone
from typing import Any, Dict, List

# for debugging
from pprint import pprint


##########################################################################
##########################################################################


est = timezone('America/New_York')


##########################################################################
##########################################################################


class YahooNormalizer:
    """ normalizer for Yahoo data."""

    def __init__(self, leagueId: str):

        self.leagueId = leagueId
        


    def normalize_boxscore(self, webData: dict) -> dict:

        gameId = webData["gameData"]["gameid"]
        gameData = webData["gameData"]
 
        return {
            "provider": "yahoo",
            "game": self._set_game_info(gameData),
            "teamStats": self._set_team_stats(webData),
            "playerStats": self._set_player_stats(webData),
            "periods": self._set_period_data(gameData),
            "gameLines": self._set_game_lines(gameData),
            "overUnder": self._set_over_under(gameData), 
            "lineups": self._set_lineups(webData),
            "teams": [team for team in self._set_teams(webData["teamData"]["teams"])
                   if team["team_id"] in (gameData["away_team_id"], gameData["home_team_id"])],
            "players": self._set_players(webData["playerData"]),
            "stadium": self._set_stadium(gameData),
            "misc": self._set_misc(webData)
        }


    def _starting_lineup(self, gameData):
        try:
            lineups = {x: gameData["lineups"][x] for x in ("away_lineup", "home_lineup")}
        except KeyError:
            lineups = None
        return lineups


    def normalize_matchup(self, webData: dict) -> dict:
        # pprint(webData)

        #self.logger.debug("Normalize Yahoo matchup")
        gameData = webData["gameData"]
        gameId = gameData["gameid"]

        try:
           odds = []
           for o in gameData["odds"].values():
               o["timestamp"] = str(datetime.now().astimezone(est))
               odds.append(o)
        except KeyError:
            odds = []

        try:
            pitchers = gameData["byline"]["playersByType"]
        except KeyError:
            pitchers = None


        return {
            "provider": "yahoo",
            "gameId": gameData["gameid"],
            "leagueId": self.leagueId,
            "homeId": gameData["home_team_id"],
            "awayId": gameData["away_team_id"],
            "url": gameData["navigation_links"]["boxscore"]["url"],
            "gameTime": str(datetime.strptime(gameData["start_time"], "%a, %d %b %Y %H:%M:%S %z").astimezone(est)), 
            "season": gameData["season"],
            "week": gameData.get("week", None),
            "statusType": gameData["status_type"].lower(),
            "gameType": gameData["game_type"].split(".")[-1].lower() if gameData["game_type"] else None,
            "odds": odds,
            "pitchers": pitchers,
            "lineups": self._starting_lineup(gameData),
            "players": {x: gameData["playersByTeam"].get(x) for x in (gameData["away_team_id"], gameData["home_team_id"])},
            "teams": [team for team in self._set_teams(webData["teamData"]["teams"])
                   if team["team_id"] in (gameData["away_team_id"], gameData["home_team_id"])],
            "injuries": [player["injury"] for player in webData["playerData"]["players"].values() if player.get("injury", None)],
            "stadiumId": gameData.get("stadium_id", None),
            "isNuetral": bool(gameData.get("tournament")),
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
            
        winnerId = game.get("winning_team_id")
        if winnerId:
            loserId = game["home_team_id"] if winnerId == game["away_team_id"] else game["away_team_id"]
            winnerId, loserId = winnerId, loserId
        else:
            loserId = None

        return {
            "game_id": game["gameid"],
            "league_id": self.leagueId,
            "home_id": game["home_team_id"],
            "away_id": game["away_team_id"],
            "winner_id": winnerId,
            "loser_id": loserId,
            "stadium_id": game.get("stadium_id", None),
            "is_neutral_site": bool(game.get("tournament", 0)),
            "game_date": str(datetime.strptime(game["start_time"], "%a, %d %b %Y %H:%M:%S %z").astimezone(est)), 
            "season": game["season"],
            "week": game.get("week_number", None),
            "game_type": game["season_phase_id"].split(".")[-1].lower(),
            "game_result": game["outcome_type"].split(".")[-1].lower() if game["outcome_type"] else "unknown"
        }

        
    def _set_game_lines(self, data: dict) -> List[dict]:
        gameId = data["gameid"]
        teamIds = {"away": data["away_team_id"], "home": data["home_team_id"]}
        oppIds = {"away": teamIds["home"], "home": teamIds["away"]}
        
        gameLines = []
        try:
            odds = list(data["odds"].values())[-1]

            awayPts = int(data["total_away_points"])
            homePts = int(data["total_home_points"])

            for a_h, teamPts, oppPts in [("away", awayPts, homePts), ("home", homePts, awayPts)]:
                try:
                    result = teamPts - oppPts
                    spread_key = f"{a_h}_spread"
                    spreadOutcome = (result + float(odds[spread_key])>0) - (result + float(odds[spread_key]) < 0)
                    moneyOutcome = (teamPts > oppPts) - (teamPts < oppPts)  # Boolean, automatically 1 (win) or 0 (loss)
                    
                    gameLines.append({
                        "team_id": teamIds[a_h],
                        "opp_id": oppIds[a_h],
                        "game_id": gameId,
                        "spread": odds[spread_key],
                        "spread_line": -110 if odds[f"{a_h}_line"] == '' else odds[f"{a_h}_line"] ,
                        "money_line": None if odds[f"{a_h}_ml"] == '' else odds[f"{a_h}_ml"], 
                        "result": result,
                        "spread_outcome": spreadOutcome,
                        "money_outcome": moneyOutcome
                    })
                except ValueError:
                    pass
        except (KeyError, UnboundLocalError, TypeError) as e:
            # self.logger.warning(f"No Odds Data for {gameId}")
            pass
        return gameLines
    

    def _set_misc(self, webData: dict) -> Any:
        raise NotImplementedError


    def _set_over_under(self, data: dict) -> dict:
        gameId = data["gameid"]
        try:
            odds = list(data["odds"].values())[-1]
        except:
            odds = None
        
        try:
            total = int(data["total_away_points"]) + int(data["total_home_points"])
        except:
            total = None
        
        overUnder = None
        try:
            overUnder = {
                "game_id": gameId,
                "over_under": odds["total"],
                "over_line": -110 if odds["over_line"] == '' else odds["over_line"],
                "under_line": -110 if odds["under_line"] == '' else odds["under_line"],
                "total": total,
                "ou_outcome": (float(total) > float(odds["total"])) - (float(total) < float(odds["total"]))
            }
        except (KeyError, UnboundLocalError, TypeError, ValueError) as e:
            # self.logger.warning(f"No Odds Data for {gameId}")
            pass
        return overUnder


    def _set_period_data(self, data: dict) -> List[dict]:
        gameId = data["gameid"]
        teamIds = {"away": data["away_team_id"], "home": data["home_team_id"]}
        oppIds = {"away": teamIds["home"], "home": teamIds["away"]}

        periods = []
        try:
            for p in data["game_periods"]:
                periodId = p["period_id"]
                for a_h in ("away", "home"):
                   
                   periods.append({
                        "game_id": gameId,
                        "team_id": teamIds[a_h],
                        "opp_id": oppIds[a_h],
                        "period": periodId,
                        "pts": int(p["{}_points".format(a_h)])
                    })
        except (TypeError, ValueError):
            pass
        return periods


    def _set_players(self, data: dict) -> List[dict]:
        posTypes = dict([(key, value["abbr"]) for key, value in data["positions"].items()])
        players = []
        for key, value in data["players"].items():
            
            try:
                position = posTypes.get(value.get("primary_position_id", {}), None)
            except TypeError:
                position = None
            
            players.append({
                "player_id": value["player_id"],
                "first_name": value["first_name"],
                "last_name": value["last_name"],
                "pos": position
            })
        return players


    def _set_player_stats_list(self, data: dict) -> List:
        
        teamIds = {"away": data["away_team_id"], "home": data["home_team_id"]}
        oppIds = {"away": teamIds["home"], "home": teamIds["away"]}

        playerList = []
        for a_h in ("away", "home"):
            try:
                for playerId in data["lineups"]["{}_lineup_order".format(a_h)]["all"]:
                    playerList.append((playerId, teamIds[a_h], oppIds[a_h]))
            except (KeyError, TypeError) as e:
                self.logger.warning("No player List for "+data["gameid"])
        return playerList


    def _set_stadium(self, data: dict) -> dict:
        return {
            "stadium_id": data["stadium_id"],
            "name": data.get("stadium", None)
        }


    def _set_teams(self, data: dict) -> List[dict]:
        teams = []
        for team in [value for key, value in data.items() if self.leagueId.lower() in key]:
            team["first_name"] = "Oakland" if team["last_name"] == "Athletics" else team["first_name"]
            teams.append({
                "team_id": team["team_id"],
                "league_id": self.leagueId,
                "first_name": team["first_name"],
                "last_name": team["last_name"],
                "abrv": team.get("abbr", "N/A"),
                "conference": team.get("conference_abbr", None),
                "division": team.get("division", None),
                "primary_color": team.get("colorPrimary", None),
                "secondary_color": team.get("colorSecondary", None)
                })
        return teams  
    

    def _set_lineup_data(self, data: dict) -> List[dict]:
        raise NotImplementedError


    def _set_team_stats(self, data: dict) -> List[dict]:
        raise NotImplementedError


    def _set_player_stats(self, data: dict) -> List[dict]:
        raise NotImplementedError           

        



#############################################################################################
#############################################################################################



from math import sqrt
from ...sport_normalizers import BasketballNormalizer

# for debugging
# from pprint import pprint 

#############################################################################################
#############################################################################################

 

class YahooBasketballNormalizer(BasketballNormalizer, YahooNormalizer):
    """Normalizer for Yahoo Basketball data (NBA and NCAAB)."""

    def __init__(self, leagueId: str):
        BasketballNormalizer.__init__(self, leagueId)
        YahooNormalizer.__init__(self, leagueId)

        self._id_prefix = "nba" if leagueId == "NBA" else "ncaab"
        self._stat_variation = f"{self._id_prefix}.stat_variation.2"


    def _set_lineups(self, webData):
        return None 
    

    def _set_misc(self, webData):
        gameData = webData["gameData"]
        gameId = gameData["gameid"]
        try:
            playerShots = self._set_player_shots(gameData)
        except KeyError:
            playerShots = None
        return playerShots
    

    def _set_player_shots(self, data: Dict[str, Any]) -> List["BasketballShot"]:
        gameId = data["gameid"]
        teamIds = {"away": data["away_team_id"], "home": data["home_team_id"]}

        playerShots = []
        for shot in [shot for shot in data["play_by_play"].values()
                     if shot["class_type"] == "SHOT" and (int(shot["type"]) not in range(10, 25) or (int(shot["points"])==1 and int(shot["period"]) >= self._regulation_periods and  self._calculate_clutch(teamIds, shot)))]:
            base_pct = float(shot["baseline_offset_percentage"])
            side_pct = float(shot["sideline_offset_percentage"])
            base_pct_adjusted = base_pct * ((-1) ** int(shot["side_of_basket"] == "R"))
            distance = int(sqrt((50 * base_pct_adjusted) ** 2 + (side_pct * 94) ** 2))

            playerShots.append({
                "player_id": f"{self._id_prefix}.p.{shot['player']}",
                "team_id": f"{self._id_prefix}.t.{shot['team']}",
                "opp_id": teamIds["home"] if int(teamIds["home"].split(".")[-1]) != int(shot["team"]) else teamIds["away"],
                "game_id": gameId,
                "play_num": shot["play_num"],
                "period": shot["period"],
                "shot_type_id": shot["type"],
                "assist_id": None if int(shot["assister"]) == 0 else f"{self._id_prefix}.p.{shot['assister']}",
                "shot_made": bool(int(shot["shot_made"])),
                "points": int(shot["points"]),
                "base_pct": base_pct,
                "side_pct": side_pct,
                "distance": distance,
                "fastbreak": bool(int(shot["fastbreak"])),
                "side_of_basket": shot["side_of_basket"],
                "clutch": (False if int(shot["period"]) < self._regulation_periods 
                        else self._calculate_clutch(teamIds, shot)),
                "zone": self._get_shot_zone(shot)
            })
        return playerShots
    

    def _set_player_stats(self, data: Dict[str, Any]) -> List["BasketballPlayerStat"]:
        gameData = data["gameData"]
        gameId = gameData["gameid"]

        playerStats = []
        try:
            starters = [posRecord["player_id"] for a_h in ("away", "home")
                        for posRecord in gameData["lineups"]["{}_lineup".format(a_h)]["all"].values()
                        if int(posRecord["starter"]) == 1]
        except (AttributeError, TypeError):
            starters = []

        for playerId, teamId, oppId in self._set_player_stats_list(gameData):
            try:
                raw_player_data = data["statsData"]["playerStats"][playerId][self._stat_variation]
                mins = f"{(t := raw_player_data.get(f'{self._id_prefix}.stat_type.3', '0:0').split(':'))[0]}.{int((int(t[1]) / 60) * 100 + 0.5) if len(t) > 1 else 0}"
            except (KeyError, AttributeError):
                raw_player_data = None
                mins = 0

            if raw_player_data and float(mins) > 0:
                try:
                    playerStats.append({
                        "player_id": playerId,
                        "game_id": gameId,
                        "team_id": teamId,
                        "opp_id": oppId,
                        "starter": (playerId in starters),
                        "mins": mins,
                        "fgm": raw_player_data[f"{self._id_prefix}.stat_type.28"].split("-")[0],
                        "fga": raw_player_data[f"{self._id_prefix}.stat_type.28"].split("-")[1],
                        "ftm": raw_player_data[f"{self._id_prefix}.stat_type.29"].split("-")[0],
                        "fta": raw_player_data[f"{self._id_prefix}.stat_type.29"].split("-")[1],
                        "tpm": raw_player_data[f"{self._id_prefix}.stat_type.30"].split("-")[0],
                        "tpa": raw_player_data[f"{self._id_prefix}.stat_type.30"].split("-")[1],
                        "pts": raw_player_data[f"{self._id_prefix}.stat_type.13"],
                        "oreb": raw_player_data[f"{self._id_prefix}.stat_type.14"],
                        "dreb": raw_player_data[f"{self._id_prefix}.stat_type.15"],
                        "ast": raw_player_data[f"{self._id_prefix}.stat_type.17"],
                        "stl": raw_player_data[f"{self._id_prefix}.stat_type.18"],
                        "blk": raw_player_data[f"{self._id_prefix}.stat_type.19"],
                        "turns": raw_player_data[f"{self._id_prefix}.stat_type.20"],
                        "fls": raw_player_data[f"{self._id_prefix}.stat_type.22"],
                        "plus_minus": raw_player_data.get(f"{self._id_prefix}.stat_type.32") if self.leagueId == "NBA" else None
                    })
                except IndexError:
                    pass
        return playerStats
    

    def _set_team_stats(self, data: Dict[str, Any]) -> List["BasketballTeamStat"]:
        gameData = data["gameData"]
        gameId = gameData["gameid"]
        teamIds = {"away": gameData["away_team_id"], "home": gameData["home_team_id"]}
        oppIds = {"away": teamIds["home"], "home": teamIds["away"]}

        teamStats = []
        for a_h in ("away", "home"):
            raw_stat_data = data["statsData"]["teamStatsByGameId"][gameId][teamIds[a_h]][self._stat_variation]
            # Adjust minutes for overtime: base + (extra periods * 5)
            minutes = self._base_minutes + (len(gameData["game_periods"]) - self._regulation_periods) * 5
            
            teamStats.append({
                "game_id": gameId,
                "team_id": teamIds[a_h],
                "opp_id": oppIds[a_h],
                "minutes": minutes,
                "fga": raw_stat_data[f"{self._id_prefix}.stat_type.128"].split("-")[1],
                "fgm": raw_stat_data[f"{self._id_prefix}.stat_type.128"].split("-")[0],
                "fta": raw_stat_data[f"{self._id_prefix}.stat_type.129"].split("-")[1],
                "ftm": raw_stat_data[f"{self._id_prefix}.stat_type.129"].split("-")[0],
                "tpa": raw_stat_data[f"{self._id_prefix}.stat_type.130"].split("-")[1],
                "tpm": raw_stat_data[f"{self._id_prefix}.stat_type.130"].split("-")[0],
                "pts": raw_stat_data[f"{self._id_prefix}.stat_type.113"],
                "oreb": raw_stat_data[f"{self._id_prefix}.stat_type.114"],
                "dreb": raw_stat_data[f"{self._id_prefix}.stat_type.115"],
                "ast": raw_stat_data[f"{self._id_prefix}.stat_type.117"],
                "stl": raw_stat_data[f"{self._id_prefix}.stat_type.118"],
                "blk": raw_stat_data[f"{self._id_prefix}.stat_type.119"],
                "turns": raw_stat_data[f"{self._id_prefix}.stat_type.120"],
                "fouls": raw_stat_data[f"{self._id_prefix}.stat_type.122"]
            })
            
        return teamStats  

