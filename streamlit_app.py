import streamlit as st
import pandas as pd
from projections import project_golf_points
from optimizer import optimize_lineup

# --- Custom CSS: Happy Gilmore Background + Grass Title ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Luckiest+Guy&display=swap');

    .stApp {
        background-image: url("https://www.comingsoon.net/wp-content/uploads/sites/3/2025/07/Happy-Gilmore-2-Death.jpg?resize=101");
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
st.subheader("Upload FanDuel Golf CSV")
salary_file = st.file_uploader("Upload FanDuel CSV", type="csv", key="salary")

st.subheader("Upload Strokes Gained Putting CSV")
putting_file = st.file_uploader("Upload SG Putting CSV", type="csv", key="putting")

if salary_file:
    try:
        df = pd.read_csv(salary_file)
    except Exception as e:
        st.error(f"Error loading FanDuel CSV file: {e}")
        st.stop()

    # Clean Fanduel CSV columns & rename for consistency
    # Check essential columns exist
    required_fd_cols = ['Nickname', 'Salary', 'FPPG']
    missing_fd = [col for col in required_fd_cols if col not in df.columns]
    if missing_fd:
        st.error(f"Missing required columns in FanDuel CSV: {missing_fd}")
        st.stop()

    # Rename FPPG column for projections if needed
    df.rename(columns={'FPPG': 'FPPG'}, inplace=True)

    # Initialize SG_Putting to 0 in case no file uploaded
    df['SG_Putting'] = 0

    if putting_file:
        try:
            putt_df = pd.read_csv(putting_file)
        except Exception as e:
            st.error(f"Error loading SG Putting CSV file: {e}")
            st.stop()

        # We assume putting CSV has PLAYER and TOTAL SG:PUTTING columns
        # Clean column names
        putt_df.rename(columns=lambda x: x.strip(), inplace=True)

        # Check required columns
        if not {'PLAYER', 'TOTAL SG:PUTTING'}.issubset(putt_df.columns):
            st.error("SG Putting CSV must contain 'PLAYER' and 'TOTAL SG:PUTTING' columns")
            st.stop()

        # Merge on Nickname <-> PLAYER (case insensitive)
        # Create lowercase keys for merge
        df['nickname_lower'] = df['Nickname'].str.lower()
        putt_df['player_lower'] = putt_df['PLAYER'].str.lower()

        merged_df = pd.merge(
            df,
            putt_df[['player_lower', 'TOTAL SG:PUTTING']],
            left_on='nickname_lower',
            right_on='player_lower',
            how='left'
        )

        # Fill NaNs with 0 for missing SG Putting
        merged_df['SG_Putting'] = merged_df['TOTAL SG:PUTTING'].fillna(0)

        # Replace df with merged version without helper columns
        df = merged_df.drop(columns=['nickname_lower', 'player_lower', 'TOTAL SG:PUTTING', 'PLAYER'])

    else:
        st.info("No SG Putting CSV uploaded — SG_Putting set to zero for all players.")

    # Apply projection function
    df['ProjectedPoints'] = df.apply(project_golf_points, axis=1)

    # Show player pool
    st.subheader("📋 Player Pool")
    st.dataframe(
        df[['Nickname', 'Salary', 'FPPG', 'SG_Putting', 'ProjectedPoints']].sort_values(by='ProjectedPoints', ascending=False)
    )

    # Lock players
    locked_players = st.multiselect("🔒 Lock In Specific Players", options=df['Nickname'].tolist())

    # Exclude players
    excluded_players = st.multiselect("🚫 Exclude These Players", options=df['Nickname'].tolist())

    # Filter out excluded players
    filtered_df = df[~df['Nickname'].isin(excluded_players)].copy()
    filtered_df['Locked'] = filtered_df['Nickname'].isin(locked_players)

    # Optimize lineup button
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


