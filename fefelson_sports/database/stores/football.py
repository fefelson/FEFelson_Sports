from datetime import date
from pandas import read_sql, merge
from sqlalchemy.orm import Session
from typing import Any 

from .store import Store

from ..orms import (FootballTeamStat, PassPlay, RushPlay, KickPlay, FootballPassing, 
                        FootballRushing, FootballReceiving, FootballFumbles, FootballPunting, 
                        FootballKicking, FootballReturns, FootballDefense)



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
                            fts.pts AS off_pts, 
                            fts.time_of_poss,
                                fts.pass_plays AS off_pass_plays,
                                fts.pass_yards AS off_pass_yards, 
                                fts.rush_plays AS off_rush_plays,
                                fts.rush_yards AS off_rush_yards, 
                                fts.penalty_yards AS off_penalty_yards, 
                                fts.int_thrown + fts.fum_lost AS off_turns, 
                                fts.third_att AS off_third_att,
                                fts.third_conv AS off_third_conv, 
                                fts.fourth_att AS off_fourth_att,
                                fts.fourth_conv As off_fourth_conv,

                                opp_fts.pts AS def_pts, 
                                opp_fts.pass_plays AS def_pass_plays,
                                opp_fts.pass_yards AS def_pass_yards, 
                                opp_fts.rush_plays AS def_rush_plays,
                                opp_fts.rush_yards AS def_rush_yards, 
                                opp_fts.penalty_yards AS def_penalty_yards, 
                                opp_fts.int_thrown + opp_fts.fum_lost AS def_turns, 
                                opp_fts.third_att AS def_third_att,
                                opp_fts.third_conv AS def_third_conv, 
                                opp_fts.fourth_att AS def_fourth_att,
                                opp_fts.fourth_conv As def_fourth_conv

                    FROM football_team_stats AS fts
                    INNER JOIN football_team_stats AS opp_fts ON fts.game_id = opp_fts.game_id AND fts.team_id = opp_fts.opp_id
                    INNER JOIN games AS g ON fts.game_id = g.game_id
                    INNER JOIN leagues AS l ON g.league_id = l.league_id
                    WHERE fts.team_id = {teamId} {andGD}
                """
        result = read_sql(query, session.bind)
        
        # 2. Passing + Rushing TDs - FIXED: separate queries, no cross-join
        # Offensive TDs
        query_off_td = f"""
            SELECT g.game_id,
                SUM(p.pass_att) AS off_pass_att,
                SUM(p.pass_comp) AS off_pass_comp,
                SUM(p.pass_td) AS off_pass_td,
                SUM(ABS(p.sack_yds_lost)) AS off_sack_yds_lost

            FROM passing p
            INNER JOIN games g ON p.game_id = g.game_id
            INNER JOIN leagues AS l ON g.league_id = l.league_id
            WHERE p.team_id = {teamId} {andGD}
            GROUP BY g.game_id
        """
        off_pass = read_sql(query_off_td, session.bind)

        # Defensive TDs (allowed = opponent's offensive)
        query_def_td = f"""
            SELECT g.game_id,
                SUM(opp_p.pass_att) AS def_pass_att,
                SUM(opp_p.pass_comp) AS def_pass_comp,
                SUM(opp_p.pass_td) AS def_pass_td,
                SUM(ABS(opp_p.sack_yds_lost)) AS def_sack_yds_lost

            FROM passing opp_p
            INNER JOIN games g ON opp_p.game_id = g.game_id
            INNER JOIN leagues AS l ON g.league_id = l.league_id
            WHERE opp_p.opp_id = {teamId} {andGD}
            GROUP BY g.game_id
        """
        def_pass = read_sql(query_def_td, session.bind)

        # 2. Rushing TDs - FIXED: separate queries, no cross-join
        # Offensive TDs
        query_off_rush_td = f"""
            SELECT g.game_id,
                SUM(r.rush_td) AS off_rush_td
            FROM rushing r
            INNER JOIN games g ON r.game_id = g.game_id
            INNER JOIN leagues AS l ON g.league_id = l.league_id
            WHERE r.team_id = {teamId} {andGD}
            GROUP BY g.game_id
        """
        off_rush = read_sql(query_off_rush_td, session.bind)

        # Defensive Rush TDs (allowed = opponent's offensive)
        query_def_rush_td = f"""
            SELECT g.game_id, 
                SUM(opp_r.rush_td) AS def_rush_td
            FROM rushing opp_r
            INNER JOIN games g ON opp_r.game_id = g.game_id
            INNER JOIN leagues AS l ON g.league_id = l.league_id
            WHERE opp_r.opp_id = {teamId} {andGD}
            GROUP BY g.game_id
        """
        def_rush = read_sql(query_def_rush_td, session.bind)

        # 3. Defender - Uses OPPONENTS STATS FOR OFFENSE
        query_off_defender = f"""
            SELECT g.game_id, 
                SUM(opp_d.pass_def) AS off_pass_def, 
                SUM(opp_d.qb_hits) AS off_qb_hits,
                SUM(opp_d.ints) AS off_pass_ints, 
                SUM(opp_d.sacks) AS off_sacks

            FROM defense opp_d
            INNER JOIN games g ON opp_d.game_id = g.game_id
            INNER JOIN leagues AS l ON g.league_id = l.league_id
            WHERE opp_d.opp_id = {teamId} {andGD}
            GROUP BY g.game_id
        """
        off_defender = read_sql(query_off_defender, session.bind)

        # Defensive Defenderss (allowed = opponent's offensive)
        query_def_defender = f"""
            SELECT g.game_id, 
                SUM(d.pass_def) AS def_pass_def, 
                SUM(d.qb_hits) AS def_qb_hits,
                SUM(d.ints) AS def_pass_ints, 
                SUM(d.sacks) AS def_sacks

            FROM defense d
            INNER JOIN games g ON d.game_id = g.game_id
            INNER JOIN leagues AS l ON g.league_id = l.league_id
            WHERE d.team_id = {teamId} {andGD}
            GROUP BY g.game_id
        """
        def_defender = read_sql(query_def_defender, session.bind)


        # 3. Punts - FIXED: separate
        query_off_punts = f"""
            SELECT g.game_id, 
                SUM(punts) AS off_punts,
                SUM(punt_yds) AS off_punt_yards

            FROM punts p
            INNER JOIN games g ON p.game_id = g.game_id
            INNER JOIN leagues AS l ON g.league_id = l.league_id
            WHERE p.team_id = {teamId} {andGD}
            GROUP BY g.game_id
        """
        off_punts = read_sql(query_off_punts, session.bind)

        query_def_punts = f"""
            SELECT g.game_id, 
                SUM(punts) AS def_punts,
                SUM(punt_yds) AS def_punt_yards

            FROM punts p
            INNER JOIN games g ON p.game_id = g.game_id
            INNER JOIN leagues AS l ON g.league_id = l.league_id
            WHERE p.opp_id = {teamId} {andGD}
            GROUP BY g.game_id
        """
        def_punts = read_sql(query_def_punts, session.bind)

        # 4. Kick Returns - FIXED: separate
        query_off_kr = f"""
            SELECT g.game_id, 
                    SUM(kr_yds) AS off_kr_yds,
                    SUM(pr_yds) AS off_pr_yds

            FROM kick_returns kr
            INNER JOIN games g ON kr.game_id = g.game_id
            INNER JOIN leagues AS l ON g.league_id = l.league_id
            WHERE kr.team_id = {teamId} {andGD}
            GROUP BY g.game_id
        """
        off_kr = read_sql(query_off_kr, session.bind)

        query_def_kr = f"""
            SELECT g.game_id,  
                    SUM(kr_yds) AS def_kr_yds,
                    SUM(pr_yds) AS def_pr_yds

            FROM kick_returns kr
            INNER JOIN games g ON kr.game_id = g.game_id
            INNER JOIN leagues AS l ON g.league_id = l.league_id
            WHERE kr.opp_id = {teamId} {andGD}
            GROUP BY g.game_id
        """
        def_kr = read_sql(query_def_kr, session.bind)

        # 4. Field Goals - FIXED: separate
        query_off_fg = f"""
            SELECT g.game_id, 
                    SUM(fga) AS off_fga

            FROM kicks k
            INNER JOIN games g ON k.game_id = g.game_id
            INNER JOIN leagues AS l ON g.league_id = l.league_id
            WHERE k.team_id = {teamId} {andGD}
            GROUP BY g.game_id
        """
        off_fg = read_sql(query_off_fg, session.bind)

        query_def_fg = f"""
            SELECT g.game_id, 
                    SUM(fga) AS def_fga

            FROM kicks k
            INNER JOIN games g ON k.game_id = g.game_id
            INNER JOIN leagues AS l ON g.league_id = l.league_id
            WHERE k.opp_id = {teamId} {andGD}
            GROUP BY g.game_id
        """
        def_fg = read_sql(query_def_fg, session.bind)

        # 5. Merge all safely
        result = merge(result, off_pass, how="left", on="game_id")
        result = merge(result, def_pass, how="left", on="game_id")
        result = merge(result, off_rush, how="left", on="game_id")
        result = merge(result, def_rush, how="left", on="game_id")
        result = merge(result, off_punts, how="left", on="game_id")
        result = merge(result, def_punts, how="left", on="game_id")
        result = merge(result, off_fg, how="left", on="game_id")
        result = merge(result, def_fg, how="left", on="game_id")
        result = merge(result, off_defender, how="left", on="game_id")
        result = merge(result, def_defender, how="left", on="game_id")
        result = merge(result, off_kr, how="left", on="game_id")
        result = merge(result, def_kr, how="left", on="game_id")


        # Keep your other merges (defense, returns) if needed - they look okay

        # 6. Calculate drives
        drive_cols = [
            'off_pass_td', 'off_rush_td', 'off_turns', 'off_fga', 'off_punts',
            'off_fourth_att', 'off_fourth_conv',
            'def_pass_td', 'def_rush_td', 'def_turns', 'def_fga', 'def_punts',
            'def_fourth_att', 'def_fourth_conv'
        ]
        result[drive_cols] = result[drive_cols].fillna(0)

        result["off_drives"] = (
            result["off_pass_td"] + result["off_rush_td"] + result["off_turns"] +
            result["off_fga"] + result["off_punts"] +
            (result["off_fourth_att"] - result["off_fourth_conv"])
        ).astype(int)

        result["def_drives"] = (
            result["def_pass_td"] + result["def_rush_td"] + result["def_turns"] +
            result["def_fga"] + result["def_punts"] +
            (result["def_fourth_att"] - result["def_fourth_conv"])
        ).astype(int)

        if awayHome != "all":
            result = result[(result['team_id'] == result[f"{awayHome}_id"])]
        if len(result) == 0:
            return None

        return {
        
        "off_pts": result["off_pts"].sum() / result["off_drives"].sum() if result["off_drives"].sum() else 0,
        "off_plays": result["off_rush_plays"].mean() + result["off_pass_plays"].mean(),
        "off_pass_pct": (result["off_pass_plays"].mean() / (result["off_rush_plays"].mean() + result["off_pass_plays"].mean()))*100,
        "off_comp_pct": (result["off_pass_comp"].sum() / result["off_pass_att"].sum()) *100 if result["off_pass_att"].sum() else 0,
        "off_yards_per_comp": result["off_pass_yards"].sum() / result["off_pass_comp"].sum() if result["off_pass_comp"].sum() else 0,
        "off_yards_per_car": result["off_rush_yards"].sum() / result["off_rush_plays"].sum() if result["off_rush_plays"].sum() else 0,
        "off_rush_yards": result["off_rush_yards"].sum() / result["off_drives"].sum() if result["off_drives"].sum() else 0,
        "off_pass_yards": result["off_pass_yards"].sum() / result["off_drives"].sum() if result["off_drives"].sum() else 0,
        "off_sack_yds_lost": result["off_sack_yds_lost"].sum() / result["off_drives"].sum() if result["off_drives"].sum() else 0,
        "off_turns": result["off_turns"].sum() / result["off_drives"].sum() if result["off_drives"].sum() else 0,
        "off_penalty_yards": result["off_penalty_yards"].sum() / result["off_drives"].sum() if result["off_drives"].sum() else 0,
        "off_third_pct": (result["off_third_conv"].sum() / result["off_third_att"].sum())*100 if result["off_third_att"].sum() else 0,
        "off_fourth_pct": (result["off_fourth_conv"].sum() / result["off_fourth_att"].sum())*100 if result["off_fourth_att"].sum() > 0 else 0,
        "off_pass_protect": ((result["off_sacks"].sum()*2 + result['off_qb_hits'].sum()) / result['off_pass_plays'].sum()) *100 if result["off_pass_plays"].sum() else 0,
        "off_return_yds": result["off_kr_yds"].median() + result["off_pr_yds"].median(),
        'off_go_pct': (result["off_fourth_att"].sum() / (result["off_fourth_att"].sum() + result["off_fga"].sum()))*100 if (result["off_fourth_att"].sum() + result["off_fga"].sum()) else 0,

        

        "def_pts": result["def_pts"].sum() / result["def_drives"].sum() if result["def_drives"].sum() else 0,
        "def_plays": result["def_rush_plays"].mean() + result["def_pass_plays"].mean(),
        "def_pass_pct": (result["def_pass_plays"].mean() / (result["def_rush_plays"].mean() + result["def_pass_plays"].mean()))*100,
        "def_comp_pct": result["def_pass_comp"].sum() / result["def_pass_att"].sum() *100 if result["def_pass_att"].sum() else 0,
        "def_yards_per_comp": result["def_pass_yards"].sum() / result["def_pass_comp"].sum() if result["def_pass_comp"].sum() else 0,
        "def_yards_per_car": result["def_rush_yards"].sum() / result["def_rush_plays"].sum() if result["def_rush_plays"].sum() else 0,
        "def_rush_yards": result["def_rush_yards"].sum()  / result["def_drives"].sum() if result["def_drives"].sum() else 0,
        "def_pass_yards": result["def_pass_yards"].sum() / result["def_drives"].sum() if result["def_drives"].sum() else 0,
        "def_sack_yds_lost": result["def_sack_yds_lost"].sum() / result["def_drives"].sum() if result["def_drives"].sum() else 0,
        "def_turns": result["def_turns"].sum() / result["def_drives"].sum() if result["def_drives"].sum() else 0,
        "def_penalty_yards": result["def_penalty_yards"].sum() / result["def_drives"].sum() if result["def_drives"].sum() else 0,
        "def_third_pct": (result["def_third_conv"].sum() / result["def_third_att"].sum())*100 if result["def_third_att"].sum() else 0,
        "def_fourth_pct": (result["def_fourth_conv"].sum() / result["def_fourth_att"].sum())*100 if result["def_fourth_att"].sum() > 0 else 0,
        "def_pass_rush": ((result["def_sacks"].sum()*2 + result['def_qb_hits'].sum()) / result['def_pass_plays'].sum()) *100 if result["def_pass_plays"].sum() else 0,
        "def_pass_cover":  ((result["def_pass_def"].sum() + result['def_pass_ints'].sum()*3) / result['def_pass_plays'].sum()) - (result["def_pass_comp"].sum() / result["def_pass_att"].sum()) if result["def_pass_att"].sum() else 0,
        "def_return_yds": result["def_kr_yds"].median() + result["def_pr_yds"].median(),
        'def_go_pct': (result["def_fourth_att"].sum() / (result["def_fourth_att"].sum() + result["def_fga"].sum()))*100 if (result["def_fourth_att"].sum() + result["def_fga"].sum()) else 0,

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


    def insert_kicking(self, session: Session, statsData: dict) -> None:
        self.insert(session, FootballKicking, statsData)


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
