ott_weight = st.slider("Weight: SG OTT", 0.0, 1.0, 0.25)
app_weight = st.slider("Weight: SG APP", 0.0, 1.0, 0.3)
putt_weight = st.slider("Weight: SG Putting", 0.0, 1.0, 0.2)

def project_golf_points(row):
    return (
        row['FPPG'] +
        putt_weight * row['SG_Putting'] +
        app_weight * row['SG_APP'] +
        ott_weight * row['SG_OTT']
    )
