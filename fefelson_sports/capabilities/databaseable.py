from abc import ABC, abstractmethod
from difflib import get_close_matches
from sqlalchemy.exc import IntegrityError
from typing import Any, Optional
from itertools import chain

from ..database.models.baseball import BattingOrder, Bullpen, BaseballTeamStat, Pitch, AtBat, BattingStat, PitchingStat
from ..database.models.core import Game, Period, Player, ProviderMapping, Team, Stadium
from ..database.models.database import engine, get_db_session
from ..database.models.gaming import GameLine, OverUnder

from ..utils.logging_manager import get_logger

#################################################################
#################################################################

def map_players(yahooBox, espnBox):

    yahoo_by_name = {f"{p['first_name'].lower()} {p['last_name'].lower()}": p["player_id"] for p in yahooBox["players"]}
    mapping = {}

    for espn_player in[ab[index] for ab in espnBox["misc"]["at_bats"] for index in ("batter_id", "pitcher_id")]:
        name = espn_player.lower()
        match = get_close_matches(name, yahoo_by_name.keys(), n=1, cutoff=0.7)
        
        if match:
            mapping[espn_player.lower()] = yahoo_by_name[match[0]]
            
        else:
            # Flag for review
            print(f"No match found for ESPN player: {espn_player}")

    return mapping


#################################################################
#################################################################


class Databaseable(ABC):


    def __init__(self, dbAgent: Optional["DatabaseAgent"]=None):
        self.dbAgent = dbAgent # Handles database operations


    def _set_dbAgent(self, dbAgent: "DatabaseAgent"):
        self.dbAgent = dbAgent


    @abstractmethod
    def save_to_db(self, data: Any):
        """Saves self.data to the database."""
        raise NotImplementedError   



    @abstractmethod
    def load_from_db(self) -> Any:
        """Loads data from the database into dataclass object using and returns it."""
        raise NotImplementedError  



###################################################################
###################################################################


class DatabaseAgent(ABC):
    """Abstract interface for database operations."""
    
    @abstractmethod
    def insert_boxscores(self, dataList: "BoxscoreData"):
        raise NotImplementedError


    @abstractmethod
    def insert_player(self, dataList: "BoxscoreData"):
        raise NotImplementedError


###################################################################
###################################################################


class SQLAlchemyDatabaseAgent(DatabaseAgent):
    """SQLAlchemy implementation of the IDatabaseAgent interface."""


    def _flatten(items):
        """Recursively flatten misc, yielding individual SQLAlchemy objects."""
        if items is None:  # Handle None case
            return
        for item in items:
            if isinstance(item, list):
                yield from SQLAlchemyDatabaseAgent._flatten(item)  # Recurse into nested lists
            else:
                yield item  # Yield individual objects


    @staticmethod
    def insert_boxscore(boxscore: "BoxscoreData") -> None:
        raise NotImplementedError


    @staticmethod
    def insert_player(player: dict) -> None:
        raise NotImplementedError



class MLBAlchemy(SQLAlchemyDatabaseAgent):

    @staticmethod
    def insert_player(player: dict) -> None:
        with get_db_session() as session:
            # Insert Player with check
            if not session.query(Player).filter_by(player_id=player["player_id"]).first():
                session.add(Player(**player))   


    @staticmethod
    def insert_boxscore(boxscore: "BoxscoreData") -> None:
        """Insert boxscore data into the database."""
        
        yahooBox = boxscore["yahooBox"]
        espnBox = boxscore["espnBox"]

        with get_db_session() as session:
            if yahooBox is None:
                return None 

            if espnBox:
                if (yahooBox["stadium"].get("name") is None or yahooBox["stadium"]["name"] == "") and (espnBox["stadium"].get("name") is not None and espnBox["stadium"]["name"] != ""):
                    yahooBox["stadium"]["name"] = espnBox["stadium"]["name"]
            
            if not session.query(Stadium).filter_by(stadium_id=yahooBox["stadium"]["stadium_id"]).first():
                session.add(Stadium(**yahooBox["stadium"]))

            game = yahooBox["game"]
            # Insert Game with check
            if not session.query(Game).filter_by(game_id=game["game_id"]).first():
                session.add(Game(**game))
                try:
                    for batter in yahooBox["lineups"]["batting"]:
                        if session.query(Player).filter_by(player_id=batter["player_id"]).first():
                            session.add(BattingOrder(**batter))
                except KeyError:
                    pass 
                try:
                    for pitcher in yahooBox["lineups"]["pitching"]:
                        if session.query(Player).filter_by(player_id=pitcher["player_id"]).first():
                            session.add(Bullpen(**pitcher))
                except KeyError:
                    pass


                for provider, box in (("yahoo", yahooBox), ("espn", espnBox)):
                    if box is not None:
                        mappings = {
                                "provider": provider,
                                "entity_type": "game",
                                "entity_id": yahooBox["game"]["game_id"],
                                "provider_id": box["game"]["game_id"]
                        }
                        existing = session.query(ProviderMapping).filter(
                            ProviderMapping.provider == mappings["provider"],
                            ProviderMapping.entity_type == mappings["entity_type"],
                            ProviderMapping.entity_id == mappings["entity_id"]
                        ).first()

                        if not existing:
                            session.add(ProviderMapping(**mappings))

                if yahooBox.get("gameLines"):
                    for gl in yahooBox["gameLines"]:
                        # Insert Game with check
                        existing = session.query(GameLine).filter(
                                    GameLine.game_id == gl["game_id"],
                                    GameLine.team_id == gl["team_id"]
                                ).first()
                        if not existing:
                            session.add(GameLine(**gl))

                if yahooBox.get("overUnder"):
                    if not session.query(OverUnder).filter_by(game_id=yahooBox["overUnder"]["game_id"]).first():
                        session.add(OverUnder(**yahooBox["overUnder"]))


                periods = []
                for p in yahooBox["periods"]:
                    try:
                        int(p["pts"])
                        periods.append(p)
                    except ValueError:
                        pass
                
                for p in periods:
                    # Insert Period with check
                    existing = session.query(Period).filter(
                                Period.game_id == p["game_id"],
                                Period.team_id == p["team_id"],
                                Period.period == p["period"]
                            ).first()
                    if not existing:
                        session.add(Period(**p))

                game = yahooBox["game"]

                teamStats = []
                if espnBox:
                    for espn in espnBox["teamStats"]:
                        teamStats.append( {"game_id": game["game_id"], 
                                "team_id": espn["team_id"],
                                "opp_id": game["home_id"] if espn["team_id"] == game["away_id"] else game["away_id"],
                                "runs": espn["batting"]["r"],
                                "hits": espn["batting"]["h"],
                                "errors": espn["errors"]
                                })
                for stats in teamStats:
                    existing = session.query(BaseballTeamStat).filter(
                                BaseballTeamStat.game_id == stats["game_id"],
                                BaseballTeamStat.team_id == stats["team_id"]
                            ).first()
                    if not existing:
                        session.add(BaseballTeamStat(**stats))

                at_bats = yahooBox["misc"]["at_bats"]

                # Insert Game with check
                for ab in at_bats:
                    batter = session.query(Player).filter(
                                Player.player_id == ab["batter_id"]
                            ).first()
                    pitcher = session.query(Player).filter(
                                Player.player_id == ab["pitcher_id"]
                            ).first()
                    if batter and pitcher:
                        session.add(AtBat(**ab))  

                pitches = []
                try:
                    playerMappings = map_players(yahooBox, espnBox)
                    yahoo = yahooBox["game"]
                    espn = espnBox["misc"]["pitches"]
                    for pitch in espn:
                        pitch["game_id"] = yahoo["game_id"]
                        pitch["batter_id"] = playerMappings[pitch["batter_id"].lower()]
                        pitch["pitcher_id"] = playerMappings[pitch["pitcher_id"].lower()]
                        pitches.append(pitch)
                except (TypeError, KeyError):
                    pass 
            
                for p in pitches:
                    batter = session.query(Player).filter(
                                Player.player_id == p["batter_id"]
                            ).first()
                    pitcher = session.query(Player).filter(
                                Player.player_id == p["pitcher_id"]
                            ).first()
                    if batter and pitcher:
                        session.add(Pitch(**p))

                batterStats = yahooBox["misc"]["batting_stats"]
                pitcherStats = yahooBox["misc"]["pitching_stats"]


                for bs in batterStats:
                    batter = session.query(Player).filter(
                                Player.player_id == bs["batter_id"]
                            ).first()
                    existing = session.query(BattingStat).filter(
                                BattingStat.game_id == bs["game_id"],
                                BattingStat.batter_id == bs["batter_id"]
                            ).first()
                    if batter and not existing:
                        session.add(BattingStat(**bs))


                for ps in pitcherStats:
                    pitcher = session.query(Player).filter(
                                Player.player_id == ps["pitcher_id"]
                            ).first()
                    existing = session.query(PitchingStat).filter(
                                PitchingStat.game_id == ps["game_id"],
                                PitchingStat.pitcher_id == ps["pitcher_id"]
                            ).first()
                    if pitcher and not existing:
                        session.add(PitchingStat(**ps))



                