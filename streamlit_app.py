import streamlit as st
import pandas as pd
from projections import project_golf_points
from optimizer import optimize_lineup

# -- Title --
st.markdown("<h1 style='text-align: center;'>⛳️ Mikey's Golf Optimizer</h1>", unsafe_allow_html=True)

# -- Upload CSVs --
col1, col2, col3, col4 = st.columns(4)

with col1:
    fanduel_file = st.file_uploader("📤 FanDuel CSV", type="csv")
with col2:
    putting_file = st.file_uploader("📤 SG Putting CSV", type="csv")
with col3:
    approach_file = st.file_uploader("📤 SG Approach CSV", type="csv")
with col4:
    ott_file = st.file_uploader("📤 SG Off-the-Tee CSV", type="csv")

# -- Load and Merge --
if fanduel_file and putting_file and approach_file and ott_file:
    try:
        df_fd = pd.read_csv(fanduel_file)
        df_putting = pd.read_csv(putting_file)
        df_approach = pd.read_csv(approach_file)
        df_ott = pd.read_csv(ott_file)

        df_fd['PLAYER'] = df_fd['Nickname'].str.strip().str.lower()
        df_putting['PLAYER'] = df_putting['PLAYER'].str.strip().str.lower()
        df_approach['PLAYER'] = df_approach['PLAYER'].str.strip().str.lower()
        df_ott['PLAYER'] = df_ott['PLAYER'].str.strip().str.lower()

        df = df_fd.copy()
        df = pd.merge(df, df_putting[['PLAYER', 'AVG']], on='PLAYER', how='left')
        df.rename(columns={'AVG': 'SG_Putting'}, inplace=True)
        df = pd.merge(df, df_approach[['PLAYER', 'AVG']], on='PLAYER', how='left')
        df.rename(columns={'AVG': 'SG_APP'}, inplace=True)
        df = pd.merge(df, df_ott[['PLAYER', 'AVG']], on='PLAYER', how='left')
        df.rename(columns={'AVG': 'SG_OTT'}, inplace=True)

        for col in ['SG_Putting', 'SG_APP', 'SG_OTT']:
            df[col] = df[col].fillna(0)

        df['ProjectedPoints'] = df.apply(project_golf_points, axis=1)

        st.subheader("📋 Player Pool")
        st.dataframe(df[['Nickname', 'Salary', 'FPPG', 'SG_Putting', 'SG_APP', 'SG_OTT', 'ProjectedPoints']])

        # Locks and Excludes
        locked = st.multiselect("🔒 Lock Players", df['Nickname'].tolist())
        excluded = st.multiselect("🚫 Exclude Players", df['Nickname'].tolist())

        df_filtered = df[~df['Nickname'].isin(excluded)].copy()
        df_filtered['Locked'] = df_filtered['Nickname'].isin(locked)

        st.subheader("🎯 Optimize Your Lineup")
        if st.button("Run Optimizer"):
            st.write("🔄 Optimizer started...")
            try:
                lineup = optimize_lineup(df_filtered, salary_cap=60000, lineup_size=6)
                st.success("✅ Optimized Lineup")
                st.dataframe(lineup[['Nickname', 'Salary', 'ProjectedPoints', 'SG_Putting', 'SG_APP', 'SG_OTT']])
                st.write(f"💰 Total Salary: {lineup['Salary'].sum()}")
                st.write(f"📈 Projected Points: {lineup['ProjectedPoints'].sum():.2f}")
            except Exception as e:
                st.error(f"🚨 Error: {e}")
                import traceback
                st.text(traceback.format_exc())

    except Exception as e:
        st.error(f"File processing error: {e}")
