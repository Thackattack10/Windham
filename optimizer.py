import pandas as pd

def optimize_lineup(df, salary_cap=60000, lineup_size=6):
    """
    Selects the optimal lineup of `lineup_size` players under `salary_cap`
    maximizing ProjectedPoints.
    """

    from itertools import combinations

    if len(df) < lineup_size:
        raise ValueError("Not enough players to form a lineup.")

    best_lineup = None
    best_score = -1

    locked = df[df['Locked']]
    non_locked = df[~df['Locked']]

    if len(locked) > lineup_size:
        raise ValueError("Too many locked players for lineup size.")

    remaining_spots = lineup_size - len(locked)

    for combo in combinations(non_locked.index, remaining_spots):
        selected = pd.concat([locked, non_locked.loc[list(combo)]])
        total_salary = selected['Salary'].sum()

        if total_salary <= salary_cap:
            score = selected['ProjectedPoints'].sum()
            if score > best_score:
                best_score = score
                best_lineup = selected.copy()

    if best_lineup is None:
        raise ValueError("No valid lineup found under the salary cap.")

    return best_lineup
