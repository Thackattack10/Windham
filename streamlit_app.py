import streamlit as st
import pandas as pd
from projections import project_golf_points
from optimizer import optimize_lineup

# --- Custom CSS ---
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
salary_file = st.file_uploader("Upload FanDuel Golf CSV", type="csv")
putting_file = st.file_uploader("Upload Strokes Gained Putting CSV", type="csv")

if salary_file:
    try:
        df = pd.read_csv(salary_file)
    except Exception as e:
        st.error(f"Error loading FanDuel CSV file: {e}")
        st.stop()

    # Validate required columns in FanDuel CSV
    required_cols = ['Nickname', 'First Name', 'Salary', 'FPPG']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns in FanDuel CSV: {missing_cols}")
        st.stop()

    # --- Merge putting data if provided ---
    if putting_file:
        try:
            putting_df = pd.read_csv(putting_file)

            # Rename columns for merging
            putting_df.rename(columns={'PLAYER': 'FullName', 'AVG': 'SG_Putting'}, inplace=True)

            # Normalize names: lowercase, strip whitespace
            putting_df['FullName'] = putting_df['FullName'].str.strip().str.lower()
            df['FullName'] = (df['First Name'] + ' ' + df['Nickname']).str.strip().str.lower()

            # Merge putting stats into main df
            df = pd.merge(df, putting_df[['FullName', 'SG_Putting']], on='FullName', how='left')

            # Fill missing strokes gained putting with 0
            df['SG_Putting'] = df['SG_Putting'].fillna(0)

        except Exception as e:
            st.warning(f"Couldn't merge putting data: {e}")
            df['SG_Putting'] = 0
    else:
        df['SG_Putting'] = 0

    # Apply projection function (from projections.py)
    df['ProjectedPoints'] = df.apply(project_golf_points, axis=1)

    # Show player pool
    st.subheader("📋 Player Pool")
    st.dataframe(
        df[['Nickname', 'First Name', 'Salary', 'FPPG', 'SG_Putting', 'ProjectedPoints']].sort_values(
            by='ProjectedPoints', ascending=False
        )
    )

    # Lock players
    locked_players = st.multiselect("🔒 Lock In Specific Players", options=df[']()_
