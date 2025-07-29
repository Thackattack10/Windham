# optimizer.py

from pulp import LpMaximize, LpProblem, LpVariable, lpSum

def optimize_lineup(players_df):
    """
    Optimize a golf lineup for FanDuel golf contest.
    
    Constraints:
    - Salary cap <= 50000 (example)
    - Exactly 6 players selected
    """
    prob = LpProblem("FanDuel_Golf", LpMaximize)

    # Create a binary variable for each player: 1 if selected, else 0
    player_vars = {idx: LpVariable(f"x{idx}", cat='Binary') for idx in players_df.index}

    # Objective: maximize sum of projected points
    prob += lpSum(players_df.loc[idx, 'Projection'] * player_vars[idx] for idx in players_df.index)

    # Salary cap constraint (adjust if different)
    prob += lpSum(players_df.loc[idx, 'Salary'] * player_vars[idx] for idx in players_df.index) <= 50000

    # Must pick exactly 6 players
    prob += lpSum(player_vars.values()) == 6

    # Solve the problem
    prob.solve()

    # Get selected players
    selected = [idx for idx, var in player_vars.items() if var.value() == 1]

    return players_df.loc[selected]
