def project_golf_points(row):
    salary_score = row.get('Salary', 0) * 0.0005
    putting_bonus = row.get('SG_Putting', 0) * 3  # tweak weight
    return salary_score + putting_bonus
