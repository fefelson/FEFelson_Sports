from .analytics import Analytics

class NBAAnalytics(Analytics):

    _minutesPerGame = 48

    def __init__(self):
        super().__init__("NBA")











# class BasketballAnalytics(Analytics):

#     def __init__(self, leagueId: str):
#         super().__init__(leagueId)


#     def _fetch_team_stats(self, season: int) -> pd.DataFrame:
#          with get_db_session() as session:
#              query = f""" 
#                         SELECT * FROM basketball_team_stats
#                             INNER JOIN games ON basketball_team_stats.game_id = games.game_id
#                             WHERE games.season = {season} AND games.league_id = '{self.leagueId}'
#                     """
#              return  pd.read_sql(query, session.bind) 


#     def _set_net_ratings(self, timeFrame: str, offense: pd.DataFrame, defense: pd.DataFrame) -> List[Any]:
#         teamRecords = []
#         teams = {"off":offense, "def":defense}
#         efficiency = {}
#         for off_def in ("off", "def"):
#             isOffense = (off_def == "off")
#             entityId = "team_id" if isOffense else "opp_id"
#             metricLabel = f"{off_def}_eff"
            
#             efficiency[off_def] = teams[off_def].groupby(entityId)[['pts', 'possessions']].apply(
#                                     lambda x: ((x['pts'] * 100) / x['possessions']).mean()
#                                     ).reset_index(name=metricLabel)
#             [teamRecords.append(x) for x in self._set_stat_metric(timeFrame, "team", entityId, metricLabel, efficiency[off_def])]
#             teamRecords.append( self._set_league_metric(timeFrame, "team", metricLabel, efficiency[off_def], isMax=isOffense))
            
#         # Merge the two DataFrames on team_id
#         netRating = efficiency["off"].merge(efficiency["def"], left_on='team_id', right_on='opp_id')
#         # Calculate Net Rating
#         netRating['net_rating'] = netRating['off_eff'] - netRating['def_eff']
#         [teamRecords.append(x) for x in self._set_stat_metric(timeFrame, "team", "team_id", "net_rating", netRating)]
#         teamRecords.append( self._set_league_metric(timeFrame, "team", "net_rating", netRating))
               
#         return teamRecords
    

#     def _set_team_minute_adjusted(self, timeFrame: str, metric: str, offense: pd.DataFrame, defense: pd.DataFrame, reverse: bool=False) -> List[Any]:
#         teamRecords = []
#         teams = {"off": offense, "def": defense}
#         for off_def in ("off", "def"):
#             isOffense = (off_def == "off")
#             isMax = isOffense if not reverse else not isOffense
#             entityId = "team_id" if isOffense else "opp_id"
#             metricLabel = f"{off_def}_{metric}"
#             dataFrame = teams[off_def].groupby(entityId)[[metric, 'minutes']].apply(
#                             lambda x: (x[metric] * (self._minutesPerGame / x['minutes'])).mean()
#                         ).reset_index(name=metricLabel) 
#             [teamRecords.append(x) for x in self._set_stat_metric(timeFrame, "team", entityId, metricLabel, dataFrame)]
#             teamRecords.append( self._set_league_metric(timeFrame, "team", metricLabel, dataFrame, isMax=isMax))
        
#         return teamRecords
    

#     def _set_team_one_per_another(self, timeFrame: str, one: str, another: str, offense: pd.DataFrame, defense: pd.DataFrame, reverse: bool=False) -> List[Any]:
#         teamRecords = []
#         teams = {"off": offense, "def": defense}
#         for off_def in ("off", "def"):
#             isOffense = (off_def == "off") 
#             isMax = isOffense if not reverse else not isOffense
#             entityId = "team_id" if isOffense else "opp_id"
#             metricLabel = f"{off_def}_{one}_per_{another}"
#             dataFrame = teams[off_def].groupby(entityId)[[one, another]].apply(
#                             lambda x: (x[one]/x[another]).mean()
#                         ).reset_index(name=metricLabel) 
#             [teamRecords.append(x) for x in self._set_stat_metric(timeFrame, "team", entityId, metricLabel, dataFrame)]
#             teamRecords.append( self._set_league_metric(timeFrame, "team", metricLabel, dataFrame, isMax=isMax))
#         return teamRecords


#     def _set_team_rebounds(self, timeFrame: str, offense: pd.DataFrame, defense: pd.DataFrame) -> List[Any]:
#         teamRecords = []
#         # Merge the offensive and defensive DataFrames on team_id (offense) and opp_id (defense)
#         for reb, opp_reb in (("oreb", "dreb"), ("dreb", "oreb")):
#             metricLabel = f"{reb}_pct"
#             reb_df = offense.merge(defense, left_on='team_id', right_on='opp_id', suffixes=('_off', '_def'))
#             reb_df[metricLabel] = reb_df[f"{reb}_off"] / (reb_df[f"{reb}_off"] + reb_df[f"{opp_reb}_def"])
            
#             # Keep only relevant columns
#             reb_df = reb_df[['team_id_off', metricLabel]]
#             # Group by team_id and take the mean OREB% per team
#             reb_summary = reb_df.groupby('team_id_off')[metricLabel].mean().reset_index()

#             [teamRecords.append(x) for x in self._set_stat_metric(timeFrame, "team", "team_id_off", metricLabel, reb_summary)]
#             teamRecords.append( self._set_league_metric(timeFrame, "team", metricLabel, reb_summary))

#         return teamRecords


#     def _team_averages_adjusted(self, teamStats: pd.DataFrame) -> List[Any]:

#         tableRecords = []
#         for timeFrame, dataFrame in self._get_time_frames(teamStats):

#             offense = self._get_valid_group("team_id", dataFrame)
#             defense = self._get_valid_group("opp_id", dataFrame)

#             [tableRecords.append(x) for x in self._set_net_ratings(timeFrame, offense, defense)]
#             [tableRecords.append(x) for x in self._set_team_minute_adjusted(timeFrame, "possessions", offense, defense)]
#             [tableRecords.append(x) for x in self._set_team_minute_adjusted(timeFrame, "pts", offense, defense)]
#             [tableRecords.append(x) for x in self._set_team_minute_adjusted(timeFrame, "fga", offense, defense)]
#             [tableRecords.append(x) for x in self._set_team_minute_adjusted(timeFrame, "fta", offense, defense)]
#             [tableRecords.append(x) for x in self._set_team_minute_adjusted(timeFrame, "tpa", offense, defense)]
#             [tableRecords.append(x) for x in self._set_team_one_per_another(timeFrame, "fgm", "fga", offense, defense)]
#             [tableRecords.append(x) for x in self._set_team_one_per_another(timeFrame, "ftm", "fta", offense, defense)]
#             [tableRecords.append(x) for x in self._set_team_one_per_another(timeFrame, "tpm", "tpa", offense, defense)]
#             [tableRecords.append(x) for x in self._set_team_one_per_another(timeFrame, "ast", "fgm", offense, defense)]
#             [tableRecords.append(x) for x in self._set_team_one_per_another(timeFrame, "turnovers", "possessions", offense, defense, reverse=True)]
#             [tableRecords.append(x) for x in self._set_team_rebounds(timeFrame, offense, defense)]
#         return tableRecords


