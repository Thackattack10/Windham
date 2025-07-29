def project_golf_points(row):
    """
    Projection formula combining FPPG, SG Putting, and SG Approach.
    Adjust weights as you see fit.
    """
    fppg = row.get('FPPG', 0)
    sg_putting = row.get('SG_Putting', 0)
    sg_app = row.get('SG_APP', 0)

    # Example weights: 60% FPPG + 20% SG Putting + 20% SG Approach
    projection = fppg * 0.4 + sg_putting * 0.3 + sg_app * 0.3
    return projection
