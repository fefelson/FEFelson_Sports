from sqlalchemy.orm import Session

from .database_agent import SQLAlchemyDatabaseAgent

from ..stores.baseball import TeamStatStore, PlayerStatStore, PlayerPlayStore

# for debugging
# from pprint import pprint

class MLBAlchemy(SQLAlchemyDatabaseAgent):

    def __init__(self):
        super().__init__("MLB")

        self.teamsStatStore = TeamStatStore()
        self.playerStatStore = PlayerStatStore()
        self.playerPlayStore = PlayerPlayStore()


    def _insert_league_specific_data(self, boxscore: dict, mapping: dict, session: Session):
        
        for a_h in range(2):
            
            yahooTS = boxscore["yahoo"]["teamStats"][a_h]
            espnTS = boxscore["espn"]["teamStats"][a_h]

            for label in ("game_id", "team_id", "opp_id"):
                yahooTS[label] = mapping[yahooTS[label]]
            for label in ("errors", ):
                yahooTS[label] = espnTS[label]

            self.teamsStatStore.insert(session, yahooTS)


        # Set Lineup

        for subset, subFunc in (("batting", self.playerStatStore.insert_lineup), 
                                ("pitching", self.playerStatStore.insert_bullpen)):
            for yahooL in boxscore["yahoo"]["lineups"][subset]:
                for label in ("game_id", "team_id", "opp_id", "player_id"):
                    yahooL[label] = mapping[yahooL[label]]
                subFunc(session, yahooL)

        # Set Player Stats

        for subset, subFunc in (("batting_stats", self.playerStatStore.insert_batting),
                                ("pitching_stats", self.playerStatStore.insert_pitching)):
            for yahooPS in boxscore["yahoo"]["playerStats"][subset]:
                for label in ("game_id", "team_id", "opp_id", "player_id"):
                    yahooPS[label] = mapping[yahooPS[label]]                
                subFunc(session, yahooPS)
    

        # Set PBP Stats
        
        for ab in boxscore["yahoo"]["misc"]["at_bats"]:
            for label in ("game_id", "team_id", "opp_id", "batter_id", "pitcher_id"):
                ab[label] = mapping[ab[label]]   
            self.playerPlayStore.insert_at_bat(session, ab)

        for pitch in boxscore["espn"]["misc"]["pitches"]:
            for label in ("game_id", "team_id", "opp_id", "batter_id", "pitcher_id"):
                pitch[label] = mapping[pitch[label]]   
            self.playerPlayStore.insert_pitch(session, pitch)


