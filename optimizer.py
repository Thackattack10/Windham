import pandas as pd
from pulp import LpMaximize, LpProblem, LpVariable, lpSum


def optimize_lineup(df, salary_cap=60000, lineup_size=6):
    # Create LP problem
    model = LpProblem("GolfLineup", LpMaximize)

    # Create a binary variable for each player
    player_vars = {i: LpVariable(f"player_{i}", cat="Binary") for i in df.index}

    # Objective: Maximize projected points
    model += lpSum(player_vars[i] * df.loc[i, "ProjectedPoints"] for i in df.index)

    # Constraint: Total salary
    model += lpSum(player_vars[i] * df.loc[i, "Salary"] for i in df.index) <= salary_cap

    # Constraint: Exactly lineup_size players
    model += lpSum(player_vars[i] for i in df.index) == lineup_size

    # Constraint: Locked players must be selected
    for i in df[df['Locked']].index:
        model += player_vars[i] == 1

    # Solve the problem
    status = model.solve()

    # Extract results
    selected = [i for i in df.index if player_vars[i].value() == 1]

    if not selected:
        raise ValueError("No valid lineup found. Try relaxing constraints.")

    return df.loc[selected]
