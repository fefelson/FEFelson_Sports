from datetime import datetime
from pytz import timezone
from typing import Any, List

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

def select_stats_section(statsType, statsJson):
    # pprint(statsJson)
    for item in statsJson:
        if item["statId"] == statsType:
            return item["value"]

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
        # pprint(webData)
        # raise 
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


    def _starting_lineup(self, gameData):
        try:
            lineups = {x: gameData["lineups"][x] for x in ("away_lineup", "home_lineup")}
        except KeyError:
            lineups = None
        return lineups


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
        # pprint(data["bets"])
        # raise
        gameLines = []

        if not data["bets"]:
            return gameLines

        teamPts = {data[f"{a_h}TeamId"]: data[f"{a_h}Score"] for a_h in ("away", "home")}

        for i in range(2):
            
            try:
                moneyLine = select_betting_section("MONEY_LINE", data["bets"])["options"][i]
                spread = select_betting_section("SPREAD", data["bets"])["options"][i]

                teamId = moneyLine["teams"][0]["teamId"]
                oppId = self.oppIds.get(teamId, -1)
                    
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
                pprint(data["bets"])
               
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

        
        

        



#############################################################################################
#############################################################################################


from ...sport_normalizers import FootballNormalizer 

class YahooNCAAFNormalizer(YahooNormalizer, FootballNormalizer):
    """Normalizer for Yahoo Football data (NFL and NCAAF)."""

    def __init__(self, leagueId: str):
        super().__init__(leagueId)

        self._id_prefix = "nfl" if self.leagueId == "NFL" else "ncaaf"


    def _set_lineups(self, data: dict) -> List[dict]:
        return []


    def _set_misc(self, webData: dict) -> dict:
        try:
            misc = {"pass_plays": self._set_pass_plays(webData),
                "rush_plays": self._set_rush_plays(webData),
                "kick_plays": self._set_kick_plays(webData),
                "playbyplay": webData["playByPlay"]
            }
        except KeyError:
            misc = {}
        return misc


    def _set_pass_plays(self, webData: dict) -> List[dict]:
        
        pass_plays = []

        # for play in webData["playByPlay"]: 
        #     if play["playTypeId"] == "PASS":
        #         pprint(play)
        #         print("\n\n\n")
            # if int(play["type"]) in (2,3,4):

            #     teamId = f"{self._id_prefix}.t.{play['team']}"
            #     oppId = gameData["away_team_id"] if teamId == gameData["home_team_id"] else gameData["home_team_id"]

            #     mins,secs = play['clock'].split(":")
            #     secs = int(int(secs)*10/60)
                
            #     pass_plays.append({
            #         "game_id": gameId,
            #         "team_id": teamId,
            #         "opp_id": oppId,
            #         "play_num": play["play_id"],
            #         "period": play["period"],
            #         "down": play["down"],
            #         "distance": play["distance"],
            #         "clock": float(f"{mins}.{secs}"),
            #         "yards_to_endzone": play["yards_to_endzone"],
            #         "quarterback": play["sub_plays"][0]["sub_play"]["passer"],
            #         "target": play["sub_plays"][0]["sub_play"].get("receiver"),
            #         "yards": play["sub_plays"][0]["sub_play"]["yards"],
            #         "direction": play["sub_plays"][0]["sub_play"]["direction"],
            #         "completed": True if int(play["type"]) == 2 else False,
            #         "touchdown": True if int(play["sub_plays"][0]["sub_play"]["points"]) == 6 else False,
            #         "intercepted": True if int(play["type"]) == 4 else False
            #     })
        return pass_plays


    def _set_rush_plays(self, webData: dict) -> List[dict]:

        rush_plays = []

        # for play in gameData["play_by_play"].values():
        #     if int(play["type"]) == 1:

        #         teamId = f"{self._id_prefix}.t.{play['team']}"
        #         oppId = gameData["away_team_id"] if teamId == gameData["home_team_id"] else gameData["home_team_id"]
                
        #         mins,secs = play['clock'].split(":")
        #         secs = int(int(secs)*10/60)

        #         rush_plays.append({
        #             "game_id": gameId,
        #             "team_id": teamId,
        #             "opp_id": oppId,
        #             "play_num": play["play_id"],
        #             "period": play["period"],
        #             "down": play["down"],
        #             "distance": play["distance"],
        #             "clock": float(f"{mins}.{secs}"),
        #             "yards_to_endzone": play["yards_to_endzone"],
        #             "rusher": play["sub_plays"][0]["sub_play"]["rusher"],
        #             "yards": play["sub_plays"][0]["sub_play"]["yards"],
        #             "direction": play["sub_plays"][0]["sub_play"]["direction"],
        #             "touchdown": True if int(play["sub_plays"][0]["sub_play"]["points"]) == 6 else False
        #         })

        return rush_plays


    def _set_kick_plays(self, webData: dict) -> List[dict]:

        kick_plays = []

        # for play in gameData["play_by_play"].values():
        #     if int(play["type"]) == 9:

        #         teamId = f"{self._id_prefix}.t.{play['team']}"
        #         oppId = gameData["away_team_id"] if teamId == gameData["home_team_id"] else gameData["home_team_id"]
                
        #         mins,secs = play['clock'].split(":")
        #         secs = int(int(secs)*10/60)

        #         kick_plays.append({
        #             "game_id": gameId,
        #             "team_id": teamId,
        #             "opp_id": oppId,
        #             "play_num": play["play_id"],
        #             "period": play["period"],
        #             "down": play["down"],
        #             "distance": play["distance"],
        #             "clock": float(f"{mins}.{secs}"),
        #             "kicker": play["sub_plays"][0]["sub_play"]["player"],
        #             "yards": play["sub_plays"][0]["sub_play"]["yards"],
        #             "kick_good": True if int(play["sub_plays"][0]["sub_play"]["points"]) == 3 else False,
        #             "kick_blocked": bool(int(play["sub_plays"][0]["sub_play"]["kick_blocked"]))
        #         })

        return kick_plays


    def _set_team_stats(self, data: dict) -> List[dict]:
        
        # pprint(data)
        # raise
        teamStats = []
        for a_h in ("away", "home"):
        #     opp = "away" if a_h == "home" else "home"
        #     gameStats0 = data["gameStats"][f"{a_h}TeamGameStats0"]["stats"]
        #     gameStats1 = data["gameStats"][f"{a_h}TeamGameStats1"]["stats"]   
            
            teamStats.append({
                "game_id": self.gameId,
                "team_id": self.teamIds[a_h],
                "opp_id": self.oppIds[a_h],
                "pts":  data[f"{a_h}Score"]
            })
        return teamStats 


    def _set_player_stats(self, webData: dict) -> dict:
        playerStats = {
            "passing": self._set_passing_stats(webData),
            "rushing": self._set_rushing_stats(webData),
            "receiving": self._set_recieving_stats(webData),
            "fumbles": self._set_fumble_stats(webData),
            "kicking": self._set_kick_stats(webData),
            "punting": self._set_punt_stats(webData),
            "returns": self._set_return_stats(webData),
            "defense": self._set_defense_stats(webData)
        }
        return playerStats
        

    def _set_passing_stats(self, data: dict) -> List[dict]:
        # pprint(data)
        # raise
        passingStats = []
        for a_h in ("away", "home"):
            for table in data["gameStats"]["playerStats"][f"{a_h}Tables"]:
                for player in table["tableStats"]:
                    stats = player["player"]["playerGameStats0"]
                    if stats and isinstance(stats, list):
                        stats = stats[0]["stats"]
                        
                        # raise

                        passingStats.append({
                            "player_id":  player["player"]["playerId"],
                            "game_id": self.gameId,
                            "team_id": self.teamIds[a_h],
                            "opp_id": self.oppIds[a_h],
                            "pass_att": select_stats_section("PASSING_ATTEMPTS", stats),
                            "pass_comp": select_stats_section("PASSING_COMPLETIONS", stats),
                            "pass_yds": select_stats_section("PASSING_YARDS", stats),
                            "pass_td": select_stats_section("PASSING_TOUCHDOWNS", stats),
                            "pass_int": select_stats_section("PASSING_INTERCEPTIONS", stats),
                            "sacks": select_stats_section("SACKS_TAKEN", stats),
                            "sack_yds_lost": select_stats_section("SACKS_YARDS_LOST", stats)
                        })

        return passingStats


    def _set_rushing_stats(self, data: dict) -> List[dict]:

        rushingStats = []
        for a_h in ("away", "home"):
            for table in data["gameStats"]["playerStats"][f"{a_h}Tables"]:
                for player in table["tableStats"]:
                    stats = player["player"]["playerGameStats1"]

                    if stats and isinstance(stats, list) and select_stats_section("RUSHING_ATTEMPTS", stats[0]["stats"]):
                        stats = stats[0]["stats"]
                        # pprint(stats)
                        # raise

                        rushingStats.append({
                            "player_id":  player["player"]["playerId"],
                            "game_id": self.gameId,
                            "team_id": self.teamIds[a_h],
                            "opp_id": self.oppIds[a_h],
                            "rush_att": select_stats_section("RUSHING_ATTEMPTS", stats),
                            "rush_yds": select_stats_section("RUSHING_YARDS", stats),
                            "rush_td": select_stats_section("RUSHING_TOUCHDOWNS", stats)
                        })

        return rushingStats


    def _set_recieving_stats(self, data: dict) -> List[dict]:

        receivingStats = []
        for a_h in ("away", "home"):
            for table in data["gameStats"]["playerStats"][f"{a_h}Tables"]:
                for player in table["tableStats"]:
                    stats = player["player"]["playerGameStats2"]

                    if stats and isinstance(stats, list) and select_stats_section("TARGETS", stats[0]["stats"]):
                        stats = stats[0]["stats"]
                        # pprint(stats)
                        # raise

                        receivingStats.append({
                            "player_id":  player["player"]["playerId"],
                            "game_id": self.gameId,
                            "team_id": self.teamIds[a_h],
                            "opp_id": self.oppIds[a_h],
                            "tgt": select_stats_section("TARGETS", stats),
                            "rec": select_stats_section("RECEPTIONS", stats),
                            "rec_yds": select_stats_section("RECEIVING_YARDS", stats),
                            "rec_td": select_stats_section("RECEIVING_TOUCHDOWNS", stats),
                            "yac": select_stats_section("YARDS_AFTER_CATCH", stats),
                            "rec_1d": select_stats_section("RECEIVING_FIRST_DOWNS", stats)
                        })

        return receivingStats


    def _set_fumble_stats(self, data: dict) -> List[dict]:

        fumbleStats = []
        for a_h in ("away", "home"):
            for table in data["gameStats"]["playerStats"][f"{a_h}Tables"]:
                for player in table["tableStats"]:
                    stats = player["player"]["playerGameStats1"]

                    if stats and isinstance(stats, list) and select_stats_section("FUMBLES_LOST", stats[0]["stats"]):
                        stats = stats[0]["stats"]
                        # pprint(stats)
                        # raise

                        fumbleStats.append({
                            "player_id":  player["player"]["playerId"],
                            "game_id": self.gameId,
                            "team_id": self.teamIds[a_h],
                            "opp_id": self.oppIds[a_h],
                            "fum_lost": select_stats_section("FUMBLES_LOST", stats)
                        })

        return fumbleStats


    def _set_kick_stats(self, data: dict) -> List[dict]:
       
        kickStats = []
        for a_h in ("away", "home"):
            for table in data["gameStats"]["playerStats"][f"{a_h}Tables"]:
                for player in table["tableStats"]:
                    stats = player["player"]["playerGameStats3"]

                    if stats and isinstance(stats, list) and select_stats_section("FIELD_GOAL_ATTEMPTS", stats[0]["stats"]):
                        stats = stats[0]["stats"]
                        # pprint(stats)
                        # raise

                        kickStats.append({
                            "player_id":  player["player"]["playerId"],
                            "game_id": self.gameId,
                            "team_id": self.teamIds[a_h],
                            "opp_id": self.oppIds[a_h],
                            "fga": select_stats_section("FIELD_GOAL_ATTEMPTS", stats),
                            "fgm": select_stats_section("FIELD_GOALS_MADE", stats),
                        })

        return kickStats


    def _set_punt_stats(self, data: dict) -> List[dict]:
       
        puntStats = []
        for a_h in ("away", "home"):
            for table in data["gameStats"]["playerStats"][f"{a_h}Tables"]:
                for player in table["tableStats"]:
                    stats = player["player"]["playerGameStats4"]

                    if stats and isinstance(stats, list) and select_stats_section("PUNTS", stats[0]["stats"]):
                        stats = stats[0]["stats"]
                        # pprint(stats)
                        # raise

                        puntStats.append({
                            "player_id":  player["player"]["playerId"],
                            "game_id": self.gameId,
                            "team_id": self.teamIds[a_h],
                            "opp_id": self.oppIds[a_h],
                            "punts": select_stats_section("PUNTS", stats),
                            "punt_yds": select_stats_section("PUNT_YARDS", stats),
                            "in20": select_stats_section("PUNTS_INSIDE_20", stats),
                            "touchback": select_stats_section("PUNT_TOUCHBACKS", stats)
                        })

        return puntStats


    def _set_return_stats(self, data: dict) -> List[dict]:

        returnStats = []
        for a_h in ("away", "home"):
            for table in data["gameStats"]["playerStats"][f"{a_h}Tables"]:
                for player in table["tableStats"]:
                    kickStats = player["player"]["playerGameStats5"]
                    puntStats = player["player"]["playerGameStats6"]

                    if (kickStats and isinstance(kickStats, list) and int(select_stats_section("KICKOFF_RETURNS", kickStats[0]["stats"]))) or (puntStats and isinstance(puntStats, list) and int(select_stats_section("PUNT_RETURNS", puntStats[0]["stats"]))):
                        kickStats = kickStats[0]["stats"]
                        puntStats = puntStats[0]["stats"]
                        # pprint(kickStats)
                        # print("\n\n\n")
                        # pprint(puntStats)
                        # raise

                        returnStats.append({
                            "player_id":  player["player"]["playerId"],
                            "game_id": self.gameId,
                            "team_id": self.teamIds[a_h],
                            "opp_id": self.oppIds[a_h],
                            "kr": select_stats_section("KICKOFF_RETURNS", kickStats),
                            "kr_yds": select_stats_section("KICKOFF_RETURN_YARDS", kickStats),
                            "kr_td": select_stats_section("KICKOFF_RETURN_TOUCHDOWNS", kickStats),
                            "pr": select_stats_section("PUNT_RETURNS", puntStats),
                            "pr_yds": select_stats_section("PUNT_RETURN_YARDS", puntStats),
                            "pr_td": select_stats_section("PUNT_RETURN_TOUCHDOWNS", puntStats)
                        })

        return returnStats


    def _set_defense_stats(self, data: dict) -> List[dict]:
        
        defenseStats = []
        for a_h in ("away", "home"):
            for table in data["gameStats"]["playerStats"][f"{a_h}Tables"]:
                for player in table["tableStats"]:
                    stats = player["player"]["playerGameStats7"]

                    if stats and isinstance(stats, list):
                        stats = stats[0]["stats"]
                        # pprint(stats)
                        # raise

                        defenseStats.append({
                            "player_id":  player["player"]["playerId"],
                            "game_id": self.gameId,
                            "team_id": self.teamIds[a_h],
                            "opp_id": self.oppIds[a_h],
                            "tackles": select_stats_section("TOTAL_TACKLES", stats),
                            "sacks": select_stats_section("SACKS", stats),
                            "ints": select_stats_section("INTERCEPTIONS_FORCED", stats),
                            "pass_def": select_stats_section("PASSES_DEFENDED", stats)
                        })

        return defenseStats





   