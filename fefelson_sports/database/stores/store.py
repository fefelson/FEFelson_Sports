from datetime import date
from sqlalchemy.orm import Session

from ..orms.database import get_db_session

from ...utils.date_utils import calculate_start_date

class Store:

    def __init__(self):
        pass 


    def _and_gameDate(self, timeFrame):

        startDate = calculate_start_date(timeFrame)
        if startDate:
            return f" AND (DATE(game_date) >= '{startDate}'::DATE AND DATE(game_date) < '{date.today()}'::DATE) "
        if timeFrame == 'Season':
            return f" AND g.season = l.curr_season "
        
        return ""



    def _execute_with_session(self, session_func: Session=None):
        """Execute a function with an appropriate session, either provided or new."""
        if session_func is None:
            with get_db_session() as session:
                return session
        return session_func  # Use the provided session
