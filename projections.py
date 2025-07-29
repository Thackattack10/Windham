def project_golf_points(row):
    """
    Projection formula combining FPPG and SG Putting.
    You can adjust weights here as you like.
    """
    fppg = row.get('FPPG', 0)
    sg_putting = row.get('SG_Putting', 0)

    # Example weights: 80% FPPG + 20% SG Putting
    projection = fppg * 0.7 + sg_putting * 0.3
    return projection
