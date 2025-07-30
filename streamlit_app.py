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

    div[data-testid="fileUploaderDropzone"] {
        max-width: 220px;
        min-height: 50px;
        font-size: 0.85rem;
        padding: 6px 8px;
        border-radius: 8px;
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid #555;
    }

    div[data-testid="fileUploaderDropzone"] > label > div {
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Title ---
st.markdown('<h1 class="grass-title">⛳️ Mikey\'s Golf Optimizer</h1>', unsafe_allow_html=True)

# --- Upload CSVs Side-by-Side ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    fanduel_file = st.file_uploader(
        "📤 FanDuel CSV", type="csv", key="fd_csv",
        help="Drag and drop your FanDuel CSV here",
    )

with col2:
    putting_file = st.file_uploader(
        "📤 SG Putting CSV", type="csv", key="putting_csv",
        help="Drag and drop your SG Putting CSV here",
    )

with col3:
    approach_file = st.file_uploader(
        "📤 SG Approach CSV", type="csv", key="approach_csv",
        help="Drag and drop your SG Approach CSV here",
    )

with col4:
    ott_file = st.file_uploader(
        "📤 SG Off-the-Tee CSV", type="csv", key="ott_csv",
        help="Drag and drop your SG:OTT CSV here",
    )

# --- Process Files ---
if fanduel_file and putting_file and approach_file and ott_file:
    try:
        df_fd = pd.read_csv(fanduel_file)
        df_putting = pd.read_csv(putting_file)
        df_approach = pd.read_csv(approach_file)
        df_ott = pd.read_csv(ott_file)
    except Exception as e:
        st.error(f"Error reading CSV files: {e}")
        st.stop()

    # Clean and merge data
    df_fd['PLAYER'] = df_fd['Nickname'].str.strip().str.lower()
    df_putting['PLAYER'] = df_putting['PLAYER'].str.strip().str.lower()
    df_approach['PLAYER'] = df_approach['PLAYER'].str.strip().str.lower()
    df_ott['PLAYER'] = df_ott['PLAYER'].str.strip().str.lower()

    df = pd.merge(df_fd, df_putting[['PLAYER', 'AVG']], on='PLAYER', how='left')
    df.rename(columns={'AVG': 'SG_Putting'}, inplace=True)

    df = pd.merge(df, df_approach[['PLAYER', 'AVG']], on='PLAYER', how='left')
    df.rename(columns={'AVG': 'SG_APP'}, inplace=True)

    df = pd.merge(df, df_ott[['PLAYER', 'AVG']], on='PLAYER', how='left')
    df.rename(columns={'AVG': 'SG_OTT'}, inplace=True)

    # Fill missing strokes gained values with 0
    df['SG_Putting'] = df['SG_Putting'].fillna(0)
    df['SG_APP'] = df['SG_APP'].fillna(0)
    df['SG_OTT'] = df['SG_OTT'].fillna(0)

    # Validate required columns
    required_columns = ['Nickname', 'Salary', 'FPPG', 'SG_Putting', 'SG_APP', 'SG_OTT']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
        st.stop()

    # Projection
    df['ProjectedPoints'] = df.apply(project_golf_points, axis=1)

    # Show player pool
    st.subheader("📋 Player Pool")
    st.dataframe(df[['Nickname', 'Salary', 'FPPG', 'SG_Putting', 'SG_APP', 'SG_OTT', 'ProjectedPoints']]
                 .sort_values(by='ProjectedPoints', ascending=False))

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
            lineup = optimize_lineup(filtered_df, salary_cap=60000)  # 60k salary cap
            st.success("✅ Optimized lineup found!")
            st.dataframe(lineup[['Nickname', 'Salary', 'ProjectedPoints', 'SG_Putting', 'SG_APP', 'SG_OTT']].reset_index(drop=True))
            st.write(f"💰 Total Salary: {lineup['Salary'].sum()}")
            st.write(f"📈 Projected Points: {lineup['ProjectedPoints'].sum():.2f}")
        except ValueError as ve:
            st.error(str(ve))
