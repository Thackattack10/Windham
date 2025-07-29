# optimizer.py

from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpStatusOptimal

def optimize_lineup(players_df, salary_cap=60000):
    """
    Optimize a golf lineup for FanDuel golf contest.

    Args:
        players_df (pd.DataFrame): DataFrame with players. Must include:
            - 'Salary'
            - 'ProjectedPoints' or 'Projection'
            - 'Locked' (bool) column, True if player must be included.
        salary_cap (int): Salary cap, default 60,000.

    Returns:
        pd.DataFrame: Selected lineup with exactly 6 players, including all locked players.
    """
    prob = LpProblem("FanDuel_Golf", LpMaximize)

    player_vars = {idx: LpVariable(f"x{idx}", cat='Binary') for idx in players_df.index}

    points_col = 'ProjectedPoints' if 'ProjectedPoints' in players_df.columns else 'Projection'

    # Objective: maximize projected points
    prob += lpSum(players_df.loc[idx, points_col] * player_vars[idx] for idx in players_df.index)

    # Salary cap constraint
    prob += lpSum(players_df.loc[idx, 'Salary'] * player_vars[idx] for idx in_*_
