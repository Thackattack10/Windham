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
putting_file = st.file_uploader("Upload Strokes Gained Putting CSV (Optional)", type="csv")

if salary_file:
    try:
        df = pd.read_csv(salary_file)
    except Exception as e:
        st.error(f"Error loading FanDuel CSV: {e}")
        st.stop()

    # Check required columns
    required_columns = ['Nickname', 'Salary']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns in FanDuel CSV: {missing_cols}")
        st.stop()

    # Load and merge strokes gained putting CSV
    if putting_file:
        try:
            putting_df = pd.read_csv(putting_file)
            if 'Player' in putting_df.columns:
                putting_df.rename(columns={'Player': 'Nickname'}, inplace=True)
            df = pd.merge(df, putting_df[['Nickname', 'SG_Putting']], on='Nickname', how='left')
        except Exception as e:
            st.warning(f"Couldn't merge putting data: {e}")
            df['SG_Putting'] = 0
    else:
        df['SG_Putting'] = 0

    # --- Apply projection ---
    df['ProjectedPoints'] = df.apply(project_golf_points, axis=1)

    # --- Show player pool ---
    st.subheader("📋 Player Pool")
    st.dataframe(df[['Nickname', 'Salary', 'SG_Putting', 'ProjectedPoints']].sort_values(by='ProjectedPoints', ascending=False))

    # --- Lock and exclude players ---
    locked_players = st.multiselect("🔒 Lock In Specific Players", options=df['Nickname'].tolist())
    excluded_players = st.multiselect("🚫 Exclude These Players", options=df['Nickname'].tolist())

    # Filter out excluded players
    filtered_df = df[~df['Nickname'].isin(excluded_players)].copy()
    filtered_df['Locked'] = filtered_df['Nickname'].isin(locked_players)

    # --- Number of lineups ---
    num_lineups = st.number_input("🧮 How many unique lineups?", min_value=1, max_value=20, value=1)

    # --- Run optimizer ---
    st.subheader("🎯 Optimize Your Lineup")
    if st.button("Run Optimizer"):
        used_players = set()
        all_lineups = []

        for i in range(num_lineups):
            temp_df = filtered_df[~filtered_df['Nickname'].isin(used_players)].copy()

            try:
                lineup = optimize_lineup(temp_df)
                all_lineups.append(lineup)
                used_players.update(lineup['Nickname'])
            except ValueError:
                st.warning(f"❌ Could not generate lineup #{i+1} — not enough unique players.")
                break

        if all_lineups:
            st.success(f"✅ Generated {len(all_lineups)} unique lineup(s)!")
            for i, lineup in enumerate(all_lineups):
                st.subheader(f"📋 Lineup #{i+1}")
                st.dataframe(lineup[['Nickname', 'Salary', 'ProjectedPoints']].reset_index(drop=True))
                st.write(f"💰 Total Salary: {lineup['Salary'].sum()}")
                st.write(f"📈 Projected Points: {lineup['ProjectedPoints'].sum():.2f}")

else:
    st.info("Please upload a FanDuel CSV file to get started.")
