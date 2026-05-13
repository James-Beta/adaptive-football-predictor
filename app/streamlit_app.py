import streamlit as st

# We import the rendering functions from our other modules
from components.predictions import render_predictions
from components.fixtures import render_fixtures
from components.team_stats import render_team_stats
from components.performance import render_performance

# Must be the first Streamlit command
st.set_page_config(page_title="Football Predictor", page_icon="⚽", layout="wide")

def main():
    st.sidebar.title("⚽ Navigation")
    
    # The sidebar navigation menu
    page = st.sidebar.radio(
        "Go to", 
        ["🔮 Live Predictions", "📅 Raw Fixtures", "📊 Team Form (Metrics)", "📈 AI Performance"]
    )

    # Route to the correct module based on selection
    if page == "🔮 Live Predictions":
        render_predictions()
    elif page == "📅 Raw Fixtures":
        render_fixtures()
    elif page == "📊 Team Form (Metrics)":
        render_team_stats()
    elif page == "📈 AI Performance":
        render_performance()

if __name__ == "__main__":
    main()