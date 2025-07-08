from .basketball_team_stats_calculator import BasketballTeamStatsCalculator



def get_stats_calculator(leagueId):
    calculator = None
    if leagueId == "NBA":
        calculator = BasketballTeamStatsCalculator(leagueId)
    elif leagueId == "NCAAB":
        calculator = BasketballTeamStatsCalculator(leagueId)
    return calculator
