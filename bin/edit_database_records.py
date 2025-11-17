from datetime import date, timedelta
from pprint import pprint
from sqlalchemy.sql import text

from fefelson_sports.database.orms import League, Week
from fefelson_sports.database.orms.database import get_db_session, Base
from fefelson_sports.database.seed import seed_data
from fefelson_sports.database.stores.base import ProviderStore
from fefelson_sports.database.stores.core import PlayerStore
from fefelson_sports.models.players import Player




def clear_table(tableName):
    with get_db_session() as session:
        session.execute(text(f"DELETE FROM {tableName} WHERE league_id = 'NBA'"))



def reset_db():

    with get_db_session() as session:
        # Disable foreign key checks (for PostgreSQL, adjust if needed)
        session.execute(text("SET CONSTRAINTS ALL DEFERRED"))
        # Truncate all tables
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE;"))
        # Re-enable foreign key checks
        session.execute(text("SET CONSTRAINTS ALL IMMEDIATE"))


def update_league():

    with get_db_session() as session:
        nfl = session.query(League).filter_by(league_id="NFL").first()
        # nfl.curr_season = 2025
        # nfl.start_date = date(2025,8,19)
        # nfl.end_date = date(2026,2,10)
        nfl.last_update = None

        mlb = session.query(League).filter_by(league_id="MLB").first()
        # mlb.curr_season = 2025
        # mlb.start_date = date(2025,3,15)
        # mlb.end_date = date(2025,11,5)
        # mlb.last_update = None

        ncaaf = session.query(League).filter_by(league_id="NCAAF").first()
        # ncaaf.curr_season = 2025
        # ncaaf.start_date = date(2025,8,19)
        # ncaaf.end_date = date(2026,1,20)
        ncaaf.last_update = None

        nba = session.query(League).filter_by(league_id="NBA").first()
        # nba.curr_season = 2025
        # nba.start_date = date(2025,10,18)
        # nba.end_date = date(2026,6,20)
        nba.last_update = None

        ncaab = session.query(League).filter_by(league_id="NCAAB").first()
        # ncaab.curr_season = 2025
        # ncaab.start_date = date(2025,11,1)
        # ncaab.end_date = date(2026,4,10)
        ncaab.last_update = None



def create_weeks():

    # startInitial = date(2025,9,2)
    # endInitial = date(2025,9,8)
    # week_num = 1

    # with get_db_session() as session:

    #     for week_num in range(1,23):

    #         startDate = startInitial + timedelta(7*(week_num-1))
    #         endDate = endInitial + timedelta(7*(week_num-1))
    #         week = {"league_id": "NFL", "week_num": week_num, "start_date": startDate, "end_date": endDate}
    #         session.add(Week(**week))


    startInitial = date(2025,8,26)
    endInitial = date(2025,9,1)
    week_num = 1

    with get_db_session() as session:

        for week_num in range(1,23):

            startDate = startInitial + timedelta(7*(week_num-1))
            endDate = endInitial + timedelta(7*(week_num-1))
            week = {"league_id": "NCAAF", "week_num": week_num, "start_date": startDate, "end_date": endDate}
            session.add(Week(**week))


def update_weeks():

    with get_db_session() as session:

        firstWeek = session.query(Week).filter_by(league_id="NCAAF", week_num=1).first()
        firstWeek.start_date = date(2025,8,22)
        firstWeek.end_date = date(2025,9,2)
        
        secondWeek = session.query(Week).filter_by(league_id="NCAAF", week_num=2).first()
        secondWeek.start_date = date(2025,9,3)




        



if __name__ == "__main__":
    
    # reset_db()
    # seed_data()
    update_league()
    # clear_table("games")
    # # create_weeks()
    # # update_weeks()
    # set_mlb_b_t()
    
    
