from contextlib import contextmanager
from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, sessionmaker


db_url = dotenv_values()['DATABASE_URL']

# Define Base
Base = declarative_base()

engine = create_engine(
    db_url,
    pool_size=20,  # Increase based on workload
    max_overflow=40,
    pool_timeout=60,
    pool_pre_ping=True,  # Avoid stale connections
    echo=False
)
SessionFactory = sessionmaker(bind=engine)


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