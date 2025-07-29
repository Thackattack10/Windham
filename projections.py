def project_golf_points(row):
    # Simple weighted projection formula using FPPG and Strokes Gained Putting
    fppg_weight = 0.7
    sg_putting_weight = 0.3

    fppg = row.get('FPPG', 0)
    sg_putting = row.get('SG_Putting', 0)

    projection = fppg_weight * fppg + sg_putting_weight * sg_putting
    return projection
