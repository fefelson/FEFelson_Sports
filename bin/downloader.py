from datetime import datetime, timedelta
from time import sleep
import os

from fefelson_sports.capabilities.fileable import PickleAgent
from fefelson_sports.capabilities.databaseable import SQLAlchemyDatabaseAgent, MLBAlchemy
from fefelson_sports.sports.leagues import MLB
from fefelson_sports.providers import get_download_agent, get_normal_agent
from fefelson_sports.models.players import Player
from fefelson_sports.models.matchups import Matchup
from fefelson_sports.models.scoreboards import Scoreboard
import datetime


BASE_PATH = os.environ["HOME"]+"/FEFelson/FEFelson_Sports/leagues/mlb/boxscores"
providers = ("yahoo", "espn")

def main():

    matchup = Matchup("MLB")
    scoreboard = Scoreboard("MLB")
    gameDate = str(datetime.date.today())
    for game in scoreboard.process(gameDate).values():          
        if game["yahoo"]["statusType"] == "pregame":
            m = matchup.process(game)
            from pprint import pprint 
            pprint(m)


    # yahooBox = PickleAgent.read(BASE_PATH+"/2022/04/07/420407103/yahoo.pkl")
    # espnBox = PickleAgent.read(BASE_PATH+"/2022/04/07/420407103/espn.pkl")

    # from pprint import pprint
    # espn_agent = get_normal_agent("MLB", "espn")
    # yahoo_agent = get_normal_agent("MLB", "yahoo")

    # pprint(yahoo_agent.normalize_boxscore(yahooBox).keys())
    # print("\n\n")
    # pprint(espn_agent.normalize_boxscore(espnBox).keys())

    




if __name__ == "__main__":

    main()
