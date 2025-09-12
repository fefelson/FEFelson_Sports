from typing import List

from .yahoo_normalizer import YahooNormalizer

from ...sport_normalizers import FootballNormalizer 

# for debugging
# from pprint import pprint

#############################################################################################
#############################################################################################



class YahooFootballNormalizer(YahooNormalizer, FootballNormalizer):
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
                "kick_plays": self._set_kick_plays(webData)
            }
        except KeyError:
            misc = {}
        return misc


    def _set_pass_plays(self, webData: dict) -> List[dict]:
        gameData = webData["gameData"]
        gameId = gameData["gameid"]
        pass_plays = []

        for play in gameData["play_by_play"].values():
            if int(play["type"]) in (2,3,4):

                teamId = f"{self._id_prefix}.t.{play['team']}"
                oppId = gameData["away_team_id"] if teamId == gameData["home_team_id"] else gameData["home_team_id"]

                mins,secs = play['clock'].split(":")
                secs = int(int(secs)*10/60)
                
                pass_plays.append({
                    "game_id": gameId,
                    "team_id": teamId,
                    "opp_id": oppId,
                    "play_num": play["play_id"],
                    "period": play["period"],
                    "down": play["down"],
                    "distance": play["distance"],
                    "clock": float(f"{mins}.{secs}"),
                    "yards_to_endzone": play["yards_to_endzone"],
                    "quarterback": play["sub_plays"][0]["sub_play"]["passer"],
                    "target": play["sub_plays"][0]["sub_play"].get("receiver"),
                    "yards": play["sub_plays"][0]["sub_play"]["yards"],
                    "direction": play["sub_plays"][0]["sub_play"]["direction"],
                    "completed": True if int(play["type"]) == 2 else False,
                    "touchdown": True if int(play["sub_plays"][0]["sub_play"]["points"]) == 6 else False,
                    "intercepted": True if int(play["type"]) == 4 else False
                })

        return pass_plays


    def _set_rush_plays(self, webData: dict) -> List[dict]:
        gameData = webData["gameData"]
        gameId = gameData["gameid"]
        rush_plays = []

        for play in gameData["play_by_play"].values():
            if int(play["type"]) == 1:

                teamId = f"{self._id_prefix}.t.{play['team']}"
                oppId = gameData["away_team_id"] if teamId == gameData["home_team_id"] else gameData["home_team_id"]
                
                mins,secs = play['clock'].split(":")
                secs = int(int(secs)*10/60)

                rush_plays.append({
                    "game_id": gameId,
                    "team_id": teamId,
                    "opp_id": oppId,
                    "play_num": play["play_id"],
                    "period": play["period"],
                    "down": play["down"],
                    "distance": play["distance"],
                    "clock": float(f"{mins}.{secs}"),
                    "yards_to_endzone": play["yards_to_endzone"],
                    "rusher": play["sub_plays"][0]["sub_play"]["rusher"],
                    "yards": play["sub_plays"][0]["sub_play"]["yards"],
                    "direction": play["sub_plays"][0]["sub_play"]["direction"],
                    "touchdown": True if int(play["sub_plays"][0]["sub_play"]["points"]) == 6 else False
                })

        return rush_plays


    def _set_kick_plays(self, webData: dict) -> List[dict]:
        gameData = webData["gameData"]
        gameId = gameData["gameid"]
        kick_plays = []

        for play in gameData["play_by_play"].values():
            if int(play["type"]) == 9:

                teamId = f"{self._id_prefix}.t.{play['team']}"
                oppId = gameData["away_team_id"] if teamId == gameData["home_team_id"] else gameData["home_team_id"]
                
                mins,secs = play['clock'].split(":")
                secs = int(int(secs)*10/60)

                kick_plays.append({
                    "game_id": gameId,
                    "team_id": teamId,
                    "opp_id": oppId,
                    "play_num": play["play_id"],
                    "period": play["period"],
                    "down": play["down"],
                    "distance": play["distance"],
                    "clock": float(f"{mins}.{secs}"),
                    "kicker": play["sub_plays"][0]["sub_play"]["player"],
                    "yards": play["sub_plays"][0]["sub_play"]["yards"],
                    "kick_good": True if int(play["sub_plays"][0]["sub_play"]["points"]) == 3 else False,
                    "kick_blocked": bool(int(play["sub_plays"][0]["sub_play"]["kick_blocked"]))
                })

        return kick_plays


    def _set_team_stats(self, data: dict) -> List[dict]:
        gameData = data["gameData"]
        gameId = gameData["gameid"]
        teamIds = {"away": gameData["away_team_id"], "home": gameData["home_team_id"]}
        oppIds = {"away": teamIds["home"], "home": teamIds["away"]}
        # pprint(data["statsData"])
        # raise
        teamStats = []
        for a_h in ("away", "home"):
            raw_stat_data = data["statsData"]["teamStatsByGameId"][gameId][teamIds[a_h]][f"{self._id_prefix}.stat_variation.2"]
            try:
                _,mins,secs = raw_stat_data[f"{self._id_prefix}.stat_type.935"].split(":")
                secs = int(int(secs)*10/60)
            except KeyError:
                mins = -1; secs = 0
            
            teamStats.append({
                "game_id": gameId,
                "team_id": teamIds[a_h],
                "opp_id": oppIds[a_h],
                "pts": gameData[f"total_{a_h}_points"],
                "plays": raw_stat_data[f"{self._id_prefix}.stat_type.946"],
                "yards": raw_stat_data[f"{self._id_prefix}.stat_type.945"],
                "pass_plays": raw_stat_data[f"{self._id_prefix}.stat_type.951"].split("-")[1],
                "pass_yards": raw_stat_data[f"{self._id_prefix}.stat_type.947"],
                "rush_plays": raw_stat_data[f"{self._id_prefix}.stat_type.920"],
                "rush_yards": raw_stat_data[f"{self._id_prefix}.stat_type.921"],
                "int_thrown": raw_stat_data[f"{self._id_prefix}.stat_type.926"],
                "fum_lost": raw_stat_data[f"{self._id_prefix}.stat_type.932"],
                "times_sacked": raw_stat_data[f"{self._id_prefix}.stat_type.927"],
                "sack_yds_lost": raw_stat_data[f"{self._id_prefix}.stat_type.928"],
                "penalties": raw_stat_data[f"{self._id_prefix}.stat_type.933"],
                "penalty_yards": raw_stat_data[f"{self._id_prefix}.stat_type.934"],
                "time_of_poss": f"{mins}.{secs}",
                "third_att": raw_stat_data[f"{self._id_prefix}.stat_type.941"].split("-")[1],
                "third_conv": raw_stat_data[f"{self._id_prefix}.stat_type.941"].split("-")[0],
                "fourth_att": raw_stat_data[f"{self._id_prefix}.stat_type.944"].split("-")[1],
                "fourth_conv": raw_stat_data[f"{self._id_prefix}.stat_type.944"].split("-")[0]        
            })
        return teamStats 


    def _set_player_stats(self, webData: dict) -> dict:
        playerStats = {
            "passing": self._set_passing_stats(webData),
            "rushing": self._set_rushing_stats(webData),
            "receiving": self._set_recieving_stats(webData),
            "fumbles": self._set_fumble_stats(webData),
            "punting": self._set_punt_stats(webData),
            "returns": self._set_return_stats(webData),
            "defense": self._set_defense_stats(webData)
        }
        return playerStats
        

    def _set_passing_stats(self, webData: dict) -> List[dict]:
        gameData = webData["gameData"]
        statsData = webData["statsData"]
        gameId = gameData["gameid"]
        teamIds = {"away": gameData["away_team_id"], "home": gameData["home_team_id"]}
        oppIds = {"away": teamIds["home"], "home": teamIds["away"]}

        passingStats = []
        for a_h in ("away", "home"):
            for playerId in gameData["playersByTeam"][teamIds[a_h]]:
                try:
                    playerStats = statsData["playerStats"][playerId][f"{self._id_prefix}.stat_variation.2"]
                    passingStats.append({
                        "player_id": playerId,
                        "game_id": gameId,
                        "team_id": teamIds[a_h],
                        "opp_id": oppIds[a_h],
                        "pass_att": playerStats[f"{self._id_prefix}.stat_type.103"],
                        "pass_comp": playerStats[f"{self._id_prefix}.stat_type.102"],
                        "pass_yds": playerStats[f"{self._id_prefix}.stat_type.105"],
                        "pass_td": playerStats[f"{self._id_prefix}.stat_type.108"],
                        "pass_int": playerStats[f"{self._id_prefix}.stat_type.109"],
                        "sacks": playerStats[f"{self._id_prefix}.stat_type.111"],
                        "sack_yds_lost": playerStats[f"{self._id_prefix}.stat_type.112"]
                    })
                except KeyError:
                    pass 
        return passingStats


    def _set_rushing_stats(self, webData: dict) -> List[dict]:
        gameData = webData["gameData"]
        statsData = webData["statsData"]
        gameId = gameData["gameid"]
        teamIds = {"away": gameData["away_team_id"], "home": gameData["home_team_id"]}
        oppIds = {"away": teamIds["home"], "home": teamIds["away"]}

        rushingStats = []
        for a_h in ("away", "home"):
            for playerId in gameData["playersByTeam"][teamIds[a_h]]:
                try:
                    playerStats = statsData["playerStats"][playerId][f"{self._id_prefix}.stat_variation.2"]
                    rushingStats.append({
                        "player_id": playerId,
                        "game_id": gameId,
                        "team_id": teamIds[a_h],
                        "opp_id": oppIds[a_h],
                        "rush_att": playerStats[f"{self._id_prefix}.stat_type.202"],
                        "rush_yds": playerStats[f"{self._id_prefix}.stat_type.203"],
                        "rush_td": playerStats[f"{self._id_prefix}.stat_type.207"]
                    })
                except KeyError:
                    pass 
        return rushingStats


    def _set_recieving_stats(self, webData: dict) -> List[dict]:
        gameData = webData["gameData"]
        statsData = webData["statsData"]
        gameId = gameData["gameid"]
        teamIds = {"away": gameData["away_team_id"], "home": gameData["home_team_id"]}
        oppIds = {"away": teamIds["home"], "home": teamIds["away"]}

        receivingStats = []
        for a_h in ("away", "home"):
            for playerId in gameData["playersByTeam"][teamIds[a_h]]:
                                
                try:
                    playerStats = statsData["playerStats"][playerId][f"{self._id_prefix}.stat_variation.2"]
                    receivingStats.append({
                        "player_id": playerId,
                        "game_id": gameId,
                        "team_id": teamIds[a_h],
                        "opp_id": oppIds[a_h],
                        "tgt": playerStats.get(f"{self._id_prefix}.stat_type.310"),
                        "rec": playerStats[f"{self._id_prefix}.stat_type.302"],
                        "rec_yds": playerStats[f"{self._id_prefix}.stat_type.303"],
                        "rec_td": playerStats[f"{self._id_prefix}.stat_type.309"]
                    })
                except KeyError:
                    pass 
        return receivingStats


    def _set_fumble_stats(self, webData: dict) -> List[dict]:
        gameData = webData["gameData"]
        statsData = webData["statsData"]
        gameId = gameData["gameid"]
        teamIds = {"away": gameData["away_team_id"], "home": gameData["home_team_id"]}
        oppIds = {"away": teamIds["home"], "home": teamIds["away"]}

        fumbleStats = []
        for a_h in ("away", "home"):
            for playerId in gameData["playersByTeam"][teamIds[a_h]]:
                try:
                    playerStats = statsData["playerStats"][playerId][f"{self._id_prefix}.stat_variation.2"]
                    if int(playerStats[f"{self._id_prefix}.stat_type.3"]) > 0:
                        fumbleStats.append({
                            "player_id": playerId,
                            "game_id": gameId,
                            "team_id": teamIds[a_h],
                            "opp_id": oppIds[a_h],
                            "fum_lost": playerStats[f"{self._id_prefix}.stat_type.3"]
                        })
                except KeyError:
                    pass 
        return fumbleStats


    def _set_punt_stats(self, webData: dict) -> List[dict]:
        gameData = webData["gameData"]
        statsData = webData["statsData"]
        gameId = gameData["gameid"]
        teamIds = {"away": gameData["away_team_id"], "home": gameData["home_team_id"]}
        oppIds = {"away": teamIds["home"], "home": teamIds["away"]}

        # pprint(statsData)
        # raise

        puntStats = []
        for a_h in ("away", "home"):
            for playerId in gameData["playersByTeam"][teamIds[a_h]]:
                try:
                    playerStats = statsData["playerStats"][playerId][f"{self._id_prefix}.stat_variation.2"]
                    puntStats.append({
                        "player_id": playerId,
                        "game_id": gameId,
                        "team_id": teamIds[a_h],
                        "opp_id": oppIds[a_h],
                        "punts": playerStats[f"{self._id_prefix}.stat_type.602"],
                        # playerStats[f"{self._id_prefix}.stat_type.604"]  is punt avg -- * puts = punt_yds
                        "punt_yds": round(float(playerStats[f"{self._id_prefix}.stat_type.604"]) * int(playerStats[f"{self._id_prefix}.stat_type.602"])),
                        "in20": playerStats.get(f"{self._id_prefix}.stat_type.605"),
                        "touchback": playerStats.get(f"{self._id_prefix}.stat_type.607")
                    })
                except (KeyError, ValueError):
                    pass 
        return puntStats


    def _set_return_stats(self, webData: dict) -> List[dict]:
        gameData = webData["gameData"]
        statsData = webData["statsData"]
        gameId = gameData["gameid"]
        teamIds = {"away": gameData["away_team_id"], "home": gameData["home_team_id"]}
        oppIds = {"away": teamIds["home"], "home": teamIds["away"]}

        returnStats = []
        for a_h in ("away", "home"):
            for playerId in gameData["playersByTeam"][teamIds[a_h]]:
                try:
                    playerStats = statsData["playerStats"][playerId][f"{self._id_prefix}.stat_variation.2"]
                    returnStats.append({
                        "player_id": playerId,
                        "game_id": gameId,
                        "team_id": teamIds[a_h],
                        "opp_id": oppIds[a_h],
                        "kr": playerStats[f"{self._id_prefix}.stat_type.502"],
                        "kr_yds": playerStats[f"{self._id_prefix}.stat_type.503"],
                        "kr_td": playerStats[f"{self._id_prefix}.stat_type.507"],
                        "pr": playerStats[f"{self._id_prefix}.stat_type.508"],
                        "pr_yds": playerStats[f"{self._id_prefix}.stat_type.509"],
                        "pr_td": playerStats[f"{self._id_prefix}.stat_type.513"]
                    })
                except KeyError:
                    pass 
        return returnStats


    def _set_defense_stats(self, webData: dict) -> List[dict]:
        gameData = webData["gameData"]
        statsData = webData["statsData"]
        gameId = gameData["gameid"]
        teamIds = {"away": gameData["away_team_id"], "home": gameData["home_team_id"]}
        oppIds = {"away": teamIds["home"], "home": teamIds["away"]}

        defenseStats = []
        for a_h in ("away", "home"):
            for playerId in gameData["playersByTeam"][teamIds[a_h]]:
                try:
                    playerStats = statsData["playerStats"][playerId][f"{self._id_prefix}.stat_variation.2"]
                    defenseStats.append({
                        "player_id": playerId,
                        "game_id": gameId,
                        "team_id": teamIds[a_h],
                        "opp_id": oppIds[a_h],
                        "tackles": playerStats.get(f"{self._id_prefix}.stat_type.704"),
                        "sacks": playerStats[f"{self._id_prefix}.stat_type.705"],
                        "ints": playerStats[f"{self._id_prefix}.stat_type.707"],
                        "pass_def": playerStats[f"{self._id_prefix}.stat_type.710"]
                    })
                except KeyError:
                    pass 
        return defenseStats





   