from datetime import datetime, timedelta
from sqlalchemy.sql import text
from typing import Any, List, Tuple
import numpy as np
import pandas as pd

from ..database.orms.database import get_db_session
from ..database.stores.base import LeagueStore
from ..database.orms.analytic_tables import StatMetric, LeagueMetric
from ..utils.logging_manager import get_logger

from pprint import pprint



########################################################################################
########################################################################################

class Analytics:

    def __init__(self, leagueId: str):
        self.leagueId = leagueId
        self.season = LeagueStore().get_current_season(leagueId)


    def _fetch_team_gaming(self, season: int) -> pd.DataFrame:  
        with get_db_session() as session:
            query = f"""
             WITH GameBets AS (
                SELECT 
                    team.game_id,
                    team.team_id,
                    team.opp_id,
                    games.game_date,
                    team.spread,
                    team.result,
                    team.result - team.spread AS ats,
                    team.money_line,
                    team.spread_outcome,
                    team.money_outcome,
                    ou.over_under,
                    ou.total,
                    ou.total - ou.over_under AS att,
                    ou.ou_outcome = 1 AS over_outcome,
                    ou.ou_outcome = -1 AS under_outcome,

                    -- Spread ROI
                    CASE 
                        WHEN team.spread_outcome = 1 AND team.spread_line < 0 THEN (10000/(team.spread_line*-1.0)) + 100
                        WHEN team.spread_outcome = 1 AND team.spread_line > 0 THEN team.spread_line + 100
                        WHEN team.spread_outcome = 0 THEN 100
                        ELSE 0 
                    END AS spread_roi,

                    -- Moneyline ROI
                    CASE 
                        WHEN team.money_outcome = 1 AND team.money_line > 0 THEN 100 + team.money_line
                        WHEN team.money_outcome = 1 AND team.money_line < 0 THEN (10000/(team.money_line*-1.0)) + 100
                        WHEN team.money_outcome = 0 THEN 100
                        ELSE 0
                    END AS money_roi,

                    -- Over ROI
                    CASE 
                        WHEN ou.ou_outcome = 1 AND ou.over_line > 0 THEN 100 + ou.over_line
                        WHEN ou.ou_outcome = 1 AND ou.over_line < 0 THEN (10000/(ou.over_line*-1.0)) + 100
                        WHEN ou.ou_outcome = 0 THEN 100
                        ELSE 0 
                    END over_roi,

                    -- Under ROI
                    CASE 
                        WHEN ou.ou_outcome = -1 AND ou.under_line > 0 THEN 100 + ou.under_line
                        WHEN ou.ou_outcome = -1 AND ou.under_line < 0 THEN (10000/(ou.under_line*-1.0)) + 100
                        WHEN ou.ou_outcome = 0 THEN 100
                        ELSE 0 
                    END under_roi

                FROM game_lines AS team
                INNER JOIN over_unders AS ou ON team.game_id = ou.game_id
                INNER JOIN games ON team.game_id = games.game_id AND (team.team_id = games.home_id OR team.team_id = games.away_id)
                WHERE games.season = {season} AND games.league_id = '{self.leagueId}'
                )

                SELECT * FROM GameBets;
            """
            return  pd.read_sql(query, session.bind)   


    def _get_away_home_frames(self, dataFrame: pd.DataFrame) -> List[Tuple[str, pd.DataFrame]]:

        ahFrames = [("all", dataFrame)]

        # Convert game_date to datetime

        for label in ("away", "home"):
            # Filter by date range
            ahFrames.append((label, dataFrame[(dataFrame['team_id'] == dataFrame[f"{label}_id"])]))
        return ahFrames

        


    def _get_time_frames(self, dataFrame: pd.DataFrame) -> List[Tuple[str, pd.DataFrame]]:

        today = datetime.today()
        timeFrames = [("Season", dataFrame)]

        # Convert game_date to datetime
        dataFrame['game_date'] = pd.to_datetime(dataFrame['game_date'])

        for label, gameDate in (("2Weeks", today-timedelta(14)), 
                                ("1Month", today-timedelta(31)),
                                ("2Months", today-timedelta(62))):

            # Filter by date range
            timeFrames.append((label, dataFrame[(dataFrame['game_date'] >= gameDate)]))
        return timeFrames


    def _get_valid_group(self, entityId: str, dataFrame: pd.DataFrame) -> pd.DataFrame:
        # Count the number of games per entity
        game_counts = dataFrame.groupby(entityId).size().reset_index(name='game_count')

        # Find the maximum game count
        max_games = game_counts['game_count'].max()

        # Keep only entities that have at least 60% of the max game count
        valid_group = game_counts[game_counts['game_count'] >= 0.6 * max_games]

        # Merge back with the original filtered dataset to only keep valid teams
        if len(valid_group) > 5:
            return dataFrame[dataFrame[entityId].isin(valid_group[entityId])]
        else:
            return dataFrame


    def _item_function(self, timeFrame, a_h, entityType, metricLabel, dataFrame, isMax=True):
        # records = []
        # records.append(self._set_league_metric(timeFrame, a_h, entityType, metricLabel, dataFrame, isMax))
        return self._set_league_metric(timeFrame, a_h, entityType, metricLabel, dataFrame, isMax)


    def _item_mean(
                    self, 
                    timeFrame: str, 
                    a_h: str,
                    metric: str, 
                    idType: str,
                    entityType: str, 
                    dataFrame: pd.DataFrame, 
                    metricLabel: str=None,
                    isMax: bool=True
                    ) -> List[Any]:
        
        if not metricLabel:
            metricLabel = metric

        dataFrame = dataFrame.groupby(idType)[metric].mean().reset_index(name=metricLabel)
    
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame, isMax)


    def _item_median(
                    self, 
                    timeFrame: str, 
                    a_h: str,
                    metric: str, 
                    idType: str,
                    entityType: str, 
                    dataFrame: pd.DataFrame, 
                    metricLabel: str=None,
                    isMax: bool=True
                    ) -> List[Any]:
        
        if not metricLabel:
            metricLabel = metric

        dataFrame = dataFrame.groupby(idType)[metric].median().reset_index(name=metricLabel)
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame, isMax)


    def _set_minute_adjusted(
                                self, 
                                timeFrame: str, 
                                a_h: str, 
                                stat: str, 
                                adjust: str, 
                                idType: str,
                                entityType: str, 
                                dataFrame: pd.DataFrame,
                                metricLabel: str=None,
                                isMax: bool=True) -> List[Any]:
        if not metricLabel:
            metricLabel = stat

        dataFrame = dataFrame.groupby(idType)[[stat, adjust]].apply(
                        lambda x: x[stat].sum()/(x[adjust].sum() / self._gameMinutes)
                    ).reset_index(name=metricLabel) 
        # print("\n\n",metricLabel)
        # pprint(dataFrame.head())
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame, isMax)


    def _set_team_minute_adjusted(
                                self, 
                                timeFrame: str, 
                                a_h: str, 
                                stat: str, 
                                adjust: str, 
                                dataFrame: pd.DataFrame,
                                metricLabel: str=None,
                                isMax: bool=True) -> List[Any]:
        return self._set_minute_adjusted(timeFrame, a_h, stat, adjust, "team_id", "team", dataFrame, metricLabel, isMax)




    def _item_one_per_another(
                            self, 
                            timeFrame: str, 
                            a_h: str,
                            one: str, 
                            another: str, 
                            metricLabel: str, 
                            idType: str, 
                            entityType: str, 
                            dataFrame: pd.DataFrame, 
                            isMax: bool=True
                            ) -> List[Any]:

        dataFrame = dataFrame.groupby(idType)[[one, another]].apply(
                        lambda x: ((x[one]).sum()/(x[another]).sum())
                    ).reset_index(name=metricLabel) 
        
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame, isMax)


    def _item_one_per_another_pct(
                            self, 
                            timeFrame: str, 
                            a_h: str,
                            one: str, 
                            another: str, 
                            metricLabel: str, 
                            idType: str, 
                            entityType: str, 
                            dataFrame: pd.DataFrame, 
                            isMax: bool=True
                            ) -> List[Any]:

        dataFrame = dataFrame.groupby(idType)[[one, another]].apply(
                        lambda x: ((x[one]).sum()/(x[another]).sum())*100
                    ).reset_index(name=metricLabel) 
        
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame, isMax)


    def _item_per_sum(
                    self, 
                    timeFrame: str, 
                    a_h: str,
                    one: str, 
                    another: str,
                    metricLabel: str,
                    idType: str, 
                    entityType: str,
                    dataFrame: pd.DataFrame,
                    isMax: bool=True
                    ) -> List[Any]:

        dataFrame = dataFrame.groupby(idType)[[one, another]].apply(
                        lambda x: x[one].sum() / (x[one].sum() + x[another].sum())*100
                    ).reset_index(name=metricLabel) 
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame, isMax)


    def _item_sum(
                    self, 
                    timeFrame: str, 
                    a_h: str,
                    metric: str, 
                    idType: str, 
                    entityType: str,
                    dataFrame: pd.DataFrame,
                    metricLabel: str=None,
                    isMax: bool=True) -> List[Any]:

        if not metricLabel:
            metricLabel = metric

        dataFrame = dataFrame.groupby(idType)[metric].sum().reset_index(name=metricLabel)
        return self._item_function(timeFrame, a_h, entityType, metricLabel, dataFrame, isMax)


    def _process_quantiles(self, metric: str, dataFrame: pd.DataFrame, isMax: bool = True) -> Tuple[float, float, pd.Series]:
    # Compute best and worst values
        if isMax:
            bestValue = dataFrame[metric].max()
            worstValue = dataFrame[metric].min()
        else:
            bestValue = dataFrame[metric].min()
            worstValue = dataFrame[metric].max()

        # Convert NumPy types to Python float
        bestValue = float(bestValue) if isinstance(bestValue, np.floating) else bestValue
        worstValue = float(worstValue) if isinstance(worstValue, np.floating) else worstValue

        # Compute the quantiles
        quantiles = dataFrame[metric].quantile([0.1, 0.2, 0.4, 0.6, 0.8, 0.9])

        # Convert quantiles to Python float
        quantiles = quantiles.astype(float)
        return (bestValue, worstValue, quantiles)


    


    def _set_league_metric(self, timeFrame: str, a_h: str, entityType: str, metricLabel: str, dataFrame: pd.DataFrame, isMax: bool=True) -> StatMetric:
        bestValue, worstValue, quants = self._process_quantiles(metricLabel, dataFrame, isMax=isMax)
        return LeagueMetric(
                league_id= self.leagueId,
                entity_type= entityType,
                timeframe= timeFrame,
                away_home= a_h,
                metric_name= metricLabel,
                best_value= float(bestValue),
                worst_value=float(worstValue),
                q1 = float(quants[0.1]),                
                q2 = float(quants[0.2]),                
                q4 = float(quants[0.4]),               
                q6 = float(quants[0.6]),                
                q8 = float(quants[0.8]),                
                q9 = float(quants[0.9]),               
                reference_date = datetime.now()    
            )


    def _store_models(self, all_list_models):
        # pprint(all_list_models)
        # raise
        with get_db_session() as session:
            # Add all list objects at once
            session.add_all(all_list_models)


    def _truncate_tables(self):
        with get_db_session() as session:
            session.execute(text(f"DELETE FROM league_metrics WHERE league_id = '{self.leagueId}'"))
            session.execute(text(f"DELETE FROM stat_metrics WHERE league_id = '{self.leagueId}'"))


    def scheduled_analytics(self):
        # called by extended method
        self._truncate_tables()
        # falls through to inherited class
    
