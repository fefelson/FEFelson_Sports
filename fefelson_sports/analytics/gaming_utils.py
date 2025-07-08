
def moneyline_to_implied_prob(ml):
        if ml > 0:
            return 100 / (ml + 100)
        else:
            return -ml / (-ml + 100)



def calculate_moneyline_probs(moneyA, moneyB):
    """
    Calculate true probabilities and vig from two money lines.
    Args:
        ml1 (int): Money line for team 1 (e.g., -150)
        ml2 (int): Money line for team 2 (e.g., +140)
    Returns:
        dict: Implied probs, true probs, and vig percentage
    """
    _team = {"implied_prob":None, "true_prob":None}

    teamA = _team.copy()
    teamB = _team.copy()

    # Convert money lines to implied probabilities
    
    impProbA = moneyline_to_implied_prob(moneyA)
    impProbB = moneyline_to_implied_prob(moneyB)
    
    # Calculate total implied probability (includes vig)
    totImpProb = impProbA + impProbB
    
    # Calculate vig (overround) as a percentage
    vig = (totImpProb - 1) 
    
    # Calculate true probabilities (remove vig)
    teamA["implied_prob"] = impProbA
    teamA["true_prob"] = impProbA / totImpProb
    
    teamB["implied_prob"] = impProbB
    teamB["true_prob"] = impProbB / totImpProb

    return teamA, teamB, vig


def calculate_kelly_criterion(true_prob, gambling_line, *, bankroll=100.0, edge=0.05, fraction=1.0):
    """
    Calculate the Kelly Criterion bet size.
    
    Args:
        true_prob (float): Your estimated probability of winning (0 to 1)
        odds (float): Moneyline odds (e.g., -150, +140)
        bankroll (float): Current bankroll (default 1.0 for unit betting)
        fraction (float): Fraction of Kelly to bet (e.g., 1.0 = full Kelly, 0.5 = half Kelly)
    Returns:
        float: Recommended bet size (fraction of bankroll times bankroll)
        None: If no positive edge exists
    """
    # Convert moneyline odds to decimal odds (payout per unit bet)
    if gambling_line > 0:
        decimal_odds = (gambling_line / 100) + 1  # e.g., +140 -> 1.4
    else:
        decimal_odds = (100 / -gambling_line) + 1  # e.g., -150 -> 1.6667
    
    # Implied probability from odds (without vig adjustment)
    implied_prob = 1 / decimal_odds if gambling_line > 0 else -gambling_line / (-gambling_line + 100)
    
    # Net odds (b in Kelly formula: payout - 1)
    b = decimal_odds - 1
    
    # Kelly formula: f = (bp - q) / b, where p = true_prob, q = 1 - p
    p = true_prob
    q = 1 - true_prob
    
    # Edge must be positive to bet
    if p <= implied_prob + edge:
        return None  # Not enough edge, no bet
    
    # Kelly fraction
    kelly_fraction = (b * p - q) / b
    
    # Apply fraction of Kelly and ensure it’s between 0 and 1
    bet_fraction = max(0, min(fraction * kelly_fraction, 1))
    
    # Bet size in units
    bet_size = bet_fraction * bankroll
    
    return bet_size



def calculate_winnings(betsize, gambling_line, result):
    """
    Calculate winnings based on bet size, odds, and result.
    
    Args:
        betsize (float): Amount wagered (e.g., 10.0)
        odds (float): Moneyline odds (e.g., -150, +140)
        result (float or int): Outcome (e.g., 1 for win, 0 or -1 for loss)
    
    Returns:
        float: Winnings (profit + betsize) if result >= 0 and bet wins
        float: Negative betsize (loss) if result < 0
    """
    
    # Ensure betsize is positive
    if betsize <= 0:
        raise ValueError("Betsize must be positive")
    
    # Loss case: result < 0
    if result < 0:
        return 0

    if result == 0:
        return betsize
    
    # Win case: calculate payout based on odds
    if result > 0:  # Assuming > 0 means win 
        if gambling_line > 0:
            # Positive odds: profit = betsize * (odds / 100), winnings = profit + betsize
            profit = betsize * (gambling_line / 100)
            winnings = betsize + profit
        else:
            # Negative odds: profit = betsize * (100 / -odds), winnings = profit + betsize
            profit = betsize * (100 / -gambling_line)
            winnings = betsize + profit
        return winnings
    
    # Shouldn't reach here with proper result values, but included for completeness
    raise ValueError


