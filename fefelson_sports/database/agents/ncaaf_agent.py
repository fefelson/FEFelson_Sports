from sqlalchemy.orm import Session

from .database_agent import SQLAlchemyDatabaseAgent

from ..stores.football import TeamStatStore, PlayerStatStore

# for debugging
# from pprint import pprint

class NCAAFAlchemy(SQLAlchemyDatabaseAgent):

    def __init__(self):
        super().__init__("NCAAF")

        self.teamsStatStore= TeamStatStore()
        self.playerStatStore = PlayerStatStore()

    def _insert_league_specific_data(self, boxscore: dict, mapping: dict, session: Session):

        # pprint(boxscore)
        # raise
        
        espnBox = boxscore.get("espn")

        for a_h in range(2):
            
            yahooTS = boxscore["yahoo"]["teamStats"][a_h]
            if espnBox:
                espnTS = boxscore["espn"]["teamStats"][a_h]
            else:
                espnTS = {}
            
            for label in ("game_id", "team_id", "opp_id"):
                yahooTS[label] = mapping[yahooTS[label]]

            self.teamsStatStore.insert(session, yahooTS)

        # Set Player Stats

        for subset, subFunc in (("passing", self.playerStatStore.insert_passing),
                                ("rushing", self.playerStatStore.insert_rushing), 
                                ("receiving", self.playerStatStore.insert_receiving),
                                ("punting", self.playerStatStore.insert_punting),
                                ("returns", self.playerStatStore.insert_returns),
                                ("defense", self.playerStatStore.insert_defense)):
            for yahooPS in boxscore["yahoo"]["playerStats"][subset]:
                for label in ("game_id", "team_id", "opp_id", "player_id"):
                    yahooPS[label] = mapping.get(yahooPS[label], -1)
        
                if subset == "defense":
                    yahooPS["qb_hits"] = 0
                    yahooPS["tackles"] = 0
                    try:
                        for espnPS in boxscore["espn"]["playerStats"][subset]:
                        
                                if mapping[espnPS["player_id"]] == yahooPS["player_id"]:
                                    yahooPS["qb_hits"] = espnPS["qb_hits"]
                                    yahooPS["tackles"] = espnPS["tackles"]
                                    break
                    except KeyError:
                        pass
                if yahooPS["player_id"] != -1:
                    subFunc(session, yahooPS)
        
        if espnBox:
            for espnPS in boxscore["espn"]["playerStats"]["fumbles"]:
                try:
                    if int(espnPS["fum_lost"]):
                        for label in ("game_id", "team_id", "opp_id", "player_id"):
                            espnPS[label] = mapping[espnPS[label]]
                        self.playerStatStore.insert_fumbles(session, espnPS)
                except KeyError:
                    pass


