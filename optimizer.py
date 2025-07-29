from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpStatusOptimal

def optimize_lineup(players_df, salary_cap=60000):
    """
    Optimize a golf lineup for FanDuel golf contest.

    Args:
        players_df (pd.DataFrame): DataFrame with players. Must include:
            - 'Salary'
            - 'ProjectedPoints'
            - 'Locked' (bool) column, True if player must be included.
        salary_cap (int): Salary cap, default 60,000.

    Returns:
        pd.DataFrame: Selected lineup with exactly 6 players, including all locked players.
    """
    prob = LpProblem("FanDuel_Golf", LpMaximize)

    player_vars = {idx: LpVariable(f"x{idx}", cat='Binary') for idx in players_df.index}

    # Objective: maximize projected points
    prob += lpSum(players_df.loc[idx, 'ProjectedPoints'] * player_vars[idx] for idx in players_df.index)

    # Salary cap constraint
    prob += lpSum(players_df.loc[idx, 'Salary'] * player_vars[idx] for idx in players_df.index) <= salary_cap

    # Must pick exactly 6 players
    prob += lpSum(player_vars.values()) == 6

    # Locked players must be included
    locked_players = players_df[players_df.get('Locked', False)].index
    for idx in locked_players:
        prob += player_vars[idx] == 1

    # Solve the problem
    status = prob.solve()

    if status != LpStatusOptimal:
        raise ValueError("No optimal lineup found under current constraints.")

    selected = [idx for idx, var in player_vars.items() if var.value() == 1]

    return players_df.loc[selected]
