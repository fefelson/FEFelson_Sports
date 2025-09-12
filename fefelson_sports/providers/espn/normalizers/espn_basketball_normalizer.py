from typing import Any, Dict, List

from .espn_normalizer import ESPNNormalizer
from ...sport_normalizers import BasketballNormalizer

# for debugging
# from pprint import pprint


#############################################################################################
#############################################################################################



class ESPNBasketballNormalizer(BasketballNormalizer, ESPNNormalizer):
    """Normalizer for ESPN Basketball data (NBA and NCAAB)."""

    def __init__(self, leagueId: str):
        BasketballNormalizer.__init__(self, leagueId)
        ESPNNormalizer.__init__(self, leagueId)
    


    def _set_linueups(self, webData):
        return None 
    

    def _set_misc(self, webData):
        pass


    def _set_players(self, data: dict) -> List[dict]:
        players = []
        for team in data:
            for s_b in team["stats"]:
                for ath in s_b.get("athlts", []):
                    players.append(ath["athlt"])
        
        return players  
    

    def _set_player_shots(self, data: dict) -> List[dict]:
        raise NotImplementedError
    

    def _set_player_stats(self, data: dict) -> List[dict]:
        pass
    

    def _set_team_stats(self, data: dict) -> List[dict]:
        teamData = data["matchData"]["tmStats"]
        gameId = data["matchData"]["gmStrp"]["gid"]
        teamIds = {"away": teamData["away"]['t']['id'], "home": teamData["home"]['t']['id']}
        oppIds = {"away": teamIds["home"], "home": teamIds["away"]}
        teamStats = []

        for a_h in ("away", "home"):
            
            teamStats.append({
                "game_id": gameId,
                "team_id": teamIds[a_h],
                "opp_id": oppIds[a_h],
                "pts": data["matchData"]['gmStrp']['tms'][0 if a_h == 'home' else 1]["score"],
                "fb_pts": teamData[a_h]['s']['fastBreakPoints']['d'],
                "pts_in_pt": teamData[a_h]['s']['pointsInPaint']['d']
            })
        return teamStats 
        
