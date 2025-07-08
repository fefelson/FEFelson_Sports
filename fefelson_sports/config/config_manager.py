from typing import Dict, Any
from threading import Lock
import os

from ..capabilities.fileable import Fileable, get_file_agent


##################################################################
##################################################################



class LeagueConfig(Fileable):
    _config_lock = Lock()  # Prevent race conditions in multi-threaded environments
    _fileType = "json"
    _fileAgent = get_file_agent(_fileType)


    def __init__(self, leagueId: str):
        
        self.leagueId = leagueId
        self.set_file_path()
        self.set_file_agent(self._fileAgent)
        self.config: Dict[str, Any] = self._load_config()


    def _load_config(self) -> Dict[str, Any]:
        """Loads the full config file and extracts the league-specific settings."""
        fullConfig = self.read_file()
        return fullConfig.get(self.leagueId, {})  # Get only this league???s config
        

    def _write_config(self) -> None:
        """Writes only the updated league's config without affecting others."""
        with self._config_lock:
            # Read the full existing config
            fullConfig = self.read_file() or {}  # Default to empty dict if file is empty
            # Update only this league???s portion
            fullConfig[self.leagueId] = self.config
            # Write the entire updated config back to the file
            self.write_file(fullConfig)



    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a value from the league's config."""
        return self.config.get(key, default)
    

    def set(self, key: str, value: Any) -> None:
        """Updates a single field in the league's config and writes it back to the file."""
        self.config[key] = value
        self._write_config()


    
    def set_file_path(self):
         # Get the directory of this module (leagues.py)
         module_dir = os.path.dirname(os.path.abspath(__file__))
         # Go up two levels to ~/fefelson_mvp, then into data
         self.filePath = os.environ["HOME"]+"/FEFelson/FEFelson_Sports/data/league_config.json"


      


