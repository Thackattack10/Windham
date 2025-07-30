def project_golf_points(row):
    """
    Calculate projected points based on FPPG, SG_Putting, SG_APP, and SG_OTT.
    You can adjust the weights based on what you value more.
    """
    return (
        0.5 * row['FPPG'] +
        2.0 * row['SG_Putting'] +
        2.5 * row['SG_APP'] +
        1.8 * row['SG_OTT']
    )
