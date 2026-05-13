import streamlit as st
import pandas as pd
from pathlib import Path

@st.cache_data(ttl=3600)
def load_predictions():
    try:
        return pd.read_csv("data/processed/upcoming_predictions.csv")
    except FileNotFoundError:
        return pd.DataFrame()

def render_predictions():
    st.header("🔮 This Weekend's Predictions")
    
    df = load_predictions()
    
    if df.empty:
        st.info("No predictions found. Run `python run_live_predictions.py` to generate them.")
        return

    st.dataframe(
        df[['Date', 'HomeTeam', 'AwayTeam', 'Prob_Home', 'Prob_Draw', 'Prob_Away', 'Expected_Total_Goals', 'Predicted_Result']],
        column_config={
            "Prob_Home": st.column_config.ProgressColumn("Home Win %", format="%.2f", min_value=0, max_value=1),
            "Prob_Draw": st.column_config.ProgressColumn("Draw %", format="%.2f", min_value=0, max_value=1),
            "Prob_Away": st.column_config.ProgressColumn("Away Win %", format="%.2f", min_value=0, max_value=1),
            "Expected_Total_Goals": st.column_config.NumberColumn("Exp. Goals", format="%.2f")
        },
        hide_index=True,
        width='stretch'
    )