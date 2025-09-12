from sqlalchemy.orm import Session

from .database_agent import SQLAlchemyDatabaseAgent

from ..stores.basketball import TeamStatStore, PlayerShotStore, PlayerStatStore

# for debugging
# from pprint import pprint

class NCAABAlchemy(SQLAlchemyDatabaseAgent):

    def __init__(self):
        super().__init__("NCAAB")

        self.teamsStatStore = TeamStatStore()
        self.playerStatStore = PlayerStatStore()
        self.playerShotStore = PlayerShotStore()


    def _insert_league_specific_data(self, boxscore: dict, mapping: dict, session: Session):

        # pprint(boxscore)
        # raise
        
        for a_h in range(2):
            
            yahooTS = boxscore["yahoo"]["teamStats"][a_h]
            espnTS = boxscore["espn"]["teamStats"][a_h]

            for label in ("game_id", "team_id", "opp_id"):
                yahooTS[label] = mapping[yahooTS[label]]
            for label in ("fb_pts", "pts_in_pt"):
                yahooTS[label] = espnTS[label]

            self.teamsStatStore.insert(session, yahooTS)

        for yahooPS in boxscore["yahoo"]["playerStats"]:
            for label in ("game_id", "team_id", "opp_id", "player_id"):
                yahooPS[label] = mapping[yahooPS[label]]        
            self.playerStatStore.insert(session, yahooPS)


        if boxscore["yahoo"].get("misc"):
            for yahooShot in boxscore["yahoo"]["misc"]:
                try:
                    for label in ("game_id", "team_id", "opp_id", "player_id"):
                        yahooShot[label] = mapping[yahooShot[label]]
                    if yahooShot["assist_id"]:
                        yahooShot["assist_id"] = mapping[yahooShot["assist_id"]]
                    self.playerShotStore.insert(session, yahooShot)
                except KeyError:
                    pass

