from datetime import date
from pandas import read_sql, merge
from sqlalchemy.orm import Session
from typing import Any 

from .store import Store

from ..orms import (FootballTeamStat, PassPlay, RushPlay, KickPlay, FootballPassing, 
                        FootballRushing, FootballReceiving, FootballFumbles, FootballPunting, 
                        FootballReturns, FootballDefense)



###################################################################
###################################################################


class TeamStatStore(Store):
    
    def __init__(self):
        super().__init__()


    def get_team_stats(self, teamId, timeFrame, awayHome, session = None):
        if not teamId:
            return None 

        session = self._execute_with_session(session)
        andGD = self._and_gameDate(timeFrame)
        query = f""" 
                    SELECT g.game_id, g.home_id, g.away_id, fts.team_id, fts.opp_id, game_date,
                            CASE WHEN fts.time_of_poss + opp_fts.time_of_poss < 60 THEN 60 ELSE fts.time_of_poss + opp_fts.time_of_poss END AS total_time,
                            fts.pts AS off_pts, fts.drives AS off_drives, fts.pass_plays AS off_pass_plays,
                            fts.pass_yards AS off_pass_yards, fts.rush_plays AS off_rush_plays,
                            fts.rush_yards AS off_rush_yards, fts.penalties AS off_penalties, 
                            fts.penalty_yards AS off_penalty_yards, fts.time_of_poss AS time_of_poss,
                            fts.int_thrown + fts.fum_lost AS off_turns, 
                            fts.sack_yds_lost AS off_sack_yds_lost, fts.third_att AS off_third_att,
                            fts.third_conv AS off_third_conv, fts.fourth_att AS off_fourth_att,
                            fts.fourth_conv As off_fourth_conv,

                            opp_fts.pts AS def_pts, opp_fts.drives AS def_drives, opp_fts.pass_plays AS def_pass_plays,
                            opp_fts.pass_yards AS def_pass_yards, opp_fts.rush_plays AS def_rush_plays,
                            opp_fts.rush_yards AS def_rush_yards, opp_fts.penalties AS def_penalties, 
                            opp_fts.penalty_yards AS def_penalty_yards, 
                            opp_fts.int_thrown + opp_fts.fum_lost AS def_turns, 
                            opp_fts.sack_yds_lost AS def_sack_yds_lost, opp_fts.third_att AS def_third_att,
                            opp_fts.third_conv AS def_third_conv, opp_fts.fourth_att AS def_fourth_att,
                            opp_fts.fourth_conv As def_fourth_conv

                    FROM football_team_stats AS fts
                    INNER JOIN football_team_stats AS opp_fts ON fts.game_id = opp_fts.game_id AND fts.team_id = opp_fts.opp_id
                    INNER JOIN games AS g ON fts.game_id = g.game_id
                    INNER JOIN leagues AS l ON g.league_id = l.league_id
                    WHERE fts.team_id = {teamId} {andGD}
                """
        result =  read_sql(query, session.bind) 

        query = f""" 
                    SELECT g.game_id,
                        SUM(p.pass_att) AS off_pass_att, SUM(p.pass_comp) AS off_pass_comp,
                        SUM(opp_p.pass_att) AS def_pass_att, SUM(opp_p.pass_comp) AS def_pass_comp

                    FROM passing AS p
                    INNER JOIN passing AS opp_p ON p.game_id = opp_p.game_id AND p.team_id = opp_p.opp_id
                    INNER JOIN games AS g ON p.game_id = g.game_id
                    INNER JOIN leagues AS l ON g.league_id = l.league_id
                    WHERE p.team_id = {teamId} {andGD}
                    GROUP BY g.game_id
                """
        passResult =  read_sql(query, session.bind) 
        result = merge(result, passResult, how="left", on="game_id")

        query = f""" 
                    SELECT g.game_id,
                        SUM(opp_d.pass_def) AS off_pass_def, SUM(opp_d.qb_hits) AS off_qb_hits,
                        SUM(opp_d.ints) AS off_pass_ints, SUM(opp_d.sacks) AS off_sacks,

                        SUM(d.pass_def) AS def_pass_def, SUM(d.qb_hits) AS def_qb_hits,
                        SUM(d.ints) AS def_pass_ints, SUM(d.sacks) AS def_sacks

                    FROM defense AS d
                    INNER JOIN defense AS opp_d ON d.game_id = opp_d.game_id AND d.team_id = opp_d.opp_id
                    INNER JOIN games AS g ON d.game_id = g.game_id
                    INNER JOIN leagues AS l ON g.league_id = l.league_id
                    WHERE d.team_id = {teamId} {andGD}
                    GROUP BY g.game_id
                """
        defResult =  read_sql(query, session.bind) 
        result = merge(result, defResult, how="left", on="game_id")
        if awayHome != "all":
            result = result[(result['game_id'] == result[f"{awayHome}_id"])]

        return {
        "time_of_poss": (result["time_of_poss"].sum() / result["total_time"].sum())*100,
        
        "off_pts": result["off_pts"].sum() / (result["total_time"].sum()/60),
        "off_plays": result["off_rush_plays"].mean() + result["off_pass_plays"].mean(),
        "off_pass_pct": (result["off_pass_plays"].mean() / (result["off_rush_plays"].mean() + result["off_pass_plays"].mean()))*100,
        "off_comp_pct": (result["off_pass_comp"].sum() / result["off_pass_att"].sum()) *100,
        "off_yards_per_comp": result["off_pass_yards"].sum() / result["off_pass_comp"].sum(),
        "off_yards_per_car": result["off_rush_yards"].sum() / result["off_rush_plays"].sum(),
        "off_rush_yards": result["off_rush_yards"].sum() / (result["total_time"].sum()/60),
        "off_pass_yards": result["off_pass_yards"].sum() / (result["total_time"].sum()/60),
        "off_sack_yds_lost": result["off_sack_yds_lost"].sum() / (result["total_time"].sum()/60),
        "off_turns": result["off_turns"].sum() / (result["total_time"].sum()/60),
        "off_penalty_yards": result["off_penalty_yards"].sum() / (result["total_time"].sum()/60),
        "off_third_pct": result["off_third_conv"].mean() / result["off_fourth_att"].mean(),
        "off_fourth_pct": result["off_fourth_conv"].mean() / result["off_fourth_att"].mean(),
        "off_pass_protect": ((result["off_sacks"].sum() + result['off_qb_hits'].sum()) / result['off_pass_plays'].sum()) *100,
        
        

        "def_pts": result["def_pts"].sum() / (result["total_time"].sum()/60),
        "def_plays": result["def_rush_plays"].mean() + result["def_pass_plays"].mean(),
        "def_pass_pct": result["def_pass_plays"].mean() / (result["def_rush_plays"].mean() + result["def_pass_plays"].mean()),
        "def_comp_pct": result["def_pass_comp"].sum() / result["def_pass_att"].sum() *100,
        "def_yards_per_comp": result["def_pass_yards"].sum() / result["def_pass_comp"].sum(),
        "def_yards_per_car": result["def_rush_yards"].sum() / result["def_rush_plays"].sum(),
        "def_rush_yards": result["def_rush_yards"].sum() / (result["total_time"].sum()/60),
        "def_pass_yards": result["def_pass_yards"].sum() / (result["total_time"].sum()/60),
        "def_sack_yds_lost": result["def_sack_yds_lost"].sum() / (result["total_time"].sum()/60),
        "def_turns": result["def_turns"].sum() / (result["total_time"].sum()/60),
        "def_penalty_yards": result["def_penalty_yards"].sum() / (result["total_time"].sum()/60),
        "def_third_pct": result["def_third_conv"].mean() / result["def_fourth_att"].mean(),
        "def_fourth_pct": result["def_fourth_conv"].mean() / result["def_fourth_att"].mean(),
        "def_pass_rush": ((result["def_sacks"].sum() + result['def_qb_hits'].sum()) / result['def_pass_plays'].sum()) *100,
        "def_pass_cover":  ((result["def_pass_def"].sum() + result['def_pass_ints'].sum()) / result['def_pass_plays'].sum()) - (result["def_pass_comp"].sum() / result["def_pass_att"].sum())
        }



    def get_by_id(self, statsData: dict, session: Session = None) -> FootballTeamStat:
        session = self._execute_with_session(session)
        return session.query(FootballTeamStat).filter_by(game_id=statsData["game_id"], 
                                                            team_id=statsData["team_id"]).first()


    def insert(self, session: Session, statsData: dict) -> None:
        if not self.get_by_id(statsData, session):
            session.add(FootballTeamStat(**statsData))


###################################################################
###################################################################


class PlayerStatStore(Store):

    def __init__(self):
        super().__init__()


    def get_by_id(self, statsData: dict, statClass: Any, session: Session = None) -> Any:
        session = self._execute_with_session(session)
        return session.query(statClass).filter_by(game_id=statsData["game_id"], 
                                                    player_id=statsData["player_id"]).first()


    def insert(self, session: Session, statClass: Any, statsData:dict) -> None:
        if not self.get_by_id(statsData, statClass, session):
            session.add(statClass(**statsData))


    def insert_passing(self, session: Session, statsData: dict) -> None:
        self.insert(session, FootballPassing, statsData)
        

    def insert_rushing(self, session: Session, statsData: dict) -> None:
        self.insert(session, FootballRushing, statsData)


    def insert_receiving(self, session: Session, statsData: dict) -> None:
        self.insert(session, FootballReceiving, statsData)


    def insert_fumbles(self, session: Session, statsData: dict) -> None:
        self.insert(session, FootballFumbles, statsData)


    def insert_punting(self, session: Session, statsData: dict) -> None:
        self.insert(session, FootballPunting, statsData)


    def insert_returns(self, session: Session, statsData: dict) -> None:
        self.insert(session, FootballReturns, statsData)


    def insert_defense(self, session: Session, statsData: dict) -> None:
        self.insert(session, FootballDefense, statsData)


###################################################################
###################################################################


class PlayerPlayStore(Store):

    def __init__(self):
        super().__init__()


    def get_by_id(self, statsData: dict, statClass: Any, session: Session = None) -> Any:
        session = self._execute_with_session(session)
        return session.query(statClass).filter_by(game_id=statsData["game_id"], 
                                                    play_num=statsData["play_num"]).first()


    def insert(self, session: Session, statClass: Any, statsData:dict) -> None:
        if not self.get_by_id(statsData, statClass, session):
            session.add(statClass(**statsData))



    def insert_kick_plays(self, session: Session, statsData: dict) -> None:
        self.insert(session, KickPlay, statsData)


    def insert_pass_plays(self, session: Session, statsData: dict) -> None:
        self.insert(session, PassPlay, statsData)


    def insert_rush_plays(self, session: Session, statsData: dict) -> None:
        self.insert(session, RushPlay, statsData)
