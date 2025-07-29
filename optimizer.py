import pulp

def optimize_lineup(df, salary_cap=50000, lineup_size=6):
    """
    Optimizes a golf lineup maximizing ProjectedPoints under salary cap and lineup size constraints.
    Respects locked players.
    """
    if df.empty:
        raise ValueError("Player pool is empty")

    players = df.index.tolist()
    salaries = df['Salary'].to_dict()
    points = df['ProjectedPoints'].to_dict()
    locked = df['Locked'].to_dict()

    # Define problem
    prob = pulp.LpProblem("Golf Lineup Optimization", pulp.LpMaximize)

    # Decision variables: 1 if player selected, else 0
    player_vars = pulp.LpVariable.dicts("player", players, cat='Binary')

    # Objective: maximize projected points
    prob += pulp.lpSum([points[i] * player_vars[i] for i in players])

    # Salary cap constraint
    prob += pulp.lpSum([salaries[i] * player_vars[i] for i in players]) <= salary_cap

    # Lineup size constraint
    prob += pulp.lpSum([player_vars[i] for i in players]) == lineup_size

    # Lock players: force selected if locked
    for i in players:
        if locked.get(i, False):
            prob += player_vars[i] == 1

    # Solve
    status = prob.solve()

    if status != pulp.LpStatusOptimal:
        raise ValueError("No optimal lineup found")

    # Get selected players
    selected = [i for i in players if pulp.value(player_vars[i]) == 1]

    lineup = df.loc[selected].copy()
    return lineup
