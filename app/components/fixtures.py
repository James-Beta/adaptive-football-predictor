import streamlit as st
import pandas as pd

@st.cache_data(ttl=3600)
def load_fixtures():
    try:
        return pd.read_parquet("data/processed/fixtures.parquet")
    except FileNotFoundError:
        return pd.DataFrame()

def render_fixtures():
    st.header("📅 Raw Upcoming Fixtures")
    
    df = load_fixtures()
    
    if df.empty:
        st.info("No fixtures found. Run the data pipeline first.")
        return
        
    st.dataframe(df, hide_index=True, width='stretch')