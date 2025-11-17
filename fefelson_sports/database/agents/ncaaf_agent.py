from sqlalchemy.orm import Session

from .database_agent import SQLAlchemyDatabaseAgent

from ..stores.football import TeamStatStore, PlayerStatStore

# for debugging
from pprint import pprint

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
                try:
                    espnTS = boxscore["espn"]["teamStats"][a_h]
                except IndexError:
                    espnTS = {}
                    espnBox = None
            else:
                espnTS = {}
            
            for label in ("game_id", "team_id", "opp_id"):
                yahooTS[label] = mapping[yahooTS[label]]
            
            if espnTS:
                for label in ("yards", "pass_yards", "rush_yards", "pass_plays", "rush_plays", "drives", "rz_att", "rz_conv", 'int_thrown', 
                                'fum_lost', 'times_sacked', 'sack_yds_lost', 'penalties', 'penalty_yards', 
                                'third_att', 'third_conv', 'fourth_att', 'fourth_conv', "time_of_poss" ):
                    yahooTS[label] = espnTS[label]

                self.teamsStatStore.insert(session, yahooTS)

        # Set Player Stats

        for subset, subFunc in (("passing", self.playerStatStore.insert_passing),
                                ("rushing", self.playerStatStore.insert_rushing), 
                                ("receiving", self.playerStatStore.insert_receiving),
                                ("fumbles", self.playerStatStore.insert_fumbles),
                                ("kicking", self.playerStatStore.insert_kicking),
                                ("punting", self.playerStatStore.insert_punting),
                                ("returns", self.playerStatStore.insert_returns),
                                ("defense", self.playerStatStore.insert_defense)):
            
            for yahooPS in boxscore["yahoo"]["playerStats"][subset]:
                try:
                    for label in ("game_id", "team_id", "opp_id", "player_id"):
                        yahooPS[label] = mapping[yahooPS[label]]
            
                    if subset == "defense":
                        yahooPS["qb_hits"] = 0
                        if boxscore["espn"]["playerStats"]:
                            for espnPS in boxscore["espn"]["playerStats"][subset]:
                                try:
                                    if mapping[espnPS["player_id"]] == yahooPS["player_id"]:
                                        yahooPS["qb_hits"] = espnPS["qb_hits"]
                                        break
                                except KeyError:
                                    pass
                                
                    
                    subFunc(session, yahooPS)
                except KeyError as e:
                    print(e)
    

        # Set PBP Stats
        # for subset, subFunc in (("kick_plays", self.playerPlayStore.insert_kick_plays),
        #                         ("pass_plays", self.playerPlayStore.insert_pass_plays), 
        #                         ("rush_plays", self.playerPlayStore.insert_rush_plays)):
        #     for yahooPS in boxscore["yahoo"]["misc"][subset]:
        #         for label in ("game_id", "team_id", "opp_id"):
        #             yahooPS[label] = mapping[yahooPS[label]]

        #         for label in ("rusher", "quarterback", "target", "kicker"):
        #             if yahooPS.get(label):
        #                 yahooPS[label] = mapping[yahooPS[label]]
                
        #         subFunc(session, yahooPS)
