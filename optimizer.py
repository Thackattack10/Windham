from pulp import LpMaximize, LpProblem, LpVariable, lpSum, PULP_CBC_CMD

def optimize_lineup(df, salary_cap=60000, lineup_size=6):
    model = LpProblem("GolfLineup", LpMaximize)

    vars = {i: LpVariable(f"player_{i}", cat="Binary") for i in df.index}

    model += lpSum(vars[i] * df.loc[i, "ProjectedPoints"] for i in df.index)

    model += lpSum(vars[i] * df.loc[i, "Salary"] for i in df.index) <= salary_cap

    model += lpSum(vars[i] for i in df.index) == lineup_size

    for i in df[df['Locked']].index:
        model += vars[i] == 1

    # Use the default CBC solver explicitly with msg=True to see solver output
    solver = PULP_CBC_CMD(msg=True, timeLimit=30)  # 30 seconds timeout

    status = model.solve(solver)

    # Print solver status for debugging
    print(f"Solver status: {status}")

    selected = [i for i in df.index if vars[i].value() == 1]

    if not selected:
        raise ValueError("No valid lineup found.")

    return df.loc[selected]
