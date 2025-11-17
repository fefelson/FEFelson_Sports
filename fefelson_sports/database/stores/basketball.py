from datetime import date, timedelta
from sqlalchemy.orm import Session
from pandas import read_sql, merge
from .store import Store

from ..orms import BasketballTeamStat, BasketballPlayerStat, BasketballShot



###################################################################
###################################################################


def game_minutes_convert(dataframe, defaultMinutes, gameMinutes):
    return (dataframe.sum() * defaultMinutes) / gameMinutes if gameMinutes > 0 else 0


###################################################################
###################################################################


class TeamStatStore(Store):
    
    def __init__(self):
        super().__init__()


    def get_b2b(self, teamId, session = None):
        if not teamId:
            return None 

        yest = date.today() - timedelta(1)
        session = self._execute_with_session(session)
        query = f""" 
                SELECT g.game_id
                        
                    FROM game_lines AS gl
                    INNER JOIN games AS g ON gl.game_id = g.game_id
                    WHERE gl.team_id = {teamId} AND DATE(game_date) = '{yest}'::DATE
            """
        result = read_sql(query, session.bind) 
        return result["game_id"].count()


    def get_team_stats(self, teamId, timeFrame, awayHome, session = None):
        if not teamId:
            return None 

        session = self._execute_with_session(session)
        andGD = self._and_gameDate(timeFrame)
        query = f""" 
                SELECT g.league_id, g.game_id, home_id, away_id, bts.team_id, bts.opp_id, game_date, 
                            bts.minutes AS total_time,
                            bts.poss + opp_bts.poss AS pace,
                            
                            bts.poss AS off_poss,
                            bts.fga - bts.tpa AS off_2pa,
                            bts.fga AS off_fga, 
                            bts.fta AS off_fta,
                            bts.tpa AS off_3pa,
                            bts.fgm - bts.tpm AS off_2pm, 
                            bts.fgm AS off_fgm,
                            bts.ftm AS off_ftm,
                            bts.tpm AS off_3pm,
                            bts.oreb AS off_oreb, 
                            bts.dreb AS off_dreb,
                            bts.pts AS off_pts,
                            bts.ast AS off_ast, 
                            bts.stl AS off_stl, 
                            bts.blk AS off_blk,
                            bts.turns AS off_turn,
                            bts.fouls AS off_fouls, 
                            bts.fb_pts AS off_fb_pts,
                            bts.pts_in_pt AS off_pts_in_pt,

                            opp_bts.poss AS def_poss,
                            opp_bts.fga - opp_bts.tpa AS def_2pa,
                            opp_bts.fga AS def_fga, 
                            opp_bts.fta AS def_fta,
                            opp_bts.tpa AS def_3pa,
                            opp_bts.fgm - opp_bts.tpm AS def_2pm,
                            opp_bts.fgm AS def_fgm, 
                            opp_bts.ftm AS def_ftm,
                            opp_bts.tpm AS def_3pm,
                            opp_bts.oreb AS def_oreb, 
                            opp_bts.dreb AS def_dreb,
                            opp_bts.pts AS def_pts,
                            opp_bts.ast AS def_ast, 
                            opp_bts.stl AS def_stl, 
                            opp_bts.blk AS def_blk,
                            opp_bts.turns AS def_turn,
                            opp_bts.fouls AS def_fouls, 
                            opp_bts.fb_pts AS def_fb_pts,
                            opp_bts.pts_in_pt AS def_pts_in_pt

                    FROM basketball_team_stats AS bts
                    INNER JOIN basketball_team_stats AS opp_bts ON bts.game_id = opp_bts.game_id AND bts.team_id = opp_bts.opp_id
                    INNER JOIN games AS g ON bts.game_id = g.game_id
                    INNER JOIN leagues AS l ON g.league_id = l.league_id
                    WHERE bts.team_id = {teamId} {andGD}
            """
        result = read_sql(query, session.bind) 

        clutch_two_query = f"""
                            SELECT g.game_id,
                                    COUNT(g.game_id) AS off_clutch_2pa, 
                                    SUM(CASE WHEN shot_made THEN 1 ELSE 0 END) AS off_clutch_2pm

                            FROM basketball_shots AS bs
                            INNER JOIN games AS g ON bs.game_id = g.game_id
                            INNER JOIN leagues AS l ON g.league_id = l.league_id
                            WHERE team_id = {teamId} {andGD} AND clutch = TRUE AND points = 2
                            GROUP BY g.game_id
                            """
        clutchTwoResult = read_sql(clutch_two_query, session.bind)
        
        clutch_one_query = f"""
                        SELECT g.game_id, 
                                COUNT(g.game_id) AS off_clutch_fta, 
                                SUM(CASE WHEN shot_made THEN 1 ELSE 0 END) AS off_clutch_ftm

                        FROM basketball_shots AS bs
                        INNER JOIN games AS g ON bs.game_id = g.game_id
                        INNER JOIN leagues AS l ON g.league_id = l.league_id
                        WHERE team_id = {teamId} {andGD} AND clutch = TRUE AND points = 1
                        GROUP BY g.game_id
                        """
        clutchFTResult = read_sql(clutch_one_query, session.bind)
        
        clutch_three_query = f"""
                        SELECT g.game_id, 
                                COUNT(g.game_id) AS off_clutch_3pa, 
                                SUM(CASE WHEN shot_made THEN 1 ELSE 0 END) AS off_clutch_3pm

                        FROM basketball_shots AS bs
                        INNER JOIN games AS g ON bs.game_id = g.game_id
                        INNER JOIN leagues AS l ON g.league_id = l.league_id
                        WHERE team_id = {teamId} {andGD} AND clutch = TRUE AND points = 3
                        GROUP BY g.game_id
                        """
        clutchThreeResult = read_sql(clutch_three_query, session.bind)

        clutch_def_two_query = f"""
                        SELECT g.game_id,
                                COUNT(g.game_id) AS def_clutch_2pa, 
                                SUM(CASE WHEN shot_made THEN 1 ELSE 0 END) AS def_clutch_2pm

                        FROM basketball_shots AS bs
                        INNER JOIN games AS g ON bs.game_id = g.game_id
                        INNER JOIN leagues AS l ON g.league_id = l.league_id
                        WHERE opp_id = {teamId} {andGD}  AND clutch = TRUE AND points = 2
                        GROUP BY g.game_id
                        """
        clutchDefTwoResult = read_sql(clutch_def_two_query, session.bind)
        
        clutch_def_one_query = f"""
                        SELECT g.game_id, 
                                COUNT(g.game_id) AS def_clutch_fta, 
                                SUM(CASE WHEN shot_made THEN 1 ELSE 0 END) AS def_clutch_ftm

                        FROM basketball_shots AS bs
                        INNER JOIN games AS g ON bs.game_id = g.game_id
                        INNER JOIN leagues AS l ON g.league_id = l.league_id
                        WHERE opp_id = {teamId} {andGD} AND clutch = TRUE AND points = 1
                        GROUP BY g.game_id
                        """
        clutchDefFTResult = read_sql(clutch_def_one_query, session.bind)
        
        clutch_def_three_query = f"""
                        SELECT g.game_id,
                                COUNT(g.game_id) AS def_clutch_3pa, 
                                SUM(CASE WHEN shot_made THEN 1 ELSE 0 END) AS def_clutch_3pm

                        FROM basketball_shots AS bs
                        INNER JOIN games AS g ON bs.game_id = g.game_id
                        INNER JOIN leagues AS l ON g.league_id = l.league_id
                        WHERE opp_id = {teamId} {andGD} AND clutch = TRUE AND points = 3
                        GROUP BY g.game_id
                        """
        clutchDefThreeResult = read_sql(clutch_def_three_query, session.bind)

        result = merge(result, clutchTwoResult, how="left", on="game_id")
        result = merge(result, clutchFTResult, how="left", on="game_id")
        result = merge(result, clutchThreeResult, how="left", on="game_id")
        result = merge(result, clutchDefTwoResult, how="left", on="game_id")
        result = merge(result, clutchDefFTResult, how="left", on="game_id")
        result = merge(result, clutchDefThreeResult, how="left", on="game_id")

        clutch_cols = [
            'off_clutch_2pa', 'off_clutch_2pm', 'off_clutch_3pa', 'off_clutch_3pm', 
            'off_clutch_fta', 'off_clutch_ftm',
            'def_clutch_2pa', 'def_clutch_2pm', 'def_clutch_3pa', 'def_clutch_3pm', 
            'def_clutch_fta', 'def_clutch_ftm',
        ]

        result[clutch_cols] = result[clutch_cols].fillna(0)

        result["off_clutch_pts"] = (
            result["off_clutch_2pm"]*2 + result["off_clutch_3pm"]*3 + result["off_clutch_fta"]
        ).astype(int)

        result["off_clutch_fga"] = (
            result["off_clutch_2pa"] + result["off_clutch_3pa"]
        ).astype(int)

        result["def_clutch_pts"] = (
            result["def_clutch_2pm"]*2 + result["def_clutch_3pm"]*3 + result["def_clutch_fta"]
        ).astype(int)

        result["def_clutch_fga"] = (
            result["def_clutch_2pa"] + result["def_clutch_3pa"]
        ).astype(int)
    
        if awayHome != "all":
            result = result[(result['team_id'] == result[f"{awayHome}_id"])]

        if len(result) == 0:
            return None

        defaultMinutes = 48 if result["league_id"].iloc[0] == "NBA" else 40
        gameMinutes = result["total_time"].sum()

        offEff = (result["off_pts"].sum() * 100) / result["off_poss"].sum()
        defEff = (result["def_pts"].sum() * 100) / result["def_poss"].sum()
        
        
        return {
            'gp': len(result),
            "net_rating": offEff - defEff,
            "pace": game_minutes_convert(result["pace"], defaultMinutes, gameMinutes),
             
            "off_eff": offEff,
            'off_2p_pct': (result["off_2pm"].sum() / result["off_2pa"].sum())*100 if result["off_2pa"].sum() else 0,
            'off_ft_poss': (result["off_ftm"].sum() / result["off_poss"].sum())*100 if result["off_poss"].sum() else 0,
            'off_3p_pct': (result["off_3pm"].sum() / result["off_3pa"].sum())*100 if result["off_3pa"].sum() else 0,
            'off_ast_pct': (result["off_ast"].sum() / result["off_fgm"].sum())*100 if result["off_fgm"].sum() else 0,
            'off_turn_pct': (result["off_turn"].sum() / result["off_poss"].sum())*100 if result["off_poss"].sum() else 0,
            'off_reb_pct': (result["off_oreb"].sum() / (result["off_oreb"].sum() + result["def_dreb"].sum()))*100 if (result["off_oreb"].sum() + result["def_dreb"].sum()) else 0,
            'off_2_or_3': (result["off_2pa"].sum() / (result["off_2pa"].sum() + result["off_3pa"].sum()))*100 if result["off_fgm"].sum() else 0,
            'off_fb_pct': (result["off_fb_pts"].sum() / result["off_poss"].sum())*100 if result["off_poss"].sum() else 0,
            'off_pts_in_pt_pct': (result["off_pts_in_pt"].sum() / result["off_poss"].sum())*100 if result["off_poss"].sum() else 0,
            'off_3pm_pct': (result["off_3pm"].sum() / result["off_poss"].sum())*100 if result["off_poss"].sum() else 0,
            'off_clutch_ts': (result["off_clutch_pts"].sum() / (2*(result["off_clutch_fga"].sum() + result["off_clutch_fta"].sum() * .44)))*100 if result["off_clutch_fga"].sum() else None,
            'off_clutch_ft': (result["off_clutch_ftm"].sum() / result["off_clutch_fta"].sum())*100 if result["off_clutch_fta"].sum() else None,

            "def_eff": defEff,
            'def_2p_pct': (result["def_2pm"].sum() / result["def_2pa"].sum())*100 if result["def_2pa"].sum() else 0,
            'def_ft_poss': (result["def_ftm"].sum() / result["def_poss"].sum())*100 if result["def_poss"].sum() else 0,
            'def_3p_pct': (result["def_3pm"].sum() / result["def_3pa"].sum())*100 if result["def_3pa"].sum() else 0,
            'def_ast_pct': (result["def_ast"].sum() / result["def_fgm"].sum())*100 if result["def_fgm"].sum() else 0,
            'def_turn_pct': (result["def_turn"].sum() / result["def_poss"].sum())*100 if result["def_poss"].sum() else 0,
            'def_reb_pct': (result["off_dreb"].sum() / (result["off_dreb"].sum() + result["def_oreb"].sum()))*100 if (result["off_dreb"].sum() + result["def_oreb"].sum()) else 0,
            'def_2_or_3': (result["def_2pa"].sum() / (result["def_2pa"].sum() + result["def_3pa"].sum()))*100 if result["def_fgm"].sum() else 0,
            'def_fb_pct': (result["def_fb_pts"].sum() / result["def_poss"].sum())*100 if result["def_poss"].sum() else 0,
            'def_pts_in_pt_pct': (result["def_pts_in_pt"].sum() / result["def_poss"].sum())*100 if result["def_poss"].sum() else 0,
            'def_3pm_pct': (result["def_3pm"].sum() / result["def_poss"].sum())*100 if result["def_poss"].sum() else 0,
            'def_clutch_ts': (result["def_clutch_pts"].sum() / (2*(result["def_clutch_fga"].sum() + result["def_clutch_fta"].sum() * .44)))*100 if result["def_clutch_fga"].sum() else None,
        }


    def get_by_id(self, statsData: dict, session: Session = None) -> BasketballTeamStat:
        session = self._execute_with_session(session)
        return session.query(BasketballTeamStat).filter_by(game_id=statsData["game_id"], 
                                                            team_id=statsData["team_id"]).first()


    def insert(self, session: Session, statsData: dict) -> None:
        if not self.get_by_id(statsData, session):
            session.add(BasketballTeamStat(**statsData))


###################################################################
###################################################################


class PlayerStatStore(Store):

    def __init__(self):
        super().__init__()


    def get_by_id(self, statsData: dict, session: Session = None) -> BasketballPlayerStat:
        session = self._execute_with_session(session)
        return session.query(BasketballPlayerStat).filter_by(game_id=statsData["game_id"], 
                                                    player_id=statsData["player_id"]).first()


    def insert(self, session: Session, statsData:dict) -> None:
        if not self.get_by_id(statsData, session):
            session.add(BasketballPlayerStat(**statsData))



###################################################################
###################################################################


class PlayerShotStore(Store):

    def __init__(self):
        super().__init__()


    def get_by_id(self, statsData: dict, session: Session = None) -> BasketballShot:
        session = self._execute_with_session(session)
        return session.query(BasketballShot).filter_by(game_id=statsData["game_id"], 
                                                    play_num=statsData["play_num"]).first()


    def insert(self, session: Session, statsData:dict) -> None:
        if not self.get_by_id(statsData, session):
            session.add(BasketballShot(**statsData))
