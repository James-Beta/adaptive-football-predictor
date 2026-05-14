import streamlit as st
import pandas as pd

@st.cache_data(ttl=3600)
def load_team_metrics():
    try:
        return pd.read_parquet("data/processed/team_metrics.parquet")
    except FileNotFoundError:
        return pd.DataFrame()

def render_team_stats():
    st.header("📊 Team Form & Rolling Metrics")
    
    df = load_team_metrics()
    
    if df.empty:
        st.info("No metrics found. Run the data pipeline first.")
        return

    # Assuming your metrics file has a 'Team' column. Adjust if it is named differently!
    if 'team' in df.columns:
        teams = sorted(df['team'].unique())
        selected_team = st.selectbox("Search for a Team:", teams)
        
        # Filter and show only the most recent 10 records for that team
        team_df = df[df['team'] == selected_team].head(10)
        st.dataframe(team_df, hide_index=True, width='stretch')
    else:
        st.dataframe(df.tail(100), hide_index=True, width='stretch')