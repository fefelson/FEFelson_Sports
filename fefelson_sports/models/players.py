from typing import Any, Dict
import os 

from ..capabilities import Fileable, Normalizable, Processable, Downloadable, Databaseable
from ..capabilities.databaseable import SQLAlchemyDatabaseAgent
from ..capabilities.fileable import get_file_agent
from ..providers import get_download_agent, get_normal_agent
from ..utils.logging_manager import get_logger


######################################################################
######################################################################


BASE_PATH = os.path.join(os.environ["HOME"], "FEFelson/FEFelson_Sports/leagues")


######################################################################
######################################################################



class Player(Databaseable, Downloadable, Fileable, Normalizable, Processable):

    _fileType = "pickle"
    _fileAgent = get_file_agent(_fileType)


    def __init__(self, leagueId: str, dbAgent: "DatabaseAgent"):
        super().__init__()

        self.leagueId = leagueId
        self.dbAgent = dbAgent

        self.set_file_agent(self._fileAgent)

        self.logger = get_logger()


    def download(self, playerId: str) -> Dict[str, Any]:
        downloadAgent = get_download_agent(self.leagueId)
        return downloadAgent.fetch_player(self.leagueId, playerId)


    def load_from_db(self):
        """Loads data from the database into dataclass object using and returns it."""
        print(f"Databaseable.load_from_db called ")
        raise NotImplementedError


    def normalize(self, webData: dict) -> Dict[str, Any]:
        if webData is None:
            return None
        normalAgent = get_normal_agent(self.leagueId, webData["provider"])
        return normalAgent.normalize_player(webData)


    def process(self, playerId: str) :
        self.logger.debug("processing Player")
        
        self.set_file_path(playerId)
        if self.file_exists():
            webData = self.read_file()
        else:
            try:
                webData = self.download(playerId)
                self.write_file(webData)
            except KeyError:
                webData = None
        player = self.normalize(webData)
        return player
    

    def save_to_db(self, player: "Player"):
        """Saves self.data to the database."""
        try:
            self.dbAgent.insert_player(player)
        except Exception as e:
            # Catch unexpected errors
            self.logger.error(f"Failed to save player to db: Unexpected error - {type(e).__name__}: {str(e)}")
            # raise  # Optional: re-raise for debugging
        


    def set_file_path(self, playerId: str):
        ext = self.fileAgent.get_ext()
        playerId = playerId.split(".")[-1]
        playerPath = f"/{self.leagueId.lower()}/players/{playerId}.{ext}"
        self.filePath = BASE_PATH+playerPath

    
