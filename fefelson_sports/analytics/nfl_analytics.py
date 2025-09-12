from .football_analytics import FootballAnalytics, get_db_session

class NFLAnalytics(FootballAnalytics):

    _gameMinutes = 60

    def __init__(self):
        super().__init__("NFL")


    