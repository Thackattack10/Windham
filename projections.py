def project_golf_points(row):
    # Adjust weights as needed
    return (
        0.5 * row['FPPG'] +
        2.0 * row['SG_Putting'] +
        2.5 * row['SG_APP'] +
        1.8 * row['SG_OTT']
    )
