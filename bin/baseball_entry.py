import os
import re

from fefelson_sports.models.boxscores import Boxscore
from fefelson_sports.models.players import Player
from fefelson_sports.capabilities.fileable import PickleAgent
from fefelson_sports.capabilities.databaseable import MLBAlchemy
from fefelson_sports.providers.espn.normalizers.espn_mlb_normalizer import ESPNMLBNormalizer
from fefelson_sports.providers.yahoo.normalizers.yahoo_mlb_normalizer import YahooMLBNormalizer

from fefelson_sports.database.models.database import get_db_session


BASE_PATH = os.environ["HOME"] + "/FEFelson/FEFelson_Sports/leagues/mlb/boxscores/"
PLAYER_PATH = os.environ["HOME"]+f"/FEFelson/FEFelson_Sports/leagues/mlb/players"

BS = Boxscore("MLB", MLBAlchemy)
PL = Player("MLB", MLBAlchemy)


def insert_players():

    for playerId in [fileName.split(".")[0] for fileName in os.listdir(PLAYER_PATH)]:
        player = PL.process(playerId)
        PL.save_to_db(player)


def main():

    insert_players()

    for gamePath, _, fileNames in os.walk(BASE_PATH):
    
        if re.match(r".*/(\d{4})/(\d{2})/(\d{2})$", gamePath):            
            for gameId in [gameId for gameId in fileNames if "M" not in gameId]:
                filePath = gamePath+f"/{gameId}"
                print(filePath)
                
                boxscore = PickleAgent.read(filePath)
                boxscore = {"yahooBox": BS.normalize(boxscore["yahoo"]), "espnBox": BS.normalize(boxscore["espn"])}
                BS.save_to_db(boxscore)
                    
if __name__ == "__main__":
    main()
