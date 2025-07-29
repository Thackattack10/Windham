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

# --- Upload CSVs ---
fanduel_file = st.file_uploader("📤 Upload FanDuel CSV", type="csv", key="fd_csv")
putting_file = st.file_uploader("📤 Upload Strokes Gained Putting CSV", type="csv", key="putting_csv")
approach_file = st.file_uploader("📤 Upload Strokes Gained Approach CSV", type="csv", key="approach_csv")

if fanduel_file and putting_file:
    try:
        df_fd = pd.read_csv(fanduel_file)
        df_putting = pd.read_csv(putting_file)
    except Exception as e:
        st.error(f"Error reading FanDuel or Putting CSV files: {e}")
        st.stop()

    # Clean player names to lowercase and strip whitespace for merging
    df_fd['PLAYER'] = df_fd['Nickname'].str.strip().str.lower()
    df_putting['PLAYER'] = df_putting['PLAYER'].str.strip().str.lower()

    # Merge putting data
    df = pd.merge(df_fd, df_putting[['PLAYER', 'AVG']], on='PLAYER', how='left')
    df.rename(columns={'AVG': 'SG_Putting'}, inplace=True)
    df['SG_Putting'] = df['SG_Putting'].fillna(0)

    # Merge approach data if uploaded
    if approach_file:
        try:
            df_approach = pd.read_csv(approach_file)
            df_approach['PLAYER'] = df_approach['PLAYER'].str.strip().str.lower()

            if 'AVG' not in df_approach.columns:
                st.error("The approach CSV must have an 'AVG' column with the SG approach values.")
                st.stop()

            df = pd.merge(df, df_approach[['PLAYER', 'AVG']], on='PLAYER', how='left')
            df.rename(columns={'AVG': 'SG_APP'}, inplace=True)
            df['SG_APP'] = df['SG_APP'].fillna(0)

        except Exception as e:
            st.error(f"Error reading Strokes Gained Approach CSV: {e}")
            st.stop()
    else:
        df['SG_APP'] = 0  # No approach file uploaded, fill with zero

    # Validate required columns for projection
    required_columns = ['Nickname', 'Salary', 'FPPG', 'SG_Putting', 'SG_APP']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
        st.stop()

    # Compute projected points using your projection function
    df['ProjectedPoints'] = df.apply(project_golf_points, axis=1)

    # Show player pool
    st.subheader("📋 Player Pool")
    st.dataframe(df[['Nickname', 'Salary', 'FPPG', 'SG_Putting', 'SG_APP', 'ProjectedPoints']].sort_values(by='ProjectedPoints', ascending=False))

    # Player lock/exclude UI
    locked_players = st.multiselect("🔒 Lock In Specific Players", options=df['Nickname'].tolist())
    excluded_players = st.multiselect("🚫 Exclude These Players", options=df['Nickname'].tolist())

    # Filter dataframe accordingly
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
else:
    st.info("Please upload both FanDuel CSV and Strokes Gained Putting CSV to get started.")
