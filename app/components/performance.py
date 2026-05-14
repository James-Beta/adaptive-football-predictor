import streamlit as st
import pandas as pd

@st.cache_data(ttl=60) # Only cache for 1 minute so it updates quickly during backtests
def load_logs():
    try:
        return pd.read_csv("logs/performance_log.csv")
    except FileNotFoundError:
        return pd.DataFrame()

def render_performance():
    st.header("Continuous Learning Tracker")
    
    df = load_logs()
    
    if df.empty:
        st.info("No performance logs found. Run a backtest or update the model.")
        return

    # Top-level metrics
    latest = df.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Accuracy (5W)", f"{latest.get('Rolling_Acc', 0)*100:.1f}%")
    col2.metric("Current Log Loss (5W)", f"{latest.get('Rolling_Loss', 0):.2f}")
    col3.metric("Latest Goals MAE", f"{latest.get('Goals_MAE', 0):.2f}")
    col4.metric("Total Matches Learned", f"{df['Matches'].sum()}")

    # Charts
    st.subheader("Rolling Accuracy & Log Loss")
    if 'Rolling_Acc' in df.columns and 'Rolling_Loss' in df.columns:
        chart_data = df[['Gameweek', 'Rolling_Acc', 'Rolling_Loss']].set_index('Gameweek')
        
        c1, c2 = st.columns(2)
        with c1:
            st.line_chart(chart_data['Rolling_Acc'], color="#00ff00") 
        with c2:
            st.line_chart(chart_data['Rolling_Loss'], color="#ff0000") 

    with st.expander("View Raw Performance Logs"):
        st.dataframe(df, hide_index=True)