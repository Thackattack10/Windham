import pandas as pd
import pulp

def optimize_lineup(df, salary_cap=50000, lineup_size=6):
    """
    Optimizes a golf lineup maximizing ProjectedPoints under salary cap and lineup size constraints.
    Respects locked players and returns only selected players.
    """
    if df.empty:
        raise ValueError("Player pool is empty")

    # Prepare data
    df = df.reset_index(drop=True)
    players = df.index.tolist()
    salaries = df['Salary'].to_dict()
    points = df['ProjectedPoints'].to_dict()
    locked = df.get('Locked', pd.Series(False, index=df.index)).to_dict()

    # Define the optimization problem
    prob = pulp.LpProblem("Golf Lineup Optimization", pulp.LpMaximize)

    # Binary decision variable for each player
    player_vars = pulp.LpVariable.dicts("player", players, cat='Binary')

    # Objective: Maximize projected points
    prob += pulp.lpSum(points[i] * player_vars[i] for i in players)

    # Constraint: Total salary must not exceed the cap
    prob += pulp.lpSum(salaries[i] * player_vars[i] for i in players) <= salary_cap

    # Constraint: Exactly `lineup_size` players must be selected
    prob += pulp.lpSum(player_vars[i] for i in players) == lineup_size

    # Lock specific players if required
    for i in players:
        if locked.get(i, False):
            prob += player_vars[i] == 1

    # Solve the problem
    status = prob.solve()

    if status != pulp.LpStatusOptimal:
        raise ValueError("No optimal lineup found")

    # Select and return only chosen players
    selected_players = [i for i in players if pulp.value(player_vars[i]) == 1]
    lineup = df.loc[selected_players].copy()
    lineup.reset_index(drop=True, inplace=True)

    return lineup

