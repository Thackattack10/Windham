import streamlit as st
import pandas as pd
from projections import project_golf_points
from optimizer import optimize_lineup

# --- Custom CSS with dimmed background ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Luckiest+Guy&display=swap');

    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)),
                          url("https://www.comingsoon.net/wp-content/uploads/sites/3/2025/07/Happy-Gilmore-2-Death.jpg?resize=101");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: #39ff14;
    }

    .grass-title {
        font-family: 'Luckiest Guy', cursive;
        font-size: 4rem;
        color: #228B22;
        text-align: center;
        text-shadow:
            1px 1px 0px #006400,
            2px 2px 1px #32CD32,
            3px 3px 2px #7CFC00;
        margin-bottom: 2rem;
    }

    .block-container {
        padding-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Title ---
st.markdown('<h1 class="grass-title">⛳️ Mikey\'s Golf Optimizer</h1>', unsafe_allow_html=True)

# --- Upload FanDuel and SG Putting CSVs ---
fanduel_file = st.file_uploader("📤 Upload FanDuel CSV", type="csv")
putting_file = st.file_uploader("📤 Upload Strokes Gained Putting CSV", type="csv")

if fanduel_file and putting_file:
    try:
        df_fd = pd.read_csv(fanduel_file)
        df_putting = pd.read_csv(putting_file)
    except Exception as e:
        st.error(f"Error reading CSV files: {e}")
        st.stop()

    # Clean and merge data
    df_fd['PLAYER'] = df_fd['Nickname'].str.strip().str.lower()
    df_putting['PLAYER'] = df_putting['PLAYER'].str.strip().str.lower()

    df = pd.merge(df_fd, df_putting[['PLAYER', 'AVG']], on='PLAYER', how='left')
    df.rename(columns={'AVG': 'SG_Putting'}, inplace=True)

    # Fill missing putting with 0
    df['SG_Putting'] = df['SG_Putting'].fillna(0)

    # Validate required columns
    required_columns = ['Nickname', 'Salary', 'FPPG', 'SG_Putting']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
        st.stop()

    # Projection
    df['ProjectedPoints'] = df.apply(project_golf_points, axis=1)

    # Show player pool
    st.subheader("📋 Player Pool")
    st.dataframe(df[['Nickname', 'Salary', 'FPPG', 'SG_Putting', 'ProjectedPoints']].sort_values(by='ProjectedPoints', ascending=False))

    # Lock / exclude players
    locked_players = st.multiselect("🔒 Lock In Specific Players", options=df['Nickname'].tolist())
    excluded_players = st.multiselect("🚫 Exclude These Players", options=df['Nickname'].tolist())

    # Filter
    filtered_df = df[~df['Nickname'].isin(excluded_players)].copy()
    filtered_df['Locked'] = filtered_df['Nickname'].isin(locked_players)

    # Run optimizer
    st.subheader("🎯 Optimize Your Lineup")
    if st.button("Run Optimizer"):
        try:
            lineup = optimize_lineup(filtered_df)
            st.success("✅ Optimized lineup found!")
            st.dataframe(lineup[['Nickname', 'Salary', 'ProjectedPoints']].reset_index(drop=True))
            st.write(f"💰 Total Salary: {lineup['Salary'].sum()}")
            st.write(f"📈 Projected Points: {lineup['ProjectedPoints'].sum():.2f}")
        except ValueError as ve:
            st.error(str(ve))
