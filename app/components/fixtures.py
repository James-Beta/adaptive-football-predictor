import json

import streamlit as st
import pandas as pd

@st.cache_data(ttl=3600)
def load_fixtures():
    try:
        return pd.read_parquet("data/processed/fixtures.parquet")
    except FileNotFoundError:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_fixtures_meta():
    try:
        with open("data/processed/fixtures_meta.json", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}

def render_fixtures():
    st.header("📅 Raw Upcoming Fixtures")
    
    df = load_fixtures()
    
    if df.empty:
        st.info("No fixtures found. Run the data pipeline first.")
        return
        
    meta = load_fixtures_meta()
    if meta.get('generated_at'):
        fetched = pd.to_datetime(meta['generated_at'], errors='coerce', utc=True)
        stamp = fetched.strftime('%Y-%m-%d %H:%M UTC') if pd.notna(fetched) else meta['generated_at']
        with_odds = meta.get('with_odds')
        odds_note = f" · {with_odds} with complete odds" if with_odds is not None else ""
        st.caption(f"Last successful fixture fetch: {stamp} · {meta.get('row_count', len(df))} fixtures{odds_note}")

    st.dataframe(df, hide_index=True, width='stretch')