import numpy as np
from datetime import datetime
from collections import defaultdict
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler
from pprint import pprint

from ..src.database.models.database import get_db_session
from ..src.utils.gaming_utils import calculate_moneyline_probs, calculate_kelly_criterion, calculate_winnings



eloQuery = """
            SELECT home_id, away_id, home_id = winner_id AS is_winner
            FROM games AS g
            WHERE season != 2024 AND game_type = 'season'
            ORDER BY g.game_id
            """


class Elo:

    _BASE_ELO = 1500
    _K = 20  # how much ratings change after a game

    def __init__(self):
        # Initialize team ratings
        self.teamRatings = {}
        
        with get_db_session() as session:
            games = pd.read_sql(eloQuery, session.bind).dropna()
        all_teams = sorted(set(games["home_id"]))  # Sort for consistency
        team_to_idx = {team: idx for idx, team in enumerate(all_teams)}
        games["home_id"] = games["home_id"].map(team_to_idx)
        games["away_id"] = games["away_id"].map(team_to_idx)
        for _, game in games.iterrows():
            self.update_elo(game.home_id, game.away_id, game.is_winner)
        print("ELO initialized")



    def _get_team_ratings(self, teamId):
        return self.teamRatings.get(teamId, self._BASE_ELO)


    def _elo_function(self, teamA, teamB):
        diff = self._get_team_ratings(teamB) - self._get_team_ratings(teamA)
        exponent = diff / 400
        # Logistic function
        return 1 / (1 + 10**exponent)


    def expected_elo(self, teamA, teamB):
        eloA = self._elo_function(teamA, teamB)
        eloB = self._elo_function(teamB, teamA)
        return eloA, eloB



    def update_elo(self, teamA, teamB, actualA):

        eloA, eloB = self.expected_elo(teamA, teamB)

        teamARatings = self._get_team_ratings(teamA)
        teamBRatings = self._get_team_ratings(teamB)

        self.teamRatings[teamA] = teamARatings + self._K * (actualA - eloA)
        self.teamRatings[teamB] = teamBRatings + self._K * (1 - actualA - eloB)



class Tracker:
    def __init__(self, season):
        # Store results by month and team
        self.monthly_data = defaultdict(lambda: {"vegas_correct":0, "elo_correct":0, "model_correct":0, 
                                                    "elo_bet_total": 0, "elo_bet_num": 0, "elo_bet_return": 0, 
                                                    "model_bet_total": 0, "model_bet_num": 0, "model_bet_return": 0,
                                                    "vig":0, "total": 0})
        self.elo = Elo()
        # Load PyTorch model
        self.model = ResultPredictor()
        self.model.load_state_dict(torch.load("/home/ededub/FEFelson/fefelson_mvp/data/torch_model.pth"))
        self.model.eval()

    def add_game(self, game):
        """
        Add a game result and update tracking.
        Args:
            team (str): Team name
            elo_prob (float): Elo probability for team (0 to 1)
            vegas_prob (float): Vegas probability for team (0 to 1)
            result (int): 1 if team won, 0 if lost
            game_date (str): Date in 'YYYY-MM-DD' format
        """
        
        



        # Prepare inputs
        home_team_tensor = torch.tensor([game["home_id"]], dtype=torch.long)
        home_pitcher_tensor = torch.tensor([game["home_pitcher_id"]], dtype=torch.long)
        home_years_tensor = torch.tensor([game["home_age_years"]], dtype=torch.float)
        home_service_tensor = torch.tensor([game["home_service_time"]], dtype=torch.float)
        
        away_tensor = torch.tensor([game["away_id"]], dtype=torch.long)
        away_pitcher_tensor = torch.tensor([game["away_pitcher_id"]], dtype=torch.long)
        away_years_tensor = torch.tensor([game["away_age_years"]], dtype=torch.float)
        away_service_tensor = torch.tensor([game["away_service_time"]], dtype=torch.float)

        # Get model-adjusted probability
        with torch.no_grad():
            homeModel = self.model(home_team_tensor, away_tensor, home_pitcher_tensor, away_pitcher_tensor, home_years_tensor, home_service_tensor, away_years_tensor, away_service_tensor )
            homeModel = torch.sigmoid(homeModel).item()
        awayModel = 1 - homeModel
        

        homeElo, awayElo = self.elo.expected_elo(game["home_id"], game["away_id"])
        self.elo.update_elo(game["home_id"], game["away_id"], game["is_winner"])

        homeVegas, awayVegas, vig = calculate_moneyline_probs(game.team_money, game.opp_money)


        
        # Determine correctness of predictions (threshold at 0.5)
        actual_result = game["is_winner"]  # 1=home win, 0=home loss
        vegas_pred = 1 if homeVegas["implied_prob"] > 0.5 else 0
        elo_pred = 1 if homeElo > 0.5 else 0
        model_pred = 1 if homeModel > 0.5 else 0

        # Parse date to month-year
        date_obj = datetime.fromisoformat(str(game["game_date"]))
        month_key = date_obj.strftime('%Y-%m')

        # Update correctness counters
        self.monthly_data[month_key]["total"] += 1
        self.monthly_data[month_key]["vegas_correct"] += int(vegas_pred == actual_result)
        self.monthly_data[month_key]["elo_correct"] += int(elo_pred == actual_result)
        self.monthly_data[month_key]["model_correct"] += int(model_pred == actual_result)

        # Betting logic (Elo-based)
        elo_homeBet = calculate_kelly_criterion(homeElo, game.team_money, edge=vig)
        elo_awayBet = calculate_kelly_criterion(awayElo, game.opp_money, edge=vig)

        # Betting logic (model-based)
        model_homeBet = calculate_kelly_criterion(homeModel, game.team_money, edge=vig)
        model_awayBet = calculate_kelly_criterion(awayModel, game.opp_money, edge=vig)

        # print(homeVegas["implied_prob"], homeElo, homeModel, actual_result)
        # input()
        # Update betting stats
        self.monthly_data[month_key]["vig"] += vig * 100
        if elo_homeBet:
            self.monthly_data[month_key]["elo_bet_num"] += 1
            self.monthly_data[month_key]["elo_bet_total"] += elo_homeBet
            self.monthly_data[month_key]["elo_bet_return"] += calculate_winnings(elo_homeBet, game.team_money, actual_result)
        if elo_awayBet:
            self.monthly_data[month_key]["elo_bet_num"] += 1
            self.monthly_data[month_key]["elo_bet_total"] += elo_awayBet
            self.monthly_data[month_key]["elo_bet_return"] += calculate_winnings(elo_awayBet, game.opp_money, -actual_result)

        if model_homeBet:
            self.monthly_data[month_key]["model_bet_num"] += 1
            self.monthly_data[month_key]["model_bet_total"] += model_homeBet
            self.monthly_data[month_key]["model_bet_return"] += calculate_winnings(model_homeBet, game.team_money, actual_result)
        if model_awayBet:
            self.monthly_data[month_key]["model_bet_num"] += 1
            self.monthly_data[month_key]["model_bet_total"] += model_awayBet
            self.monthly_data[month_key]["model_bet_return"] += calculate_winnings(model_awayBet, game.opp_money, -actual_result)

    def get_results(self):
        """Return tracked results as a DataFrame."""
        monthly_results = {
            "Month": [],
            "VIG": [],
            "Vegas_Accuracy": [],
            "Model_Accuracy": [],
            "Elo_Accuracy": [],
            "Model_Bet_Rate": [],
            "Elo_Bet_Rate": [],
            "Elo_ROI": [],
            "Model_ROI": []
        }
        for month, data in self.monthly_data.items():
            total_games = data["total"] or 1  # Avoid division by zero
            vegas_acc = data["vegas_correct"] / total_games
            elo_acc = data["elo_correct"] / total_games
            model_acc = data["model_correct"] / total_games
            elo_rate = data["elo_bet_num"] / total_games
            elo_profit = data["elo_bet_return"] - data["elo_bet_total"]
            elo_roi = (elo_profit / data["elo_bet_total"] * 100) if data["elo_bet_total"] else 0
            model_rate = data["model_bet_num"] / total_games
            model_profit = data["model_bet_return"] - data["model_bet_total"]
            model_roi = (model_profit / data["model_bet_total"] * 100) if data["model_bet_total"] else 0
            vig_avg = data["vig"] / total_games

            monthly_results["Month"].append(month)
            monthly_results["Vegas_Accuracy"].append(round(vegas_acc * 100, 2))
            monthly_results["Elo_Accuracy"].append(round(elo_acc * 100, 2))
            monthly_results["Model_Accuracy"].append(round(model_acc * 100, 2))
            monthly_results["Elo_Bet_Rate"].append(round(elo_rate * 100, 2))
            # monthly_results["Elo_Return"].append(round(elo_profit, 2))
            monthly_results["Elo_ROI"].append(round(elo_roi, 2))
            monthly_results["Model_Bet_Rate"].append(round(model_rate * 100, 2))
            # monthly_results["Model_Return"].append(round(model_profit, 2))
            monthly_results["Model_ROI"].append(round(model_roi, 2))
            monthly_results["VIG"].append(round(vig_avg, 2))

        return pd.DataFrame(monthly_results)



######################################################################





def query_db(season):

    with get_db_session() as session:
        query = f"""
                WITH StartingPitchers AS (
                SELECT b.game_id, b.team_id, b.player_id, b.pitch_order
                FROM baseball_bullpen b
                WHERE b.pitch_order = 1
                )
                SELECT game_date, hp_team.team_id AS home_id, hp.player_id AS home_pitcher_id, 
                        AGE(g.game_date, hp.birthdate) AS home_age_years, EXTRACT(YEAR FROM g.game_date) - hp.rookie_season AS home_service_time,
                        ap_team.team_id AS away_id, ap.player_id AS away_pitcher_id, 
                        AGE(g.game_date, ap.birthdate) AS away_age_years, EXTRACT(YEAR FROM g.game_date) - ap.rookie_season AS away_service_time,
                        hp_team.team_id = g.winner_id AS is_winner, gl.money_line AS team_money, opp.money_line AS opp_money
                FROM games g
                INNER JOIN game_lines AS gl ON g.game_id = gl.game_id AND g.home_id = gl.team_id
                INNER JOIN game_lines AS opp on g.game_id = opp.game_id AND gl.team_id = opp.opp_id
                LEFT JOIN StartingPitchers AS hp_team ON g.game_id = hp_team.game_id AND g.home_id = hp_team.team_id
                LEFT JOIN players AS hp ON hp_team.player_id = hp.player_id
                LEFT JOIN StartingPitchers AS ap_team ON g.game_id = ap_team.game_id AND g.away_id = ap_team.team_id
                LEFT JOIN players AS ap ON ap_team.player_id = ap.player_id
                WHERE season = '{season}'
                ORDER BY g.game_id
                """
        return pd.read_sql(query, session.bind)  



def elo_test(season=2024):
    tracker = Tracker(season)
    df = query_db(season)
    df = df.dropna()

    df = df.dropna()

    # Create deterministic team ID mapping
    all_teams = sorted(set(df["home_id"]))  # Sort for consistency
    team_to_idx = {team: idx for idx, team in enumerate(all_teams)}
    num_teams = len(team_to_idx)

    all_players = sorted(set(df['home_pitcher_id']).union(set(df['away_pitcher_id'])))  # Sort for consistency
    player_to_idx = {player: idx for idx, player in enumerate(all_players)}
    num_players = len(player_to_idx)

    # Map team IDs
    df["home_id"] = df["home_id"].map(team_to_idx)
    df["away_id"] = df["away_id"].map(team_to_idx)

    df["home_pitcher_id"] = df["home_pitcher_id"].map(player_to_idx)
    df["away_pitcher_id"] = df["away_pitcher_id"].map(player_to_idx)

    df['home_age_years'] = (df['home_age_years'].dt.days / 365.25).round(2)
    df["home_age_years"] = StandardScaler().fit_transform(df[["home_age_years"]])
    df["home_service_time"] = StandardScaler().fit_transform(df[["home_service_time"]])

    df['away_age_years'] = (df['away_age_years'].dt.days / 365.25).round(2)
    df["away_age_years"] = StandardScaler().fit_transform(df[["away_age_years"]])
    df["away_service_time"] = StandardScaler().fit_transform(df[["away_service_time"]])

    df['is_winner'] = df['is_winner'].astype(bool)

    for _, game in df.iterrows():
        tracker.add_game(game)
        
    try:
        pprint(tracker.get_results())
    except:
        raise
    print("\n\n")


if __name__ == "__main__":
    elo_test()