def project_golf_points(row):
    # Use FPPG (Fantasy Points Per Game) as the projection
    return row.get('FPPG', 0)
