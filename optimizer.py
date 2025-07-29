import pandas as pd
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpBinary


def optimize_lineup(df, lineup_size=6, salary_cap=60000):
    """
    Optimize a DFS golf lineup using projected points (including SG:APP).
    
    Parameters:
    - df: DataFrame containing player data with 'Nickname', 'Salary', 'ProjectedPoints', 'Locked'
    - lineup_size: number of golfers to include in the lineup
    - salary_cap: total salary cap for the lineup

    Returns:
    - DataFrame with selected players
    """
    if df.empty:
        raise ValueError("Input DataFrame is empty.")

    # Define LP problem
    prob = LpProblem("DFS_Golf_Lineup", LpMaximize)

    # Create binary decision variables for each player
    player_vars = {
        idx: LpVariable(f"player_{idx}", cat=LpBinary)
        for idx in df.index
    }

    # Objective: maximize total projected points
    prob += lpSum(player_vars[i] * df.loc[i, 'ProjectedPoints'] for i in df.index)

    # Constraint: exactly `lineup_size` players
    prob += lpSum(player_vars[i] for i in df.index) == lineup_size

    # Constraint: total salary ≤ salary cap
    prob += lpSum(player_vars[i] * df.loc[i, 'Salary'] for i in df.index) <= salary_cap

    # Handle locked players
    locked_players = df[df['Locked'] == True]
    for i in locked_players.index:
        prob += player_vars[i] == 1

    # Solve the problem
    result_status = prob.solve()

    # Extract selected lineup
    selected_indices = [i for i in df.index if player_vars[i].value() == 1]
    if len(selected_indices) != lineup_size:
        raise ValueError("Unable to generate a valid lineup. Try adjusting player pool or constraints.")

    return df.loc[selected_indices].copy()
