from contextlib import contextmanager
from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, sessionmaker
import os

envVals = dotenv_values()
#print(envVals)

db_url = envVals['DATABASE_URL']
#os.environ["DATABASE_URL"] = envVals['DATABASE_URL']



# Define Base
Base = declarative_base()
# Create engine with the URL from alembic.ini
engine = create_engine(db_url, echo=False)  # echo=True for debugging
# Create a session factory
SessionFactory = sessionmaker(bind=engine)
# Optional: Function to initialize the database (for manual table creation)
def init_db():
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db_session():
    session = SessionFactory()
    try:
        yield session
        session.commit()  # Commits if no exceptions occur
    except IntegrityError as e:
        session.rollback()
        raise  # Re-raises the IntegrityError
    except Exception as e:
        session.rollback()
        raise  # Re-raises any other exception
    finally:
        session.close()  # Always closes the session