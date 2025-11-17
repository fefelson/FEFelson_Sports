from .football_analytics import FootballAnalytics

class NFLAnalytics(FootballAnalytics):

    _gameMinutes = 60

    def __init__(self):
        super().__init__("NFL")


    