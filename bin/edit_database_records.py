
from ..src.database.models.database import get_db_session
from sqlalchemy.sql import text


def reset_db():

    with get_db_session() as session:
        # Disable foreign key checks (for PostgreSQL, adjust if needed)

        # Truncate all tables
        # for table in reversed(Base.metadata.sorted_tables):
        #     session.execute(text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE;"))
        for table_name in ("at_bat_types", ):
            session.execute(text(f"TRUNCATE TABLE {table_name};"))
    

        # Re-enable foreign key checks


if __name__ == "__main__":
    reset_db()
