import streamlit as st
import pandas as pd
from projections import project_golf_points
from optimizer import optimize_lineup

# --- Retro Neon Style ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
    body, .stApp {
        background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%);
        color: #39ff14;
        font-family: 'Press Start 2P', cursive;
    }
    .stTitle {
        font-size: 3rem;
        text-shadow:
            0 0 5px #39ff14,
            0 0 10px #39ff14,
            0 0 20px #0fa,
            0 0 30px #0fa,
            0 0 40px #0fa;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="stTitle">⛳️ Golf FanDuel Optimizer ⛳️</h1>', unsafe_allow_html=True)

salary_file = st.file_uploader("Upload FanDuel Golf CSV", type="csv")

if salary_file:
    try:
        df = pd.read_csv(salary_file)
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        st.stop()

    required_columns = ['Nickname', 'Salary']
    if not all(col in df.columns for col in required_columns):
        st.error(f"CSV must contain columns: {', '.join(required_columns)}")
        st.stop()

    # Add placeholder stats (replace with your actual stats or data scrape)
    df['StrokesGained'] = 0.5  # example stat
    df['DrivingAccuracy'] = 0.7
    df['GreensInRegulation'] = 0.65

    # Calculate projections using your function
    df['Projection'] = df.apply(project_golf_points, axis=1)
    df['Projection'].fillna(0, inplace=True)

    st.subheader("Player Projections")
    st.dataframe(df.sort_values("Projection", ascending=False))

    st.subheader("Optimized Lineup")
    lineup = optimize_lineup(df)
    st.dataframe(lineup[['Nickname', 'Salary', 'Projection']])

    total_salary = lineup['Salary'].sum()
    total_proj = lineup['Projection'].sum()
    st.write(f"**Total Salary:** ${total_salary}")
    st.write(f"**Total Projected Points:** {total_proj:.2f}")

else:
    st.info("Please upload your FanDuel golf CSV file to get started.")
