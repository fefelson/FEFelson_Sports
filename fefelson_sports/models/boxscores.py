from datetime import datetime
from typing import Any, Dict
import os

from ..capabilities import Fileable, Normalizable, Processable, Downloadable, Databaseable
from ..capabilities.databaseable import SQLAlchemyDatabaseAgent
from ..capabilities.fileable import get_file_agent
from ..providers import get_download_agent, get_normal_agent
from ..utils.logging_manager import get_logger


######################################################################
######################################################################


basePath = os.path.join(os.environ["HOME"], "FEFelson/FEFelson_Sports/leagues")


######################################################################
######################################################################



class Boxscore(Databaseable, Downloadable, Fileable, Normalizable, Processable):

    _fileType = "pickle"
    _fileAgent = get_file_agent(_fileType)


    def __init__(self, leagueId: str, dbAgent: "DatabaseAgent"):
        super().__init__()

        self.leagueId = leagueId
        self.dbAgent = dbAgent
        self.set_file_agent(self._fileAgent)


        self.logger = get_logger()


    def download(self, game: dict) -> Dict[str, Any]:
        downloadAgent = get_download_agent(self.leagueId, game["provider"])
        return downloadAgent.fetch_boxscore(game)


    def load_from_db(self):
        """Loads data from the database into dataclass object using and returns it."""
        print(f"Databaseable.load_from_db called ")
        raise NotImplementedError


    def normalize(self, webData: dict) -> Dict[str, Any]:
        if webData is None:
            return None
        normalAgent = get_normal_agent(self.leagueId, webData["provider"])
        return normalAgent.normalize_boxscore(webData)


    def process(self, game: dict) :
        self.logger.debug("processing Boxscore")

        # from pprint import pprint 
        # pprint(game)
        # raise

        self.set_file_path(game["yahoo"])

        if self.file_exists():

            webData = self.read_file()

            yahooBox = webData["yahoo"]
            espnBox = webData["espn"]
        else:
            if game["yahoo"]["url"]:
                yahooBox = self.download(game["yahoo"])
                espnBox = None
                if game.get("espn"):
                    espnBox = self.download(game["espn"])
                
                self.write_file({"espn": espnBox, "yahoo": yahooBox})
                        
        return {"yahooBox": self.normalize(yahooBox), "espnBox": self.normalize(espnBox)}


    def save_to_db(self, boxscore: dict):
        """Saves self.data to the database."""
        try:
            self.dbAgent.insert_boxscore(boxscore)
        except Exception as e:
            # Catch unexpected errors
            self.logger.error(f"Failed to save boxscore to db: Unexpected error - {type(e).__name__}: {str(e)}")
            raise #: re-raise for debugging
        else:
            # Runs if no exception occurs
            self.logger.info("Boxscore saved to db successfully")
        # Optional: Add a finally block if you need cleanup



    def set_file_path(self, game: dict):
        if game.get("week"):
            gamePath = f"/{self.leagueId.lower()}/boxscores/{game['season']}/{game['week']}/{game['gameId'].split('.')[-1]}.{self._fileAgent.get_ext()}"
        else:
            month, day = str(datetime.fromisoformat(game["gameTime"]).date()).split("-")[1:]
            gamePath = f"/{self.leagueId.lower()}/boxscores/{game['season']}/{month}/{day}/{game['gameId'].split('.')[-1]}.{self._fileAgent.get_ext()}"
        self.filePath = basePath+gamePath

    
