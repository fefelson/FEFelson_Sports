



class BasketballTeamStatsCalculator:

    def __init__(self, league_id):
        self.minutes = 48 if league_id == "NBA" else 40

    def calculate_gaming_stats(self, gamingData):
        if gamingData.empty:
            return {
                'win_pct': "--", 'cover_pct': "--", 'over_pct': "--", 'under_pct': "--",
                'money_roi': "--", 'cover_roi': "--", 'over_roi': "--", 'under_roi': "--",
                "money_line": "--",
                "pts_spread": "--", "result": "--", "ats": "--", 
                "over_under": "--", "total": "--", "att": "--"
            }
        
        gamingData = gamingData.dropna()
        stats = {
            "att": gamingData["att"].sum() / len(gamingData),
            "total": gamingData["total"].sum() / len(gamingData),
            "over_under": gamingData["over_under"].sum() / len(gamingData),
            "ats": gamingData["ats"].sum() / len(gamingData),
            "result": gamingData["result"].sum()/ len(gamingData),
            "pts_spread": gamingData["pts_spread"].sum()/ len(gamingData),
            "money_line": gamingData["money_line"].sum() / len(gamingData),
            'win_pct': gamingData["is_money"].eq(1).sum() * 100 / len(gamingData),
            'cover_pct': gamingData["is_cover"].eq(1).sum() * 100 / len(gamingData),
            'over_pct': gamingData["is_over"].eq(1).sum() * 100 / len(gamingData),
            'under_pct': gamingData["is_under"].eq(1).sum() * 100 / len(gamingData),
            'money_roi': ((gamingData["money_roi"].sum() - (len(gamingData) * 100)) / (len(gamingData) * 100)) * 100,
            'cover_roi': ((gamingData["spread_roi"].sum() - (len(gamingData) * 100)) / (len(gamingData) * 100)) * 100,
            'over_roi': ((gamingData["over_roi"].sum() - (len(gamingData) * 100)) / (len(gamingData) * 100)) * 100,
            'under_roi': ((gamingData["under_roi"].sum() - (len(gamingData) * 100)) / (len(gamingData) * 100)) * 100,
        }
        return stats

    def calculate_team_stats(self, statsData):
        if statsData.empty:
            return {key: "--" for key in ['team_pts', 'opp_pts', 'team_fga', 'team_fgpct', 'opp_fga', 'opp_fgpct', 
                                      'team_fta', 'team_ftpct', 'opp_fta', 'opp_ftpct', 'team_tpa', 'team_tppct', 
                                      'opp_tpa', 'opp_tppct', 'team_turn', 'opp_turn', 'oreb_pct', 'dreb_pct', 
                                      'team_ast', 'opp_ast', 'off_eff', 'def_eff', 'net_rating', 'pace']}

        defaultMinutes = self.minutes
        gameMinutes = statsData["minutes"].sum()

        teamPts = (statsData["team_pts"].sum() * defaultMinutes) / gameMinutes if gameMinutes > 0 else 0
        oppPts = (statsData["opp_pts"].sum() * defaultMinutes) / gameMinutes if gameMinutes > 0 else 0
        
        teamFGA = (statsData["team_fga"].sum() * defaultMinutes) / gameMinutes if gameMinutes > 0 else 0
        teamFGM = (statsData["team_fgm"].sum() * defaultMinutes) / gameMinutes if gameMinutes > 0 else 0
        teamFGPCT = teamFGM / teamFGA if teamFGA > 0 else 0
        
        oppFGA = (statsData["opp_fga"].sum() * defaultMinutes) / gameMinutes if gameMinutes > 0 else 0
        oppFGM = (statsData["opp_fgm"].sum() * defaultMinutes) / gameMinutes if gameMinutes > 0 else 0
        oppFGPCT = oppFGM / oppFGA if oppFGA > 0 else 0

        teamFTA = (statsData["team_fta"].sum()*defaultMinutes) / gameMinutes if gameMinutes > 0 else 0
        teamFTM = (statsData["team_ftm"].sum()*defaultMinutes) / gameMinutes if gameMinutes > 0 else 0
        teamFTPct = teamFTM/teamFTA

        oppFTA = (statsData["opp_fta"].sum()*defaultMinutes) / gameMinutes if gameMinutes > 0 else 0
        oppFTM = (statsData["opp_ftm"].sum()*defaultMinutes) / gameMinutes if gameMinutes > 0 else 0
        oppFTPct = oppFTM/oppFTA

        teamTPA = (statsData["team_tpa"].sum()*defaultMinutes) / gameMinutes if gameMinutes > 0 else 0
        teamTPM = (statsData["team_tpm"].sum()*defaultMinutes) / gameMinutes if gameMinutes > 0 else 0
        teamTPPct = teamTPM/teamTPA

        oppTPA = (statsData["opp_tpa"].sum()*defaultMinutes) / gameMinutes if gameMinutes > 0 else 0
        oppTPM = (statsData["opp_tpm"].sum()*defaultMinutes) / gameMinutes if gameMinutes > 0 else 0
        oppTPPct = oppTPM/oppTPA


        teamTurn = statsData["team_trn"].sum() / statsData["team_poss"].sum()   
        oppTurn = statsData["opp_trn"].sum() / statsData["opp_poss"].sum() 

        teamOReb = statsData["team_oreb"].sum()  
        teamDReb = statsData["team_dreb"].sum()

        oppOReb = statsData["opp_oreb"].sum()  
        oppDReb = statsData["opp_dreb"].sum()

        orebPct = teamOReb / (teamOReb+oppDReb)
        drebPct = teamDReb / (teamDReb+oppOReb)

        teamAst = statsData["team_ast"].sum() / statsData["team_fgm"].sum()
        oppAst = statsData["opp_ast"].sum() / statsData["opp_fgm"].sum() 


        offEff = (statsData["team_pts"].sum()*100) / statsData["team_poss"].sum()
        defEff = (statsData["opp_pts"].sum()*100) / statsData["opp_poss"].sum()
        netRating = offEff - defEff 
        poss = (statsData["team_poss"].sum()*defaultMinutes) / gameMinutes if gameMinutes > 0 else 0

        
        return {
            'gp': len(statsData),
            'team_pts': teamPts, 'opp_pts': oppPts,
            'team_ast': teamAst, 'opp_ast': oppAst,
            'team_turn': teamTurn, 'opp_turn': oppTurn,
            'oreb_pct': orebPct, 'dreb_pct': drebPct,
            'net_rating': netRating, 'off_eff': offEff, 'def_eff': defEff,
            'team_fga': teamFGA, 'team_fgpct': teamFGPCT, 'opp_fga': oppFGA, 'opp_fgpct': oppFGPCT,
            'team_fta': teamFTA, 'team_ftpct': teamFTPct, 'opp_fta': oppFTA, 'opp_ftpct': oppFTPct,
            'team_tpa': teamTPA, 'team_tppct': teamTPPct, 'opp_tpa': oppTPA, 'opp_tppct': oppTPPct,
            'pace': poss 
        }