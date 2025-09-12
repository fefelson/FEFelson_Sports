from collections import defaultdict
from datetime import datetime, date
from os import environ, listdir
from pytz import timezone

from .store import Store

from ...utils.file_agent import JSONAgent

BASE_PATH = f"{environ['HOME']}/FEFelson/FEFelson_Sports"
est = timezone('America/New_York')

class MatchupStore(Store):

    def __init__(self):
        super().__init__()
        

    def get_game_data(self):
        gameList = []
        for filePath in [f"{BASE_PATH}/matchups/{fileName}" for fileName in listdir(f"{BASE_PATH}/matchups")]:
            data = JSONAgent.read(filePath)
            data["gameTime"] = datetime.fromisoformat(data["gameTime"])
            gameList.append(data)

        gameData = defaultdict(dict)
        for game in sorted(gameList, key=lambda x: x["gameTime"]):
            if game["gameTime"] > datetime.now().astimezone(est):
                gameData[game['leagueId']][game['title']] = game

            if game["gameTime"].date() == date.today() and game["gameTime"] > datetime.now().astimezone(est):
                gameData["Today"][game['title']] = game 
        return gameData
