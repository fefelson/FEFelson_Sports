from .basketball_analytics import BasketballAnalytics

class NCAABAnalytics(BasketballAnalytics):

    _gameMinutes = 40

    def __init__(self):
        super().__init__("NCAAB")




