from typing import List 

from .espn_normalizer import ESPNNormalizer

from ...sport_normalizers import FootballNormalizer

# for debugging
from pprint import pprint 

#############################################################################################
#############################################################################################



class ESPNFootballNormalizer(ESPNNormalizer, FootballNormalizer):
    """Normalizer for ESPN Football data (NFL and NCAAF)."""

    def __init__(self, leagueId: str):
        super().__init__(leagueId)


    def _set_misc(self, webData: dict):
        # pprint(webData)
        # raise
        pass


    def _set_player_stats(self, webData: dict) -> dict:
        try:
            playerStats = {
            "passing": self._set_passing_stats(webData),
            "rushing": self._set_rushing_stats(webData),
            "receiving": self._set_recieving_stats(webData),
            "fumbles": self._set_fumble_stats(webData),
            "defense": self._set_defense_stats(webData)
            }
        except KeyError:
            playerStats = None
            
        return playerStats


    def _set_team_stats(self, data: dict) -> List[dict]:
        # pprint(data["matchData"]["tmStats"])
        # raise
        teamStats = []

        try:
            teamData = data["matchData"]["tmStats"]
            gameId = data["matchData"]["gmStrp"]["gid"]
            teamIds = {"away": teamData["away"]['t']['id'], "home": teamData["home"]['t']['id']}
            oppIds = {"away": teamIds["home"], "home": teamIds["away"]}
            
            for a_h in ("away", "home"):
                mins,secs = teamData[a_h]['s']['possessionTime']['d'].split(":")
                secs = int(int(secs)*10/60)

                try:
                    # NFL stats not in NCAAF espn
                    passPlays = int(teamData[a_h]['s']['totalOffensivePlays']['d']) - int(teamData[a_h]['s']['rushingAttempts']['d'])
                    drives=teamData[a_h]['s']['totalDrives']['d']
                    timesSacked=teamData[a_h]['s']['sacksYardsLost']['d'].split("-")[0],
                    sackYdsLost=teamData[a_h]['s']['sacksYardsLost']['d'].split("-")[1]
                    rzAtt=teamData[a_h]['s']['redZoneAttempts']['d'].split("-")[0]
                    rzConv=teamData[a_h]['s']['redZoneAttempts']['d'].split("-")[1]
                    tdDefST=teamData[a_h]['s']['defensiveTouchdowns']['d']
                except KeyError:
                    drives=None; timesSacked=None; sackYdsLost=None; rzAtt=None;
                    rzConv=None; tdDefST=None
                    passPlays=int(teamData[a_h]['s']['completionAttempts']['d'].split("/")[-1])

                teamStats.append({
                    "game_id": gameId,
                    "team_id": teamIds[a_h],
                    "opp_id": oppIds[a_h],
                    "pts": data["matchData"]['gmStrp']['tms'][0 if a_h == 'home' else 1]["score"],
                    "drives": drives,
                    "yards": teamData[a_h]['s']['totalYards']['d'],
                    "pass_plays": passPlays,
                    "pass_yards": teamData[a_h]['s']['netPassingYards']['d'],
                    "rush_plays": teamData[a_h]['s']['rushingAttempts']['d'],
                    "rush_yards": teamData[a_h]['s']['rushingYards']['d'],
                    "int_thrown": teamData[a_h]['s']['interceptions']['d'],
                    "fum_lost": teamData[a_h]['s']['fumblesLost']['d'],
                    "times_sacked": timesSacked,
                    "sack_yds_lost": sackYdsLost,
                    "penalties": teamData[a_h]['s']['totalPenaltiesYards']['d'].split("-")[0],
                    "penalty_yards": teamData[a_h]['s']['totalPenaltiesYards']['d'].split("-")[1],
                    "time_of_poss": f"{mins}.{secs}",
                    "third_att": teamData[a_h]['s']['thirdDownEff']['d'].split("-")[0],
                    "third_conv": teamData[a_h]['s']['thirdDownEff']['d'].split("-")[1],
                    "fourth_att": teamData[a_h]['s']['fourthDownEff']['d'].split("-")[0],
                    "fourth_conv": teamData[a_h]['s']['fourthDownEff']['d'].split("-")[1],
                    "rz_att": rzAtt,
                    "rz_conv": rzConv,
                    "def_st_td": tdDefST,

                })
        except KeyError:
            pass

        return teamStats 


    def _set_passing_stats(self, webData: dict) -> List[dict]:
        gameId = webData["gmStrp"]["gid"]
        teamIds = {"away": webData["prsdTms"]["away"]['id'], "home": webData["prsdTms"]["home"]['id']}
        oppIds = {"away": teamIds["home"], "home": teamIds["away"]}

        passingStats = []
        for a_h in ("away", "home"):
            for group in webData["bxscr"][a_h == "home"]["stats"]:
                if group['type'] == 'passing':
                    for athlete in group["athlts"]:
                        try:
                            passingStats.append({
                                "player_id": athlete["athlt"]["id"],
                                "game_id": gameId,
                                "team_id": teamIds[a_h],
                                "opp_id": oppIds[a_h],
                                "pass_att": athlete["stats"][0].split("/")[1],
                                "pass_comp": athlete["stats"][0].split("/")[0],
                                "pass_yds": athlete["stats"][1],
                                "pass_td": athlete["stats"][3],
                                "pass_int": athlete["stats"][4],
                                "sacks": athlete["stats"][5].split("-")[0],
                                "sack_yds_lost": athlete["stats"][5].split("-")[0]
                            })
                        except (KeyError, IndexError):
                            pass 
        return passingStats


    def _set_rushing_stats(self, webData: dict) -> List[dict]:
        gameId = webData["gmStrp"]["gid"]
        teamIds = {"away": webData["prsdTms"]["away"]['id'], "home": webData["prsdTms"]["home"]['id']}
        oppIds = {"away": teamIds["home"], "home": teamIds["away"]}

        rushingStats = []
        for a_h in ("away", "home"):
            for group in webData["bxscr"][a_h == "home"]["stats"]:
                if group['type'] == 'rushing':
                    for athlete in group["athlts"]:
                        try:
                            rushingStats.append({
                                "player_id": athlete["athlt"]["id"],
                                "game_id": gameId,
                                "team_id": teamIds[a_h],
                                "opp_id": oppIds[a_h],
                                "rush_att": athlete["stats"][0],
                                "pass_yds": athlete["stats"][1],
                                "rush_td": athlete["stats"][3]
                            })
                        except KeyError:
                            pass 
        return rushingStats


    def _set_recieving_stats(self, webData: dict) -> List[dict]:

        gameId = webData["gmStrp"]["gid"]
        teamIds = {"away": webData["prsdTms"]["away"]['id'], "home": webData["prsdTms"]["home"]['id']}
        oppIds = {"away": teamIds["home"], "home": teamIds["away"]}

        receivingStats = []
        for a_h in ("away", "home"):
            for group in webData["bxscr"][a_h == "home"]["stats"]:
                if group['type'] == 'receiving':
                    for athlete in group["athlts"]:
                        
                        try:
                            # In NFL and not NCAAF espn
                            tgt=athlete["stats"][5]
                        except IndexError:
                            tgt=None

                        try:
                            receivingStats.append({
                                "player_id": athlete["athlt"]["id"],
                                "game_id": gameId,
                                "team_id": teamIds[a_h],
                                "opp_id": oppIds[a_h],
                                "tgt": tgt,
                                "rec": athlete["stats"][0],
                                "rec_yds": athlete["stats"][1],
                                "rec_td": athlete["stats"][3]
                            })
                        except KeyError:
                            pass 
        return receivingStats


    def _set_fumble_stats(self, webData: dict) -> List[dict]:
        gameId = webData["gmStrp"]["gid"]
        teamIds = {"away": webData["prsdTms"]["away"]['id'], "home": webData["prsdTms"]["home"]['id']}
        oppIds = {"away": teamIds["home"], "home": teamIds["away"]}

        fumbleStats = []
        for a_h in ("away", "home"):
            for group in webData["bxscr"][a_h == "home"]["stats"]:
                if group['type'] == 'fumbles':
                    for athlete in group["athlts"]:
                        try:
                            fumbleStats.append({
                                "player_id": athlete["athlt"]["id"],
                                "game_id": gameId,
                                "team_id": teamIds[a_h],
                                "opp_id": oppIds[a_h],
                                "fum_lost": athlete["stats"][1]
                            })
                        except KeyError:
                            pass 
        return fumbleStats


    def _set_defense_stats(self, webData: dict) -> List[dict]:
        gameId = webData["gmStrp"]["gid"]
        teamIds = {"away": webData["prsdTms"]["away"]['id'], "home": webData["prsdTms"]["home"]['id']}
        oppIds = {"away": teamIds["home"], "home": teamIds["away"]}

        defenseStats = []
        for a_h in ("away", "home"):
            for group in webData["bxscr"][a_h == "home"]["stats"]:
                if group['type'] == 'defensive':
                    for athlete in group["athlts"]:
                        try:
                            defenseStats.append({
                                "player_id": athlete["athlt"]["id"],
                                "game_id": gameId,
                                "team_id": teamIds[a_h],
                                "opp_id": oppIds[a_h],
                                "tackles": athlete["stats"][0],
                                "sacks": athlete["stats"][2],
                                "qb_hits": athlete["stats"][5],
                                "pass_def": athlete["stats"][4]
                            })
                        except KeyError:
                            pass 
        return defenseStats
    


