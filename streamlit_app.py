import streamlit as st
import pandas as pd
from projections import project_golf_points_factory
from optimizer import optimize_lineup
from sklearn.preprocessing import MinMaxScaler

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

# --- Sidebar sliders for projection weights ---
st.sidebar.subheader("📊 Projection Weights")
driving_weight = st.sidebar.slider("Driving Weight", 0.0, 1.0, 0.4)
putting_weight = st.sidebar.slider("Putting Weight", 0.0, 1.0, 0.5)
form_weight = st.sidebar.slider("Recent Form Weight", 0.0, 1.0, 0.3)

# --- Upload CSV ---
salary_file = st.file_uploader("Upload FanDuel Golf CSV", type="csv")

if salary_file:
    try:
        df = pd.read_csv(salary_file)
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        st.stop()

    # Validate required columns
    required_columns = ['Nickname', 'Salary', 'Driving', 'Putting', 'RecentForm']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
        st.stop()

    # Normalize stats
    scaler = MinMaxScaler()
    df[['Driving', 'Putting', 'RecentForm']] = scaler.fit_transform(df[['Driving', 'Putting', 'RecentForm']])

    # Create projection function with user weights
    projector = project_golf_points_factory(driving_weight, putting_weight, form_weight)
    df['ProjectedPoints'] = df.apply(projector, axis=1)

    # --- Filter and player selection UI ---
    st.subheader("🔍 Filter & Customize Your Pool")

    with st.expander("📋 View Full Player Pool"):
        st.dataframe(df[['Nickname', 'Salary', 'Driving', 'Putting', 'RecentForm', 'ProjectedPoints']].sort_values(by='ProjectedPoints', ascending=False))

    # Lock players
    locked_players = st.multiselect("🔒 Lock In Specific Players", options=df['Nickname'].tolist())

    # Exclude players
    excluded_players = st.multiselect("🚫 Exclude These Players", options=df['Nickname'].tolist())

    # Filter out excluded players
    filtered_df = df[~df['Nickname'].isin(excluded_players)].copy()
    filtered_df['Locked'] = filtered_df['Nickname'].isin(locked_players)

    # --- Run optimizer ---
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
    st.info("Please upload a FanDuel CSV file to start.")
