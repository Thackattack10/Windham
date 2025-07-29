import streamlit as st
import pandas as pd
from projections import project_golf_points
from optimizer import optimize_lineup

# 🌱 --- Custom CSS: Retro Background + Grass Title ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Luckiest+Guy&display=swap');

    body, .stApp {
        background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%);
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

# 🌱 --- Big Green Grass Title ---
st.markdown('<h1 class="grass-title">⛳️ Mikey\'s Golf Optimizer</h1>', unsafe_allow_html=True)

# 📤 Upload CSV
salary_file = st.file_uploader("Upload FanDuel Golf CSV", type="csv")

if salary_file:
    try:
        df = pd.read_csv(salary_file)
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        st.stop()

    required_columns = ['Nickname', 'Salary']
    if not all(col in df.columns for col in required_columns):
        st.error(f"CSV must contain columns: {',
