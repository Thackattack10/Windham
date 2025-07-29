from projections import project_golf_points
from optimizer import optimize_golf_lineup
import streamlit as st
import pandas as pd

# --- 🎨 Retro Golf Style + Background ---
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.7),rgba(0,0,0,0.7)),
                    url("https://cdn.pixabay.com/photo/2017/06/02/18/24/golf-2374814_1280.jpg");
        background-size: cover;
        background-position: center;
        font-family: 'Press Start 2P', monospace;
        color: #00ffff;
    }}

    h1.neon-title {{
        font-size: 2.5rem;
        text-align: center;
        color: #00ccff;
        text-shadow:
            0 0 5px #00ccff,
            0 0 10px #00ccff,
            0 0 20px #00ccff,
            0 0 40px #00ccff,
            0 0 80px #00ccff;
        animation: flicker 1.8s infinite alternate;
        margin-bottom: 2rem;
    }}

    .stButton button {{
        background-color: #00ccff;
        color: black;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 20px;
        border: 2px solid #00ffff;
        box-shadow: 0 0 10px #00ccff;
    }}

    .stDataFrame, .stTable {{
        background-color: rgba(0,0,0,0.85);
        color: #00ffff;
        font-size: 10px;
    }}

    @keyframes flicker {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.8; }}
        100% {{ opacity: 1; }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- 🏌️‍♂️ Neon Title ---
st.markdown('<h1 class="neon-title">⛳ Mikey\'s Golf DFS Optimizer ⛳</h1>', unsafe_allow_html=True)

# --- Upload PGA DFS CSV ---
salary_file = st.file_uploader("Upload FanDuel Golf CSV", type="csv")

if salary_file:
    try:
        df = pd.read_csv(salary_file)
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        st.stop()

    required_columns = ['Nickname','Salary','Course']
    if not all(col in df.columns for col in required_columns):
        st.error(f"Missing columns: {', '.join(required_columns)}")
        st.stop()

    # Add or calculate stats
    df['Driving'] = df.get('Driving', 0)
    df['Putting'] = df.get('Putting', 0)
    df['RecentForm'] = df.get('RecentForm', 0)

    # Project points
    df['Projection'] = df.apply(project_golf_points, axis=1)
    df['Projection'].fillna(0, inplace=True)

    st.subheader("📊 Player Projections")
    st.dataframe(df.sort_values('Projection', ascending=False))

    # Optimize lineup
    st.subheader("🧮 Optimized Golf Lineup")
    lineup = optimize_golf_lineup(df)
    st.dataframe(lineup[['Nickname','Course','Salary','Projection']])

    total_salary = lineup['Salary'].sum()
    total_projection = lineup['Projection'].sum()
    st.write(f"**Total Salary:** ${total_salary}")
    st.write(f"**Total Projected Points:** {total_projection:.2f}")

else:
    st.info("Please upload a FanDuel golf salary CSV file to get started.")
