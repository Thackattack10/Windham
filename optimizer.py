from pulp import LpMaximize, LpProblem, LpVariable, lpSum


def optimize_lineup(df, salary_cap=60000, lineup_size=6):
    model = LpProblem("GolfLineup", LpMaximize)

    # Variables: binary for each player
    vars = {i: LpVariable(f"player_{i}", cat="Binary") for i in df.index}

    # Objective: maximize projected points
    model += lpSum(vars[i] * df.loc[i, "ProjectedPoints"] for i in df.index)

    # Salary cap constraint
    model += lpSum(vars[i] * df.loc[i, "Salary"] for i in df.index) <= salary_cap

    # Lineup size constraint
    model += lpSum(vars[i] for i in df.index) == lineup_size

    # Force locked players
    for i in df[df['Locked']].index:
        model += vars[i] == 1

    model.solve()

    selected = [i for i in df.index if vars[i].value() == 1]
    if not selected:
        raise ValueError("No valid lineup found.")
    return df.loc[selected]
