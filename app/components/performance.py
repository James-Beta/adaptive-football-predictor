import streamlit as st
import pandas as pd

@st.cache_data(ttl=60)  # short cache so a fresh retrain shows up quickly
def load_logs():
    try:
        return pd.read_csv("logs/performance_log.csv")
    except FileNotFoundError:
        return pd.DataFrame()

def render_performance():
    st.header("Model Performance")

    df = load_logs()

    if df.empty:
        st.info("No performance logs found. Run the pipeline to train/evaluate the model at least once.")
        return

    # Top-level metrics from the most recent evaluate() call
    latest = df.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Latest Accuracy", f"{latest.get('Accuracy', 0) * 100:.1f}%")
    col2.metric("Latest Log Loss", f"{latest.get('Log_Loss', 0):.3f}")
    if 'Goals_MAE' in df.columns and pd.notnull(latest.get('Goals_MAE')):
        col3.metric("Latest Goals MAE", f"{latest.get('Goals_MAE', 0):.2f}")
    col4.metric("Matches Evaluated (Latest Run)", f"{int(latest.get('Matches', 0))}")

    # Simple trend across successive evaluate() calls — one point per run,
    # no rolling window or gameweek concept.
    st.subheader("Accuracy & Log Loss Across Runs")
    if {'Accuracy', 'Log_Loss'}.issubset(df.columns):
        chart_data = df[['Accuracy', 'Log_Loss']].copy()
        chart_data.index.name = 'Run'
        c1, c2 = st.columns(2)
        with c1:
            st.line_chart(chart_data['Accuracy'])
        with c2:
            st.line_chart(chart_data['Log_Loss'])

    with st.expander("View Raw Performance Log"):
        st.dataframe(df, hide_index=True, width='stretch')