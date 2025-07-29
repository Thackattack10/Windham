def project_golf_points(row):
    return row.get('FPPG', 0) + row.get('SG_Putting', 0) * 2 + row.get('Salary', 0) * 0.0005
