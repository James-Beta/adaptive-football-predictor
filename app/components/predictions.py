import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

@st.cache_data(ttl=3600)
def load_data():
    try:
        preds = pd.read_csv("data/processed/upcoming_predictions.csv")
        # We also need the metrics to draw the chart!
        metrics = pd.read_parquet("data/processed/team_metrics.parquet")
        return preds, metrics
    except FileNotFoundError:
        return pd.DataFrame(), pd.DataFrame()

def create_radar_chart(home_team, away_team, metrics_df):
    """Generates an interactive Head-to-Head Radar Chart with 0-100 Scaling"""
    
    home_stats = metrics_df[metrics_df['team'] == home_team].iloc[-1]
    away_stats = metrics_df[metrics_df['team'] == away_team].iloc[-1]

    # Define our stats, and explicitly mark which ones are "Bad" (where lower is better)
    stat_configs = [
        {'label': 'Goals', 'key': 'att_goals_scored', 'invert': False},
        {'label': 'Conversion', 'key': 'att_conversion_rate', 'invert': False},
        {'label': 'Conceded', 'key': 'def_goals_conceded', 'invert': True}, # Bad stat
        {'label': 'Pressure', 'key': 'def_pressure_allowed', 'invert': True}, # Bad stat
        {'label': 'Fouls', 'key': 'def_discipline_fouls', 'invert': True} # Bad stat
    ]
    
    categories = [cfg['label'] for cfg in stat_configs]
    
    home_scaled, home_raw = [], []
    away_scaled, away_raw = [], []

    # Calculate the 0-100 Strength Scores dynamically
    try:
        for cfg in stat_configs:
            col_min = metrics_df[cfg['key']].min()
            col_max = metrics_df[cfg['key']].max()
            
            # Helper to calculate the 0-100 score
            def get_score(val):
                if col_max == col_min: return 50.0
                score = ((val - col_min) / (col_max - col_min)) * 100
                return 100 - score if cfg['invert'] else score

            h_val = home_stats.get(cfg['key'], 0)
            a_val = away_stats.get(cfg['key'], 0)

            # Store the 0-100 score for plotting
            home_scaled.append(get_score(h_val))
            away_scaled.append(get_score(a_val))
            
            # Store the raw number for the hover tooltip (rounded for cleanliness)
            home_raw.append(f"{h_val:.2f}")
            away_raw.append(f"{a_val:.2f}")

    except Exception as e:
        st.error(f"Error mapping columns: {e}")
        return go.Figure()

    # Close the loop for Plotly
    categories.append(categories[0])
    home_scaled.append(home_scaled[0])
    away_scaled.append(away_scaled[0])
    home_raw.append(home_raw[0])
    away_raw.append(away_raw[0])

    fig = go.Figure()

    # Home Team Trace
    fig.add_trace(go.Scatterpolar(
        r=home_scaled,
        theta=categories,
        fill='toself',
        name=home_team,
        line_color='#1f77b4',
        opacity=0.8,
        text=home_raw, # Pass the raw numbers
        hoverinfo="name+theta+text" # Show the raw numbers on hover!
    ))

    # Away Team Trace
    fig.add_trace(go.Scatterpolar(
        r=away_scaled,
        theta=categories,
        fill='toself',
        name=away_team,
        line_color='#d62728',
        opacity=0.7,
        text=away_raw,
        hoverinfo="name+theta+text"
    ))

    # Clean, Normalized Layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 100], # The scale is now permanently locked 0-100!
                showticklabels=False, 
                gridcolor="rgba(255,255,255,0.1)" 
            ),
            angularaxis=dict(
                gridcolor="rgba(255,255,255,0.1)",
                tickfont=dict(size=14, color="white") 
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        showlegend=True,
        title=dict(text=f"Tactical Matchup (Strength Scores 0-100)", font=dict(size=20, color="white")),
        margin=dict(t=80, b=40, l=40, r=40),
        paper_bgcolor="#1E1E1E", 
        font=dict(color="white") 
    )
    
    return fig

    # Plotly requires the loop to be "closed" by repeating the first value at the end
    categories.append(categories[0])
    home_values.append(home_values[0])
    away_values.append(away_values[0])

    fig = go.Figure()

    # Add Home Team Polygon (Blue)
    fig.add_trace(go.Scatterpolar(
        r=home_values,
        theta=categories,
        fill='toself',
        name=home_team,
        line_color='#1f77b4',
        opacity=0.8
    ))

    # Add Away Team Polygon (Red)
    fig.add_trace(go.Scatterpolar(
        r=away_values,
        theta=categories,
        fill='toself',
        name=away_team,
        line_color='#d62728',
        opacity=0.7
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max(max(home_values), max(away_values)) * 1.2])),
        showlegend=True,
        title=dict(text=f"Tactical Matchup: {home_team} vs {away_team}", font=dict(size=20)),
        margin=dict(t=80, b=40, l=40, r=40)
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, max(max(home_values), max(away_values)) * 1.2],
                showticklabels=False, # Hides the messy numbers on the web
                gridcolor="rgba(0,0,0,0.1)" # Faint spiderweb lines
            ),
            angularaxis=dict(
                gridcolor="rgba(0,0,0,0.1)",
                tickfont=dict(size=14, color="white") # Makes your simple words pop!
            ),
            bgcolor="rgba(0,0,0,0)" # Transparent background
        ),
        showlegend=True,
        title=dict(text=f"Tactical Matchup: {home_team} vs {away_team}", font=dict(size=20)),
        margin=dict(t=80, b=40, l=40, r=40),
        paper_bgcolor="#1E1E1E" # Dark mode background like professional analytics
    )
    
    return fig

def render_predictions():
    st.header("🔮 This Weekend's Predictions")
    
    preds_df, metrics_df = load_data()
    
    if preds_df.empty:
        st.info("No predictions found. Run `python run_live_predictions.py` to generate them.")
        return

    # 1. Show the Probability Table
    st.dataframe(
        preds_df[['Date', 'HomeTeam', 'AwayTeam', 'Prob_Home', 'Prob_Draw', 'Prob_Away', 'Expected_Total_Goals']],
        column_config={
            "Prob_Home": st.column_config.ProgressColumn("Home Win %", format="%.2f", min_value=0, max_value=1),
            "Prob_Draw": st.column_config.ProgressColumn("Draw %", format="%.2f", min_value=0, max_value=1),
            "Prob_Away": st.column_config.ProgressColumn("Away Win %", format="%.2f", min_value=0, max_value=1),
            "Expected_Total_Goals": st.column_config.NumberColumn("Exp. Goals", format="%.2f")
        },
        hide_index=True,
        width='stretch'
    )

    st.divider()

    # 2. The Interactive Head-to-Head Radar Chart
    if not metrics_df.empty:
        st.subheader("🕸️ Matchup Analyzer")
        
        # Create a dropdown to select a specific match
        match_options = preds_df.apply(lambda row: f"{row['HomeTeam']} vs {row['AwayTeam']}", axis=1).tolist()
        selected_match = st.selectbox("Select a match to view the tactical matchup:", match_options)
        
        if selected_match:
            # Extract the team names from the dropdown selection
            home_team, away_team = selected_match.split(" vs ")
            
            # Generate and display the Plotly Radar Chart
            radar_fig = create_radar_chart(home_team, away_team, metrics_df)
            st.plotly_chart(radar_fig, width='stretch')