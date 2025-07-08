from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import os
import sys

from sports_scraper.scraper.capabilities.fileable import PickleAgent, JSONAgent
from sports_db.database.models.database import engine, Base
from sports_db.database.models import Sport, League, Team, Player, AtBatType, PitchType, PitchResultType, ContactType, SwingResult

from sports_scraper.scraper.providers.yahoo.normalizers.yahoo_mlb_normalizer import YahooMLBNormalizer as normalAgent
 
def seed_data():
    # Create tables if they don???t exist
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        try:
            # Seed Sports
            sports_data = [
                {"sport_id": "sport_basketball", "name": "Basketball"},
                {"sport_id": "sport_baseball", "name": "Baseball"},
                {"sport_id": "sport_football", "name": "Football"},
                {"sport_id": "sport_hockey", "name": "Hockey"}
            ]
            for data in sports_data:
                if not session.query(Sport).filter_by(sport_id=data["sport_id"]).first():
                    session.add(Sport(**data))

            # Seed Leagues
            leagues_data = [
                {"league_id": "NBA", "sport_id": "sport_basketball", "name": "National Basketball Association"},
                {"league_id": "NCAAB", "sport_id": "sport_basketball", "name": "College Basketball"},
                {"league_id": "MLB", "sport_id": "sport_baseball", "name": "Major League Baseball"},
                {"league_id": "NFL", "sport_id": "sport_football", "name": "National Football League"},
                {"league_id": "NCAAF", "sport_id": "sport_football", "name": "College Football"}
            ]
            for data in leagues_data:
                if not session.query(League).filter_by(league_id=data["league_id"]).first():
                    session.add(League(**data))
                    


             # Seed MLB Teams
            mlb_teams = PickleAgent.read(os.path.join(os.environ["HOME"], "FEFelson/leagues/mlb/mlb_teams.pkl")) 
            for data in mlb_teams:
                if not session.query(Team).filter_by(team_id=data["team_id"]).first():
                    session.add(Team(**data))


            # Seed MLB Players
            mlb_players = PickleAgent.read(os.path.join(os.environ["HOME"], "FEFelson/leagues/mlb/mlb_players.pkl")) 
            for player in [normalAgent("MLB").normalize_player(player) for player in mlb_players]:

                if not session.query(Player).filter_by(player_id=player["player_id"]).first():
                    session.add(Player(**player))



            # Seed At Bat Results
            at_bat_types = [
                {"at_bat_type_id": 0, "at_bat_type_name": "strike out", "is_pa": True, "is_ab": True, "is_ob": False, "is_hit": False, "num_bases": 0},
                {"at_bat_type_id": 1, "at_bat_type_name": "foul out", "is_pa": True, "is_ab": True, "is_ob": False, "is_hit": False, "num_bases": 0},
                {"at_bat_type_id": 2, "at_bat_type_name": "fly out", "is_pa": True, "is_ab": True, "is_ob": False, "is_hit": False, "num_bases": 0},
                {"at_bat_type_id": 3, "at_bat_type_name": "ground out", "is_pa": True, "is_ab": True, "is_ob": False, "is_hit": False, "num_bases": 0},
                {"at_bat_type_id": 4, "at_bat_type_name": "pop out", "is_pa": True, "is_ab": True, "is_ob": False, "is_hit": False, "num_bases": 0},
                {"at_bat_type_id": 5, "at_bat_type_name": "line out", "is_pa": True, "is_ab": True, "is_ob": False, "is_hit": False, "num_bases": 0},
                {"at_bat_type_id": 6, "at_bat_type_name": "hit by pitch", "is_pa": True, "is_ab": False, "is_ob": True, "is_hit": False, "num_bases": 0},
                {"at_bat_type_id": 7, "at_bat_type_name": "walk", "is_pa": True, "is_ab": False, "is_ob": True, "is_hit": False, "num_bases": 0},
                {"at_bat_type_id": 8, "at_bat_type_name": "single", "is_pa": True, "is_ab": True, "is_ob": True, "is_hit": True, "num_bases": 1},
                {"at_bat_type_id": 9, "at_bat_type_name": "double", "is_pa": True, "is_ab": True, "is_ob": True, "is_hit": True, "num_bases": 2},
                {"at_bat_type_id": 10, "at_bat_type_name": "triple", "is_pa": True, "is_ab": True, "is_ob": True, "is_hit": True, "num_bases": 3},
                {"at_bat_type_id": 11, "at_bat_type_name": "home run", "is_pa": True, "is_ab": True, "is_ob": True, "is_hit": True, "num_bases": 4}
            ]
            for data in at_bat_types:
                if not session.query(AtBatType).filter_by(at_bat_type_id=data["at_bat_type_id"]).first():
                    session.add(AtBatType(**data))
            
            # Seed Contact types
            contact_types = [
                {"contact_type_id": 0, "at_bat_type_id":2},
                {"contact_type_id": 1, "at_bat_type_id": 3},
                {"contact_type_id": 2, "at_bat_type_id": 4},
                {"contact_type_id": 3, "at_bat_type_id": 5},
                {"contact_type_id": 4, "at_bat_type_id": 8},
                {"contact_type_id": 5, "at_bat_type_id": 9},
                {"contact_type_id": 6, "at_bat_type_id": 10},
                {"contact_type_id": 7, "at_bat_type_id": 11}
            ]
            for data in contact_types:
                if not session.query(ContactType).filter_by(contact_type_id=data["contact_type_id"]).first():
                    session.add(ContactType(**data))

            # Seed Pitch Result Types
            pitch_result_types = [
                {"pitch_result_name": "ball", "pitch_result_id":0, "is_strike": False, "is_swing": False, "is_contact": False},
                {"pitch_result_name": "bunted foul", "pitch_result_id":1, "is_strike": True, "is_swing": False, "is_contact": True},
                {"pitch_result_name": "foul ball", "pitch_result_id":2, "is_strike": True, "is_swing": True, "is_contact": True},
                {"pitch_result_name": "play", "pitch_result_id":3, "is_strike": True, "is_swing": True, "is_contact": True},
                {"pitch_result_name": "strike looking", "pitch_result_id":4, "is_strike": True, "is_swing": False, "is_contact": False},
                {"pitch_result_name": "strike swinging", "pitch_result_id":5, "is_strike": True, "is_swing": True, "is_contact": False}
            ]
            for data in pitch_result_types:
                if not session.query(PitchResultType).filter_by(pitch_result_name=data["pitch_result_name"]).first():
                    session.add(PitchResultType(**data))

            # Seed Swing results
            swing_results = [
                {"swing_result_id": 0, "pitch_result_name": "strike swinging"},
                {"swing_result_id": 1, "pitch_result_name": "foul ball"},
                {"swing_result_id": 2, "pitch_result_name": "play"}
            ]
            for data in swing_results:
                if not session.query(SwingResult).filter_by(swing_result_id=data["swing_result_id"]).first():
                    session.add(SwingResult(**data))


            # Seed Pitch Types
            pitch_types = [  
                {"pitch_type_name": "changeup", "pitch_type_id":0},
                {"pitch_type_name": "curve", "pitch_type_id":1},
                {"pitch_type_name": "cutter", "pitch_type_id":2},
                {"pitch_type_name": "two-seam fb", "pitch_type_id":3},
                {"pitch_type_name": "fastball", "pitch_type_id":4},
                {"pitch_type_name": "forkball", "pitch_type_id":5},
                {"pitch_type_name": "four-seam fb", "pitch_type_id":6},
                {"pitch_type_name": "sweeper", "pitch_type_id":7},
                {"pitch_type_name": "splitter", "pitch_type_id":8},
                {"pitch_type_name": "screwball", "pitch_type_id":9},
                {"pitch_type_name": "sinker", "pitch_type_id":10},
                {"pitch_type_name": "slider", "pitch_type_id":11},
                {"pitch_type_name": "slow curve", "pitch_type_id":12},
                {"pitch_type_name": "slurve", "pitch_type_id":13},
                {"pitch_type_name": "knuckle curve", "pitch_type_id":14},
                {"pitch_type_name": "knuckleball", "pitch_type_id":15},
                {"pitch_type_name": "eephus pitch", "pitch_type_id":16},
                
            ]
            for data in pitch_types:
                if not session.query(PitchType).filter_by(pitch_type_name=data["pitch_type_name"]).first():
                    session.add(PitchType(**data))


           
            session.commit()
            print("Data seeded successfully!")
        except IntegrityError as e:
            session.rollback()
            print(f"Integrity error (likely duplicates skipped): {e}")
        except Exception as e:
            session.rollback()
            print(f"Seeding failed: {e}")
            raise

if __name__ == "__main__":
    seed_data()
