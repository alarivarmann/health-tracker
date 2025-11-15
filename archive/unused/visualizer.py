#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

DATA_FILE = Path(__file__).parent / 'metrics_log.csv'

st.set_page_config(page_title="Metrics Dashboard", page_icon="📊", layout="wide")

st.markdown('''<style>
.main{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%)}
.stMetric{background-color:white;padding:20px;border-radius:10px;box-shadow:0 4px 6px rgba(0,0,0,0.1)}
h1{color:white;text-shadow:2px 2px 4px rgba(0,0,0,0.3)}
.alert-high{background-color:#fee;border-left:4px solid #e74c3c;padding:15px;border-radius:5px;margin:10px 0}
.alert-medium{background-color:#fef9e7;border-left:4px solid #f39c12;padding:15px;border-radius:5px;margin:10px 0}
.alert-low{background-color:#eafaf1;border-left:4px solid #2ecc71;padding:15px;border-radius:5px;margin:10px 0}
</style>''', unsafe_allow_html=True)

@st.cache_data
def load_data():
    if not DATA_FILE.exists():
        return None
    df = pd.read_csv(DATA_FILE)
    df['date'] = pd.to_datetime(df['date'])
    return df

def calculate_trend(current, previous):
    if previous is None or pd.isna(previous):
        return 0, "→"
    change = current - previous
    if change > 0:
        return change, "↑"
    elif change < 0:
        return abs(change), "↓"
    else:
        return 0, "→"

def generate_insights(latest, previous=None):
    insights = []
    if latest['anxiety'] >= 7:
        insights.append(('high', '⚠️ High anxiety detected (≥7). Consider using nVNS + 10 min walk.'))
    if latest['project_chaos'] >= 7:
        insights.append(('high', '⚠️ High project chaos (≥7). Activate Anti-Chaos Routine and delivery_log.md.'))
    if latest['sleep_quality'] <= 4:
        insights.append(('high', '⚠️ Poor sleep quality (≤4). Review Sleep Recovery Plan.'))
    if latest['unwanted_meetings'] >= 6:
        insights.append(('medium', '⚡ Many unwanted meetings (≥6). Consider skip-meeting template.'))
    if latest['quiet_blocks'] <= 4:
        insights.append(('medium', '⚡ Low quiet work blocks (≤4). Protect your 2-hour deep work anchor.'))
    if latest['saying_no'] <= 4:
        insights.append(('medium', '⚡ Not saying "no" enough. Use TERP escalation for non-priority requests.'))
    if previous is not None:
        if latest['anxiety'] < previous['anxiety']:
            insights.append(('low', '✅ Anxiety decreased - great progress!'))
        if latest['sleep_quality'] > previous['sleep_quality']:
            insights.append(('low', '✅ Sleep quality improved!'))
        if latest['quiet_blocks'] > previous['quiet_blocks']:
            insights.append(('low', '✅ More quiet work blocks - deep work is working!'))
    if not insights:
        insights.append(('low', '✅ All metrics within healthy ranges. Keep it up!'))
    return insights

def main():
    st.title("📊 Work & Individual Metrics Dashboard")
    st.markdown("### Track your progress over time")
    df = load_data()
    if df is None or len(df) == 0:
        st.warning("No data yet. Run metrics-tracker.js to collect metrics.")
        st.stop()
    latest = df.iloc[-1]
    previous = df.iloc[-2] if len(df) > 1 else None
    st.sidebar.header("Filter Options")
    n_entries = st.sidebar.slider("Show last N entries", 1, len(df), min(10, len(df)))
    df_display = df.tail(n_entries)
    st.markdown("---")
    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        change, symbol = calculate_trend(latest['anxiety'], previous['anxiety'] if previous is not None else None)
        st.metric("Anxiety", f"{latest['anxiety']:.1f}", f"{symbol} {change:.1f}", delta_color="inverse")
    with col2:
        change, symbol = calculate_trend(latest['project_chaos'], previous['project_chaos'] if previous is not None else None)
        st.metric("Project Chaos", f"{latest['project_chaos']:.1f}", f"{symbol} {change:.1f}", delta_color="inverse")
    with col3:
        change, symbol = calculate_trend(latest['sleep_quality'], previous['sleep_quality'] if previous is not None else None)
        st.metric("Sleep Quality", f"{latest['sleep_quality']:.1f}", f"{symbol} {change:.1f}", delta_color="normal")
    with col4:
        change, symbol = calculate_trend(latest['quiet_blocks'], previous['quiet_blocks'] if previous is not None else None)
        st.metric("Quiet Work Blocks", f"{latest['quiet_blocks']:.1f}", f"{symbol} {change:.1f}", delta_color="normal")
    st.markdown("---")
    st.subheader("📈 Work Metrics Over Time")
    work_metrics = ['deadline_pressure', 'unmet_requests', 'project_chaos', 'unwanted_meetings']
    fig_work = go.Figure()
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe']
    for i, metric in enumerate(work_metrics):
        fig_work.add_trace(go.Scatter(x=df_display['date'], y=df_display[metric], name=metric.replace('_', ' ').title(), mode='lines+markers', line=dict(color=colors[i % len(colors)], width=3), marker=dict(size=8)))
    fig_work.update_layout(height=400, hovermode='x unified', plot_bgcolor='white', paper_bgcolor='white', yaxis=dict(range=[0, 10], title="Score (1-10)"), xaxis=dict(title="Date"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_work, use_container_width=True)
    st.subheader("🧘 Individual Metrics Over Time")
    individual_metrics = ['anxiety', 'irritability', 'sleep_quality', 'quiet_blocks']
    fig_individual = go.Figure()
    for i, metric in enumerate(individual_metrics):
        fig_individual.add_trace(go.Scatter(x=df_display['date'], y=df_display[metric], name=metric.replace('_', ' ').title(), mode='lines+markers', line=dict(color=colors[i % len(colors)], width=3), marker=dict(size=8)))
    fig_individual.update_layout(height=400, hovermode='x unified', plot_bgcolor='white', paper_bgcolor='white', yaxis=dict(range=[0, 10], title="Score (1-10)"), xaxis=dict(title="Date"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_individual, use_container_width=True)
    st.markdown("---")
    st.subheader("🎯 Key Insights & Recommendations")
    insights = generate_insights(latest, previous)
    for level, text in insights:
        if level == 'high':
            st.markdown(f'<div class="alert-high">{text}</div>', unsafe_allow_html=True)
        elif level == 'medium':
            st.markdown(f'<div class="alert-medium">{text}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-low">{text}</div>', unsafe_allow_html=True)
    with st.expander("📋 View Raw Data"):
        st.dataframe(df_display.sort_values('date', ascending=False), use_container_width=True)
    st.markdown("---")
    st.caption(f"Last updated: {latest['date'].strftime('%Y-%m-%d')} | Total entries: {len(df)}")

if __name__ == "__main__":
    main()
