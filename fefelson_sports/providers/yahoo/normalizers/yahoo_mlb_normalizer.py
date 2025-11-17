import re
from typing import List

from .yahoo_normalizer import YahooNormalizer
from ...sport_normalizers import BaseballNormalizer
from ....utils.logging_manager import get_logger

# for debugging
# from pprint import pprint

#############################################################################################
#############################################################################################

atbat_tokens = {

    "struck out": 0,
    "strikes out": 0,
    "called out on strikes": 0,

    "fouled out": 1,
    "fouls out": 1,
    
    "flied out": 2,
    "flies out": 2,
    "flied into double play": 2,
    "flied into triple play": 2,

    "grounded out": 3,
    "grounds out": 3,
    "grounded into double play": 3,
    "grounded into triple play": 3,
    "hit into fielder's choice": 3,
    "reached on fielder's choice": 3,
    "reaches on a fielder's choice": 3,
    r"reached on \[\w+\.\w+\.\d+\]'s \w+ error": 3,
    "reaches on error": 3,
    
    "popped out": 4,
    "pops out": 4,
    "popped into double play": 4,

    "lined out": 5,
    "lines out": 5,
    "lined into triple play": 5,
    "lined into double play": 5,

    "hit by pitch": 6,
    
    "walked": 7,
    "walks": 7,

    "reached on an infield single": 8, 
    "singled": 8,
    "singles": 8,

    "doubled": 9,
    "doubles": 9,              
    "ground rule double": 9,

    "tripled": 10,
    "triples": 10,

    "homered": 11,
    "homers": 11,
    "hit an inside the park home run": 11,
}


token_skip = [
    "unknown into double play",
    "On initial placement",
    "was skipped",
    "batted out of order",
    "out on batter's interference",
    "reached on catcher's interference",
     
    "bunt",
    "wild pitch",
    "sacrifice fly",
    "sacrificed",

]

def find_matching_token(input_string):
    """
    Searches for a token string from a list of tokens within the input string.
    Returns the first matching token string, or None if no match is found.
    """
    for token in atbat_tokens:
        # Use re.search to look for the token as a substring
        # Escape the token to handle any special regex characters
        if re.search(token, input_string):
            return atbat_tokens[token]
    return None



#############################################################################################
#############################################################################################



class YahooMLBNormalizer(BaseballNormalizer, YahooNormalizer):
    """Normalizer for Yahoo Baseball data (MLB)."""

    def __init__(self, leagueId: str):
        super().__init__("MLB")


    def _set_atbats(self, webData: dict) -> List[dict]:
        
        atBats = []

        for play in webData["playByPlay"]: 
            if play["playTypeId"] == "RESULT":

                a_h = "home" if play["gamePeriod"]["inningStage"] == "BOTTOM" else "away"
                result = find_matching_token(play["text"])
                if result is not None:
                    atBats.append({
                        "game_id": self.gameId,
                        "team_id": self.teamIds[a_h],
                        "opp_id": self.oppIds[a_h],
                        "play_num": str((int(play['playId']) - 1)/100),
                        "pitcher_id": play["playInfo"]["pitcherId"],
                        "batter_id": play["playInfo"]["batterId"],
                        "at_bat_type_id": result,
                        "period": play["gamePeriod"]["period"]
                    })
        
        return atBats


    def _set_pitches(self, webData: dict) -> List[dict]:
                
        pitchList = []
        for play in webData["playByPlay"]: 
            if play["playTypeId"] == "RESULT":
                a_h = "home" if play["gamePeriod"]["inningStage"] == "BOTTOM" else "away"
                pitches = play["playInfo"]["pitches"]
                
                for i, pitch in enumerate(pitches):

                    balls = int(pitches[i-1]["balls"]) if i > 0 else 0
                    strikes = int(pitches[i-1]["balls"]) if i > 0 else 0
                    sequence = int(pitch["sequence"])
                    playNum = (int(play['playId']) - 1)/100
            
                    pitchList.append({
                        "game_id": self.gameId,
                        "play_num": playNum - len(pitches) + sequence,
                        "pitcher_id": pitch['pitcherId'],
                        "batter_id": pitch['batterId'],
                        "pitch_type": pitch['pitchType'],
                        "pitch_result": pitch['result'],
                        "period": play["gamePeriod"]["period"],
                        "sequence": sequence,
                        "balls": balls,
                        "strikes": strikes,
                        "vertical": pitch['vertical'],
                        "horizontal": pitch['horizontal'],
                        "velocity": pitch['velocity']
                    })

        return pitchList


    def _set_batter_stats(self, data: dict) -> List[dict]:
        # pprint(webData["statsData"])
        # raise

        playerStats=[]

        for a_h in ("away", "home"):
            for player in data["gameStats"][f"{a_h}TeamLineup"]:
                stats = player["player"]["playerGameStats0"]

                if stats:
                    stats = stats[0]["stats"]
                    playerStats.append({
                        "player_id": player["player"]["playerId"],
                        "game_id": self.gameId,
                        "team_id": self.teamIds[a_h],
                        "opp_id": self.oppIds[a_h],
                        "ab": stats[0]["value"],
                        "bb": stats[6]["value"],
                        "r": stats[1]["value"],
                        "h": stats[2]["value"],
                        "hr": stats[4]["value"],
                        "rbi": stats[3]["value"],
                        "sb": stats[5]["value"],
                        "so": stats[7]["value"]
                    })  
        # pprint(playerStats)
        # raise               
                
        return playerStats

 


    def _set_pitcher_stats(self, data: dict) -> List[dict]:
        

        playerStats=[]

        winningPitcherId = data["boxscoreResult"]["games"][0]["winningPitcher"]["playerId"]
        losingPitcherId = data["boxscoreResult"]["games"][0]["losingPitcher"]["playerId"]
        try:
            savingPitcherId = data["boxscoreResult"]["games"][0]["savingPitcher"]["playerId"]
        except TypeError:
            savingPitcherId = -1

        for a_h in ("away", "home"):
            for player in data["gameStats"][f"{a_h}TeamLineup"]:
                stats = player["player"]["playerGameStats1"]

                if stats:
                    stats = stats[0]["stats"]
                    full_ip, partial_ip = stats[0]["value"].split(".")

                    playerStats.append({
                        "player_id": player["player"]["playerId"],
                        "game_id": self.gameId,
                        "team_id": self.teamIds[a_h],
                        "opp_id": self.oppIds[a_h],
                        "full_ip": full_ip,
                        "partial_ip": partial_ip,
                        "bba": stats[4]["value"],
                        "ha": stats[1]["value"],
                        "k": stats[5]["value"],
                        "hra": stats[7]["value"],
                        "ra": stats[2]["value"],
                        "er": stats[3]["value"],
                        "w": 1 if player["player"]["playerId"] == winningPitcherId else 0,
                        "l":  1 if player["player"]["playerId"] == losingPitcherId else 0,
                        "sv":  1 if player["player"]["playerId"] == savingPitcherId else 0
                    })  

        # pprint(playerStats)
        # raise               
                
        return playerStats
                    




    def _set_batting_order(self, data: dict) -> List[dict]:
        
        battingOrder = []
        for a_h in ("away", "home"):
            for player in data[f"{a_h}TeamLineup"]:
                if player["positionClass"] == "B":

                    battingOrder.append({
                        "game_id": self.gameId,
                        "player_id": player["player"]["playerId"],
                        "team_id": self.teamIds[a_h],
                        "opp_id": self.oppIds[a_h],
                        "batt_order": player["order"],
                        "sub_order": player["subOrder"],
                        "pos": player["position"]["abbreviation"]
                    })

        # pprint(battingOrder)
        # raise

        return battingOrder


    def _set_bullpen(self, data: dict) -> List[dict]:

        pitchingOrder = []
        for a_h in ("away", "home"):
            for player in data[f"{a_h}TeamLineup"]:
                if player["positionClass"] == "P":

                    pitchingOrder.append({
                        "game_id": self.gameId,
                        "player_id": player["player"]["playerId"],
                        "team_id": self.teamIds[a_h],
                        "opp_id": self.oppIds[a_h],
                        "pitch_order": player["order"]
                })

        # pprint(pitchingOrder)
        # raise

        return pitchingOrder


    def _set_lineups(self, webData: dict) -> dict:
        lineups = {}
        lineups["batting"] = self._set_batting_order(webData)
        lineups["pitching"] = self._set_bullpen(webData)
        
        return lineups


    def _set_player_stats(self, webData: dict) -> List:
        playerStats = {
            "batting_stats": self._set_batter_stats(webData),
            "pitching_stats": self._set_pitcher_stats(webData)
        }
        return playerStats


    def _set_misc(self, webData: dict) -> dict:
        misc = {"at_bats": self._set_atbats(webData),
                "pitches": self._set_pitches(webData)}
        return misc


    def _set_team_stats(self, data: dict) -> List[dict]:
        teamStats = []
        
        for a_h in ("away", "home"):
            opp = "away" if a_h == "home" else "home"
            try:
                gameStats0 = data["gameStats"][f"{a_h}TeamGameStats0"]["stats"]
                gameStats1 = data["gameStats"][f"{a_h}TeamGameStats1"]["stats"]    

                teamStats.append({
                    "game_id": self.gameId,
                    "team_id": self.teamIds[a_h],
                    "opp_id": self.oppIds[a_h],
                    "r": data["boxscoreResult"]["games"][0][f"{a_h}Score"],
                    "h": gameStats0[0]['value'],
                    "hr": gameStats0[2]['value'],
                    "sb": gameStats0[4]['value'],
                    "lob": gameStats0[5]['value'],
                    "bba": gameStats1[4]['value'],
                    "ha": gameStats1[2]['value'],
                    "ra": data["boxscoreResult"]["games"][0][f"{opp}Score"],
                    "er": gameStats1[1]['value'],
                    "k": gameStats1[0]['value']
                })
            except TypeError as e:
                get_logger().warning(f"_set_team_stats - {e}")

        # pprint(teamStats)
        # raise
        return teamStats  

