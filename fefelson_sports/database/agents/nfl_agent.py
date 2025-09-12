from sqlalchemy.orm import Session

from .database_agent import SQLAlchemyDatabaseAgent

from ..stores.football import TeamStatStore, PlayerStatStore, PlayerPlayStore

# for debugging
# from pprint import pprint

class NFLAlchemy(SQLAlchemyDatabaseAgent):
 
    def __init__(self):
        super().__init__("NFL")

        self.teamsStatStore= TeamStatStore()
        self.playerStatStore = PlayerStatStore()
        self.playerPlayStore = PlayerPlayStore()


    def _insert_league_specific_data(self, boxscore: dict, mapping: dict, session: Session):

        # pprint(boxscore)

        for a_h in range(2):

            # Set Team Stats 
            
            yahooTS = boxscore["yahoo"]["teamStats"][a_h]
            espnTS = boxscore["espn"]["teamStats"][a_h]
            
            for label in ("game_id", "team_id", "opp_id"):
                yahooTS[label] = mapping[yahooTS[label]]
            for label in ("drives", "rz_att", "rz_conv"):
                yahooTS[label] = espnTS[label]

            self.teamsStatStore.insert(session, yahooTS)

        # Set Player Stats

        for subset, subFunc in (("passing", self.playerStatStore.insert_passing),
                                ("rushing", self.playerStatStore.insert_rushing), 
                                ("receiving", self.playerStatStore.insert_receiving),
                                ("fumbles", self.playerStatStore.insert_fumbles),
                                ("punting", self.playerStatStore.insert_punting),
                                ("returns", self.playerStatStore.insert_returns),
                                ("defense", self.playerStatStore.insert_defense)):
            for yahooPS in boxscore["yahoo"]["playerStats"][subset]:
                for label in ("game_id", "team_id", "opp_id", "player_id"):
                    yahooPS[label] = mapping[yahooPS[label]]
        
                if subset == "defense":
                    for espnPS in boxscore["espn"]["playerStats"][subset]:
                        try:
                            if mapping[espnPS["player_id"]] == yahooPS["player_id"]:
                                yahooPS["qb_hits"] = espnPS["qb_hits"]
                                break
                        except KeyError:
                            pass
                        yahooPS["qb_hits"] = 0
                
                subFunc(session, yahooPS)
    

        # Set PBP Stats
        for subset, subFunc in (("kick_plays", self.playerPlayStore.insert_kick_plays),
                                ("pass_plays", self.playerPlayStore.insert_pass_plays), 
                                ("rush_plays", self.playerPlayStore.insert_rush_plays)):
            for yahooPS in boxscore["yahoo"]["misc"][subset]:
                for label in ("game_id", "team_id", "opp_id"):
                    yahooPS[label] = mapping[yahooPS[label]]

                for label in ("rusher", "quarterback", "target", "kicker"):
                    if yahooPS.get(label):
                        yahooPS[label] = mapping[yahooPS[label]]
                
                subFunc(session, yahooPS)
