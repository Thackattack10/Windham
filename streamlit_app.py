import streamlit as st
import pandas as pd
from projections import project_golf_points
from optimizer import optimize_lineup

# --- Custom CSS and Title here (omitted for brevity) ---

# --- Upload FanDuel CSV ---
salary_file = st.file_uploader("Upload FanDuel Golf CSV", type="csv")
# --- Upload Strokes Gained Putting CSV ---
putting_file = st.file_uploader("Upload Strokes Gained Putting CSV", type="csv")

if salary_file and putting_file:
    try:
        df = pd.read_csv(salary_file)
    except Exception as e:
        st.error(f"Error loading FanDuel CSV file: {e}")
        st.stop()

    try:
        putting_df = pd.read_csv(putting_file)
    except Exception as e:
        st.error(f"Error loading Putting CSV file: {e}")
        st.stop()

    # Check required columns FanDuel CSV
    required_fd_cols = ['First Name', 'Last Name', 'Nickname', 'Salary', 'FPPG']
    missing_fd_cols = [col for col in required_fd_cols if col not in df.columns]
    if missing_fd_cols:
        st.error(f"Missing columns in FanDuel CSV: {missing_fd_cols}")
        st.stop()

    # Check required columns Putting CSV
    if 'PLAYER' not in putting_df.columns or 'AVG' not in putting_df.columns:
        st.error("Putting CSV must have columns 'PLAYER' and 'AVG'")
        st.stop()

    # Normalize names for merge
    putting_df['FullName'] = putting_df['PLAYER'].str.strip().str.lower()
    df['FullName'] = (df['First Name'] + ' ' + df['Last Name']).str.strip().str.lower()

    # Merge strokes gained putting AVG into FanDuel df
    df = pd.merge(df, putting_df[['FullName', 'AVG']], on='FullName', how='left')

    # Rename AVG column to SG_Putting
    df.rename(columns={'AVG': 'SG_Putting'}, inplace=True)

    # Fill missing SG_Putting values with 0
    df['SG_Putting'] = df['SG_Putting'].fillna(0)

    # Apply projection function
    df['ProjectedPoints'] = df.apply(project_golf_points, axis=1)

    # Show merged sample for debug
    st.subheader("Player Projections Sample")
    st.dataframe(df[['FullName', 'Salary', 'FPPG', 'SG_Putting', 'ProjectedPoints']].head(10))

    # Lock/Exclude player widgets
    locked_players = st.multiselect("🔒 Lock In Specific Players", options=df['FullName'].tolist())
    excluded_players = st.multiselect("🚫 Exclude These Players", options=df['FullName'].tolist())

    filtered_df = df[~df['FullName'].isin(excluded_players)].copy()
    filtered_df['Locked'] = filtered_df['FullName'].isin(locked_players)

    # Optimize lineup button
    st.subheader("🎯 Optimize Your Lineup")
    if st.button("Run Optimizer"):
        try:
            lineup = optimize_lineup(filtered_df)
            st.success("✅ Optimized lineup found!")
            st.dataframe(lineup[['FullName', 'Salary', 'ProjectedPoints']].reset_index(drop=True))
            st.write(f"💰 Total Salary: {lineup['Salary'].sum()}")
            st.write(f"📈 Projected Points: {lineup['ProjectedPoints'].sum():.2f}")
        except ValueError as ve:
            st.error(str(ve))

else:
    st.info("Please upload both FanDuel CSV and Strokes Gained Putting CSV files to start.")
