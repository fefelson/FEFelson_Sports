from abc import ABC, abstractmethod
from difflib import get_close_matches
from sqlalchemy.orm import Session

from ..orms.database import get_db_session
from ..stores.base import ProviderStore
from ..stores.core import GameStore, PeriodStore, PlayerStore, StadiumStore
from ..stores.gaming import GameLineStore, OverUnderStore

# for debugging
from pprint import pprint

##################################################################
##################################################################


class DatabaseAgent(ABC):
    """Abstract interface for database operations."""
    
    @abstractmethod
    def insert_boxscore(self, boxscore: dict):
        raise NotImplementedError


###################################################################
###################################################################


class SQLAlchemyDatabaseAgent(DatabaseAgent):

    def __init__(self, league_id: str):
        super().__init__()
        self.leagueId = league_id

        self.stadiumStore = StadiumStore()
        self.providerStore = ProviderStore()
        self.gameStore = GameStore()
        self.gamelineStore = GameLineStore()
        self.periodStore = PeriodStore()
        self.ouStore = OverUnderStore()  
        self.playerStore = PlayerStore()   


    def _create_mapping(self, boxscore: dict, session: Session):
        # pprint(boxscore)
        # raise

        mapping = {}
        yahooBox = boxscore.get("yahoo")
        espnBox = boxscore.get("espn")

        for a_h in ("game_id", "away_id", "home_id"):
            if yahooBox:
                mapping[boxscore["yahoo"]["game"][a_h]] = boxscore[a_h] 

            if espnBox:
                mapping[boxscore["espn"]["game"][a_h]] = boxscore[a_h]  
        
        if yahooBox and espnBox:

            espn_by_name = {f"{p['dspNm'].lower()}": p['id'] for p in boxscore["espn"]["players"]} 

            for data in boxscore["yahoo"]["players"]:
                # print(data)
                yahooId = data.pop("player_id")
                data["league_id"] = self.leagueId
                name = f"{data['first_name']} {data['last_name']}".lower()

                match = get_close_matches(name, espn_by_name.keys(), n=2, cutoff=0.7)
                # print(name, match)
                espnId  = espn_by_name.pop(match[0]) if match else -1
                
                playerId = self.providerStore.get_inside_id("yahoo", self.leagueId, "player", yahooId, session)
                # print(playerId, yahooId)
                if playerId == -1 and not mapping.get(yahooId):     
                    playerId = self.playerStore.insert(session, data)
                    # print(f"new playerId {playerId}")
                    self.providerStore.set_provider_id("yahoo", self.leagueId, "player", yahooId, playerId, session)
                    
                    if espnId != -1:
                        self.providerStore.set_provider_id("espn", self.leagueId, "player", espnId, playerId, session)

                mapping[yahooId] = playerId 
                if espnId != -1:
                    mapping[espnId] = playerId

        return mapping


    def _insert_common_data(self, boxscore: dict, mapping: dict, session: Session):
        """Insert common boxscore data (stadium, game, periods)."""
        # Handle stadium

        espnBox = boxscore.get("espn")

        stadium = boxscore["yahoo"]["stadium"]
        if not stadium.get("name") or stadium["name"] == "" and espnBox:
            stadium["name"] = boxscore["espn"]["stadium"].get("name")
        self.stadiumStore.insert(session, stadium)

        # Handle game
        game = boxscore["yahoo"]["game"]
        for label in ("game_id", "home_id", "away_id", "winner_id", "loser_id"):
            game[label] = mapping[game[label]]

        self.gameStore.insert(session, game)

        
        # Handle periods
        for period in boxscore["yahoo"]["periods"]:
            for label in ("game_id", "team_id", "opp_id"):
                period[label] = mapping[period[label]]
            self.periodStore.insert(session, period)

        for gameline in boxscore["yahoo"]["gameLines"]:
            for label in ("game_id", "team_id", "opp_id"):
                gameline[label] = mapping[gameline[label]]
            self.gamelineStore.insert(session, gameline)

        oU = boxscore["yahoo"]["overUnder"]
        if oU:
            oU["game_id"] = mapping[oU["game_id"]]
            self.ouStore.insert(session, oU)
            

    @abstractmethod
    def _insert_league_specific_data(self, boxscore: dict, mapping: dict, session: Session):
        """Abstract method for league-specific inserts."""
        pass


    def insert_boxscore(self, boxscore: dict, session = None ) -> None:
        """Insert boxscore data into the database, including common and league-specific data."""

        if not boxscore.get("yahoo"):
            return None
        if not boxscore or boxscore["home_id"] == -1 or boxscore["away_id"] == -1 or boxscore["yahoo"]["game"]["game_result"] == "unknown":
            return None 

        mapping = self._create_mapping(boxscore, session)
        self._insert_common_data(boxscore, mapping, session)
        self._insert_league_specific_data(boxscore, mapping, session)
               
    

        