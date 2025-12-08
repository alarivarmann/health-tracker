#!/usr/bin/env python3
"""
Metrics Tracker - Main Streamlit App (Modular Version)
Uses story-based narratives with feedback loop
"""

import math
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from modules.auth import require_app_password


def normalize_date_value(date_value):
    """Normalize any stored date value into YYYY-MM-DD string."""
    if date_value is None:
        return None

    if isinstance(date_value, pd.Timestamp):
        return date_value.strftime('%Y-%m-%d')

    if isinstance(date_value, datetime):
        return date_value.strftime('%Y-%m-%d')

    date_str = str(date_value).strip()
    if not date_str or date_str.lower() in {'none', 'nan'}:
        return None

    try:
        parsed = pd.to_datetime(date_str)
        if pd.isna(parsed):
            return date_str
        return parsed.strftime('%Y-%m-%d')
    except Exception:
        return date_str

# Import our modules
from modules.config import QUESTIONS
from modules.data import (
    load_data, save_entry, get_previous_entry,
    should_prompt_today, get_metric_changes
)
from modules.analysis import analyze_with_narrative, update_narrative_with_feedback
from modules.insights import generate_quick_insights, should_recommend_delivery_log
from modules.severity import analyze_metrics_severity, get_top_issues, calculate_severity_statistics

# Page config
st.set_page_config(
    page_title="Metrics Tracker",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
    .stMetric {background-color: white;padding: 20px;border-radius: 10px;box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    h1, h2, h3 {color: white;text-shadow: 2px 2px 4px rgba(0,0,0,0.3);}
    .alert-high {background-color: #fee;border-left: 4px solid #e74c3c;padding: 15px;border-radius: 5px;margin: 10px 0;}
    .alert-medium {background-color: #fef9e7;border-left: 4px solid #f39c12;padding: 15px;border-radius: 5px;margin: 10px 0;}
    .alert-low {background-color: #eafaf1;border-left: 4px solid #2ecc71;padding: 15px;border-radius: 5px;margin: 10px 0;}
    .prompt-banner {background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);color: white;padding: 20px;border-radius: 10px;text-align: center;font-size: 1.2em;margin-bottom: 20px;}
    .narrative-box {background: white;padding: 25px;border-radius: 15px;box-shadow: 0 5px 20px rgba(0,0,0,0.1);margin: 20px 0;}
    .feedback-box {background: #f8f9fa;padding: 20px;border-radius: 10px;border-left: 4px solid #667eea;margin-top: 20px;}
</style>
""", unsafe_allow_html=True)

def main():
    require_app_password()
    st.title("📊 Work & Individual Metrics Tracker")
    
    # Initialize session state for thresholds (from .env as defaults)
    if 'config_thresholds' not in st.session_state:
        from modules.config import THRESHOLDS, ANTHROPIC_API_KEY
        # Default mode: Free if no API key, Claude AI if key exists
        default_mode = 'Claude AI' if (ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != 'your_key_here') else 'Free'
        
        st.session_state.config_thresholds = {
            'mode': default_mode,
            'claude_model': 'claude-3-5-haiku-20241022',  # Default to cheapest model
            'problem_threshold': 6,
            'increase_threshold': 1.0,
            'signal_body_tension_high': THRESHOLDS.get('signal_body_tension_high', 3),
            'signal_mind_noise_high': THRESHOLDS.get('signal_mind_noise_high', 3),
            'signal_focus_friction_high': THRESHOLDS.get('signal_focus_friction_high', 3),
            'signal_emotion_wave_high': THRESHOLDS.get('signal_emotion_wave_high', 3),
            'signal_energy_drain_high': THRESHOLDS.get('signal_energy_drain_high', 3),
            'flag_rushing_loop_high': THRESHOLDS.get('flag_rushing_loop_high', 1),
            'flag_skipped_reset_high': THRESHOLDS.get('flag_skipped_reset_high', 1),
            'flag_people_pleasing_high': THRESHOLDS.get('flag_people_pleasing_high', 1),
            'anxiety_high': THRESHOLDS.get('anxiety_high', 7),
            'anxiety_medium': THRESHOLDS.get('anxiety_medium', 5),
            'irritability_high': THRESHOLDS.get('irritability_high', 7),
            'sleep_issues_high': THRESHOLDS.get('sleep_issues_high', 7),
            'project_chaos_high': THRESHOLDS.get('project_chaos_high', 7),
            'unwanted_meetings_high': THRESHOLDS.get('unwanted_meetings_high', 6),
            'quiet_blocks_insufficient_high': THRESHOLDS.get('quiet_blocks_insufficient_high', 7),
            'cannot_say_no_high': THRESHOLDS.get('cannot_say_no_high', 7),
            'unmet_requests_high': THRESHOLDS.get('unmet_requests_high', 7),
            'stress_outside_high': THRESHOLDS.get('stress_outside_high', 7),
            'jira_blocked_high': THRESHOLDS.get('jira_blocked_high', 7),
            'no_ownership_high': THRESHOLDS.get('no_ownership_high', 7),
            'urgent_alignment_high': THRESHOLDS.get('urgent_alignment_high', 7),
            'self_development_unrealized_high': THRESHOLDS.get('self_development_unrealized_high', 7),
            'deadline_pressure_high': THRESHOLDS.get('deadline_pressure_high', 7),
            'apologies_high': THRESHOLDS.get('apologies_high', 6)
        }
    
    # Reset all ADHD primary signal widgets to -NA on fresh app load
    if 'adhd_widgets_initialized' not in st.session_state:
        adhd_primary = [q for q in QUESTIONS if q.get('category') == 'adhd_primary']
        for question in adhd_primary:
            if question.get('type') == 'yesno':
                st.session_state[f"{question['key']}_required_yesno"] = '-NA'
            else:
                st.session_state[f"{question['key']}_required_slider"] = '-NA'
        st.session_state.adhd_widgets_initialized = True
    
    # Check if input needed
    needs_prompt, reason = should_prompt_today()
    
    # Tab navigation (New Entry first, Configuration last)
    tab_entry, tab_dashboard, tab_analysis, tab_about, tab_config = st.tabs([
        "📝 New Entry",
        "📊 Dashboard",
        "📖 Analysis",
        "ℹ️ About",
        "⚙️ Configuration"
    ])

    with tab_entry:
        show_input_tab(needs_prompt)

    with tab_dashboard:
        show_dashboard_tab()

    with tab_analysis:
        show_analysis_tab()

    with tab_about:
        show_about_tab()

    with tab_config:
        show_configuration_tab()

def show_configuration_tab():
    """Configuration Tab - Adjust thresholds in real-time"""
    from modules.config import THRESHOLDS, ANTHROPIC_API_KEY
    
    st.header("⚙️ Configuration")
    
    st.markdown("""
    **Adjust threshold parameters in real-time.** Changes apply immediately to your next analysis.
    The `.env` file provides starting values, but you can experiment here.
    """)
    
    # Mode Selection (Most Important Parameter)
    st.subheader("🤖 Analysis Mode")
    
    from modules.config import ANTHROPIC_API_KEY
    has_api_key = ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != 'your_key_here'
    
    mode_options = ['Free (Rule-based)', 'Claude AI (Paid)']
    current_mode_display = 'Free (Rule-based)' if st.session_state.config_thresholds['mode'] == 'Free' else 'Claude AI (Paid)'
    
    selected_mode = st.radio(
        "Select narrative generation method:",
        mode_options,
        index=mode_options.index(current_mode_display),
        help="**Free**: Rule-based narratives (no API costs) | **Claude AI**: Advanced AI narratives (requires API key)"
    )
    
    # Update session state
    st.session_state.config_thresholds['mode'] = 'Free' if selected_mode == 'Free (Rule-based)' else 'Claude AI'
    
    # Show API key status
    if st.session_state.config_thresholds['mode'] == 'Claude AI':
        if has_api_key:
            st.success("✅ Claude API key detected and configured")
            
            # Model Selection (only show when Claude AI mode is active)
            st.markdown("### 🎯 Claude Model Selection")
            
            from modules.analysis import get_available_claude_models
            models = get_available_claude_models()
            
            # Create model options for selectbox
            model_options = {m['name']: m['id'] for m in models}
            
            # Get current model or default
            current_model_id = st.session_state.config_thresholds.get('claude_model', 'claude-sonnet-4-20250514')
            current_model_name = next((m['name'] for m in models if m['id'] == current_model_id), models[0]['name'])
            
            selected_model_name = st.selectbox(
                "Choose Claude model:",
                options=list(model_options.keys()),
                index=list(model_options.keys()).index(current_model_name),
                help="Different models offer different trade-offs between cost, speed, and intelligence"
            )
            
            # Update session state
            st.session_state.config_thresholds['claude_model'] = model_options[selected_model_name]
            
            # Show model details
            selected_model = next(m for m in models if m['name'] == selected_model_name)
            
            col_desc1, col_desc2 = st.columns([1, 1])
            with col_desc1:
                st.info(f"**Use Case:** {selected_model['use_case']}")
            with col_desc2:
                st.caption(f"💰 **Pricing:** {selected_model['cost_detail']}")
            
            st.caption(f"ℹ️ {selected_model['description']}")
            st.caption(f"📊 **Cost Comparison:** {selected_model['cost_comparison']}")
            
        else:
            st.error("⚠️ Claude AI mode requires an API key in your `.env` file (ANTHROPIC_API_KEY)")
            st.info("💡 Switch to Free mode for cost-free operation with rule-based narratives")
    else:
        st.info("ℹ️ Free mode uses rule-based narrative generation (no API calls, no costs)")
    
    st.markdown("---")
    
    # Reset button
    col_reset1, col_reset2 = st.columns([3, 1])
    with col_reset2:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            # Reset to defaults but keep current mode
            default_mode = 'Claude AI' if has_api_key else 'Free'
            st.session_state.config_thresholds = {
                'mode': default_mode,
                'claude_model': 'claude-3-5-haiku-20241022',
                'problem_threshold': 6,
                'increase_threshold': 1.0,
                'signal_body_tension_high': THRESHOLDS.get('signal_body_tension_high', 3),
                'signal_mind_noise_high': THRESHOLDS.get('signal_mind_noise_high', 3),
                'signal_focus_friction_high': THRESHOLDS.get('signal_focus_friction_high', 3),
                'signal_emotion_wave_high': THRESHOLDS.get('signal_emotion_wave_high', 3),
                'signal_energy_drain_high': THRESHOLDS.get('signal_energy_drain_high', 3),
                'flag_rushing_loop_high': THRESHOLDS.get('flag_rushing_loop_high', 1),
                'flag_skipped_reset_high': THRESHOLDS.get('flag_skipped_reset_high', 1),
                'flag_people_pleasing_high': THRESHOLDS.get('flag_people_pleasing_high', 1),
                'anxiety_high': THRESHOLDS.get('anxiety_high', 7),
                'anxiety_medium': THRESHOLDS.get('anxiety_medium', 5),
                'irritability_high': THRESHOLDS.get('irritability_high', 7),
                'sleep_issues_high': THRESHOLDS.get('sleep_issues_high', 7),
                'project_chaos_high': THRESHOLDS.get('project_chaos_high', 7),
                'unwanted_meetings_high': THRESHOLDS.get('unwanted_meetings_high', 6),
                'quiet_blocks_insufficient_high': THRESHOLDS.get('quiet_blocks_insufficient_high', 7),
                'cannot_say_no_high': THRESHOLDS.get('cannot_say_no_high', 7),
                'unmet_requests_high': THRESHOLDS.get('unmet_requests_high', 7),
                'stress_outside_high': THRESHOLDS.get('stress_outside_high', 7),
                'jira_blocked_high': THRESHOLDS.get('jira_blocked_high', 7),
                'no_ownership_high': THRESHOLDS.get('no_ownership_high', 7),
                'urgent_alignment_high': THRESHOLDS.get('urgent_alignment_high', 7),
                'self_development_unrealized_high': THRESHOLDS.get('self_development_unrealized_high', 7),
                'deadline_pressure_high': THRESHOLDS.get('deadline_pressure_high', 7),
                'apologies_high': THRESHOLDS.get('apologies_high', 6)
            }
            st.success("✅ Reset to defaults from .env file")
            st.rerun()
    
    st.markdown("---")
    
    # Severity Classification Parameters
    st.subheader("🎯 Severity Classification Rules")
    st.markdown("**Core parameters** that determine how metrics are categorized:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.config_thresholds['problem_threshold'] = st.number_input(
            "Problem Threshold",
            min_value=1,
            max_value=10,
            value=st.session_state.config_thresholds['problem_threshold'],
            help="Values >= this are considered problematic",
            key="problem_threshold_input"
        )
        st.caption("Used to identify issues that need attention")
    
    with col2:
        st.session_state.config_thresholds['increase_threshold'] = st.number_input(
            "Increase Threshold",
            min_value=0.1,
            max_value=5.0,
            value=st.session_state.config_thresholds['increase_threshold'],
            step=0.1,
            help="Delta >= this is considered a significant increase",
            key="increase_threshold_input"
        )
        st.caption("Used to detect severity increases")
    
    st.markdown("---")
    
    # Alert Thresholds
    st.subheader("🚨 Alert Thresholds")
    st.markdown("**Individual metric thresholds** for quick alerts (adjust with sliders):")

    st.markdown("**ADHD Radar (0 = calm · 10 = red alert)**")
    adhd_col_left, adhd_col_right = st.columns(2)

    with adhd_col_left:
        st.session_state.config_thresholds['signal_body_tension_high'] = st.slider(
            "Body tension trigger",
            0, 10,
            st.session_state.config_thresholds['signal_body_tension_high'],
            key="signal_body_tension_high_slider"
        )
        st.session_state.config_thresholds['signal_focus_friction_high'] = st.slider(
            "Focus friction trigger",
            0, 10,
            st.session_state.config_thresholds['signal_focus_friction_high'],
            key="signal_focus_friction_high_slider"
        )
        st.session_state.config_thresholds['signal_energy_drain_high'] = st.slider(
            "Energy drain trigger",
            0, 10,
            st.session_state.config_thresholds['signal_energy_drain_high'],
            key="signal_energy_drain_high_slider"
        )

    with adhd_col_right:
        st.session_state.config_thresholds['signal_mind_noise_high'] = st.slider(
            "Mind noise trigger",
            0, 10,
            st.session_state.config_thresholds['signal_mind_noise_high'],
            key="signal_mind_noise_high_slider"
        )
        st.session_state.config_thresholds['signal_emotion_wave_high'] = st.slider(
            "Emotion swell trigger",
            0, 10,
            st.session_state.config_thresholds['signal_emotion_wave_high'],
            key="signal_emotion_wave_high_slider"
        )

        def toggle_flag_threshold(session_key: str, label: str) -> int:
            current_value = st.session_state.config_thresholds[session_key]
            options = [
                (0, "Ignore flag (>= 0)"),
                (1, "Trigger when marked 'Yes' (>= 1)")
            ]
            option_values = [opt[0] for opt in options]
            option_labels = [opt[1] for opt in options]
            selected_index = option_values.index(current_value) if current_value in option_values else 1
            selection_label = st.selectbox(
                label,
                options=option_labels,
                index=selected_index,
                key=f"{session_key}_select"
            )
            selected_value = option_values[option_labels.index(selection_label)]
            return int(selected_value)

        st.session_state.config_thresholds['flag_rushing_loop_high'] = toggle_flag_threshold(
            'flag_rushing_loop_high',
            "Rushing loop triggers when"
        )
        st.session_state.config_thresholds['flag_skipped_reset_high'] = toggle_flag_threshold(
            'flag_skipped_reset_high',
            "Skipped reset triggers when"
        )
        st.session_state.config_thresholds['flag_people_pleasing_high'] = toggle_flag_threshold(
            'flag_people_pleasing_high',
            "People-pleasing triggers when"
        )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Work Metrics**")
        st.session_state.config_thresholds['project_chaos_high'] = st.slider(
            "Project Chaos (High)",
            1, 10,
            st.session_state.config_thresholds['project_chaos_high'],
            key="project_chaos_high_slider"
        )
        st.session_state.config_thresholds['unwanted_meetings_high'] = st.slider(
            "Unwanted Meetings (High)",
            1, 10,
            st.session_state.config_thresholds['unwanted_meetings_high'],
            key="unwanted_meetings_high_slider"
        )
        st.session_state.config_thresholds['unmet_requests_high'] = st.slider(
            "Unmet Requests (High)",
            1, 10,
            st.session_state.config_thresholds['unmet_requests_high'],
            key="unmet_requests_high_slider"
        )
        st.session_state.config_thresholds['jira_blocked_high'] = st.slider(
            "Jira Blocked (High)",
            1, 10,
            st.session_state.config_thresholds['jira_blocked_high'],
            key="jira_blocked_high_slider"
        )
        st.session_state.config_thresholds['deadline_pressure_high'] = st.slider(
            "Deadline Pressure (High)",
            1, 10,
            st.session_state.config_thresholds['deadline_pressure_high'],
            key="deadline_pressure_high_slider"
        )
        st.session_state.config_thresholds['apologies_high'] = st.slider(
            "Apologies (High)",
            1, 10,
            st.session_state.config_thresholds['apologies_high'],
            key="apologies_high_slider"
        )

    with col2:
        st.markdown("**Well-being Metrics**")
        st.session_state.config_thresholds['anxiety_high'] = st.slider(
            "Anxiety (High)",
            1, 10,
            st.session_state.config_thresholds['anxiety_high'],
            key="anxiety_high_slider"
        )
        st.session_state.config_thresholds['anxiety_medium'] = st.slider(
            "Anxiety (Medium)",
            1, 10,
            st.session_state.config_thresholds['anxiety_medium'],
            key="anxiety_medium_slider"
        )
        st.session_state.config_thresholds['irritability_high'] = st.slider(
            "Irritability (High)",
            1, 10,
            st.session_state.config_thresholds['irritability_high'],
            key="irritability_high_slider"
        )
        st.session_state.config_thresholds['stress_outside_high'] = st.slider(
            "Stress Outside Work (High)",
            1, 10,
            st.session_state.config_thresholds['stress_outside_high'],
            key="stress_outside_high_slider"
        )

    with col3:
        st.markdown("**Productivity Metrics**")
        st.session_state.config_thresholds['sleep_issues_high'] = st.slider(
            "Sleep Issues (High)",
            1, 10,
            st.session_state.config_thresholds['sleep_issues_high'],
            key="sleep_issues_high_slider"
        )
        st.session_state.config_thresholds['quiet_blocks_insufficient_high'] = st.slider(
            "Quiet Blocks Insufficient (High)",
            1, 10,
            st.session_state.config_thresholds['quiet_blocks_insufficient_high'],
            key="quiet_blocks_insufficient_high_slider"
        )
        st.session_state.config_thresholds['cannot_say_no_high'] = st.slider(
            "Cannot Say No (High)",
            1, 10,
            st.session_state.config_thresholds['cannot_say_no_high'],
            key="cannot_say_no_high_slider"
        )
        st.session_state.config_thresholds['no_ownership_high'] = st.slider(
            "No Ownership (High)",
            1, 10,
            st.session_state.config_thresholds['no_ownership_high'],
            key="no_ownership_high_slider"
        )
        st.session_state.config_thresholds['self_development_unrealized_high'] = st.slider(
            "Self-Development Unrealized (High)",
            1, 10,
            st.session_state.config_thresholds['self_development_unrealized_high'],
            key="self_development_unrealized_high_slider"
        )
        st.session_state.config_thresholds['urgent_alignment_high'] = st.slider(
            "Urgent Alignment (High)",
            1, 10,
            st.session_state.config_thresholds['urgent_alignment_high'],
            key="urgent_alignment_high_slider"
        )
    
    st.markdown("---")
    
    # Classification Logic Explanation
    st.subheader("📋 Classification Logic")
    
    with st.expander("How metrics are classified", expanded=False):
        problem_t = st.session_state.config_thresholds['problem_threshold']
        increase_t = st.session_state.config_thresholds['increase_threshold']
        
        st.markdown(f"""
        ### 🚨 Problem Severity Increase
        - Current value >= **{problem_t}** (Problem Threshold)
        - **AND** Delta >= **{increase_t}** (Increase Threshold)
        - **Result**: Red alert - rising problem needing immediate attention
        
        ### ⚠️ Continuous Issue
        - Current value >= **{problem_t}** (Problem Threshold)
        - **AND** Delta < **{increase_t}** (stable)
        - **Result**: Yellow alert - stuck at high value, needs monitoring
        
        ### ✅ Safe
        - Current value < **{problem_t}**
        - **OR** Not increasing significantly
        - **Result**: Green - no immediate action needed
        
        ### Severity Scoring
        - **Problem Severity Increase**: `current × 10 + delta × 5`
        - **Continuous Issue**: `current × 5`
        - **Safe**: `0`
        
        Higher scores appear first in the findings list.
        """)
    
    # API Configuration
    st.markdown("---")
    st.subheader("🔑 API Configuration")
    
    if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != 'your_key_here':
        st.success("✅ Anthropic API key configured")
        st.caption(f"Key: {ANTHROPIC_API_KEY[:8]}...{ANTHROPIC_API_KEY[-4:]}")
    else:
        st.warning("⚠️ No Anthropic API key configured. Set ANTHROPIC_API_KEY in .env file.")
    
    # Configuration File Info
    st.markdown("---")
    st.subheader("📄 Configuration Files")
    
    st.markdown("""
    **To modify these values:**
    1. Edit `.env` file in the project root
    2. Restart the application
    
    **Available environment variables:**
    - `ANXIETY_HIGH`, `ANXIETY_MEDIUM`
    - `IRRITABILITY_HIGH`
    - `SLEEP_ISSUES_HIGH`
    - `PROJECT_CHAOS_HIGH`
    - `UNWANTED_MEETINGS_HIGH`
    - `QUIET_BLOCKS_INSUFFICIENT_HIGH`
    - `CANNOT_SAY_NO_HIGH`
    - `UNMET_REQUESTS_HIGH`
    - `STRESS_OUTSIDE_HIGH`
    - `JIRA_BLOCKED_HIGH`
    - `NO_OWNERSHIP_HIGH`
    - `SELF_DEVELOPMENT_UNREALIZED_HIGH`
    - `URGENT_ALIGNMENT_HIGH`
    - `DEADLINE_PRESSURE_HIGH`
    - `APOLOGIES_HIGH`
    - `DELIVERY_LOG_THRESHOLD`
    - `ANTHROPIC_API_KEY`
    """)
    
    st.info("💡 **Tip**: Lower thresholds make the system more sensitive, higher thresholds make it less sensitive.")

def show_input_tab(needs_prompt):
    """New Entry Tab - Form Input"""
    previous = get_previous_entry()
    if previous:
        st.sidebar.caption(f"📅 Last entry: {previous.get('date', 'Unknown')}")

    st.header("Daily ADHD Radar & Metrics")

    metrics = {'date': datetime.now().strftime('%Y-%m-%d')}

    adhd_primary = [q for q in QUESTIONS if q.get('category') == 'adhd_primary']
    work_qs = [q for q in QUESTIONS if q.get('category') == 'work']
    individual_optional = [q for q in QUESTIONS if q.get('category') == 'individual']

    def render_required_question(question, column):
        help_text = question.get('description')
        if question.get('type') == 'yesno':
            previous_value = None
            if previous and question['key'] in previous and pd.notna(previous[question['key']]):
                try:
                    previous_value = int(previous[question['key']])
                except (ValueError, TypeError):
                    previous_value = None
            options = ['-NA', 'No', 'Yes']
            if previous_value is None:
                default_index = 0
            else:
                default_index = 2 if previous_value == 1 else 1
            with column:
                response = st.radio(
                    question['label'],
                    options=options,
                    index=default_index,
                    horizontal=True,
                    key=f"{question['key']}_required_yesno"
                )
                if help_text:
                    st.caption(help_text)
            # Value captured later from session state
        else:
            min_val = int(question.get('min', 0))
            max_val = int(question.get('max', 10))
            default_value = question.get('default')
            previous_value = None
            if previous and question['key'] in previous and pd.notna(previous[question['key']]):
                try:
                    previous_value = int(previous[question['key']])
                except (ValueError, TypeError):
                    previous_value = None
            options = ['-NA'] + [str(value) for value in range(min_val, max_val + 1)]
            default_selection = (
                str(previous_value)
                if previous_value is not None and str(previous_value) in options
                else (
                    str(int(default_value))
                    if default_value is not None and str(int(default_value)) in options
                    else '-NA'
                )
            )
            with column:
                selection = st.select_slider(
                    question['label'],
                    options=options,
                    value=default_selection,
                    key=f"{question['key']}_required_slider"
                )
                if help_text:
                    st.caption(help_text)
            # Value captured later from session state

    def render_optional_slider(question, column):
        min_val = int(question.get('min', 0))
        max_val = int(question.get('max', 10))
        help_text = question.get('description')
        default_value = question.get('default')
        previous_value = None
        if previous and question['key'] in previous and pd.notna(previous[question['key']]):
            try:
                previous_value = int(previous[question['key']])
            except (ValueError, TypeError):
                previous_value = None

        options = ['-NA'] + [str(value) for value in range(min_val, max_val + 1)]
        default_selection = (
            str(previous_value)
            if previous_value is not None and str(previous_value) in options
            else (
                str(int(default_value))
                if default_value is not None and str(int(default_value)) in options
                else '-NA'
            )
        )

        with column:
            selection = st.select_slider(
                question['label'],
                options=options,
                value=default_selection,
                key=f"{question['key']}_optional_slider"
            )
            if help_text:
                st.caption(help_text)

        if selection == '-NA':
            return None
        return int(selection)

    def render_optional_yesno(question, column):
        help_text = question.get('description')
        with column:
            previous_value = None
            if previous and question['key'] in previous and pd.notna(previous[question['key']]):
                try:
                    previous_value = int(previous[question['key']])
                except (ValueError, TypeError):
                    previous_value = None

            options = ['-NA', 'No', 'Yes']
            if previous_value is None:
                default_index = 0
            else:
                default_index = 2 if previous_value == 1 else 1

            selection = st.radio(
                question['label'],
                options=options,
                index=default_index,
                horizontal=True,
                key=f"{question['key']}_optional_yesno"
            )
            if help_text:
                st.caption(help_text)
            if selection == '-NA':
                return None
            if selection == 'Yes':
                return 1
            if selection == 'No':
                return 0
        return None

    with st.form("metrics_form"):
        st.subheader("🌟 ADHD Primary Signals (required)")
        st.caption("These eight checks keep you honest about stress build-up. Complete them before saving.")

        for index in range(0, len(adhd_primary), 2):
            col_left, col_right = st.columns(2)

            render_required_question(adhd_primary[index], col_left)

            if index + 1 < len(adhd_primary):
                render_required_question(adhd_primary[index + 1], col_right)
            else:
                with col_right:
                    st.empty()

        st.markdown("---")

        st.subheader("💼 Work Signals (optional)")
        for i in range(0, len(work_qs), 2):
            col_left, col_right = st.columns(2)

            q_left = work_qs[i]
            result_left = render_optional_slider(q_left, col_left) if q_left.get('type') != 'yesno' else render_optional_yesno(q_left, col_left)
            if result_left is not None:
                metrics[q_left['key']] = result_left

            if i + 1 < len(work_qs):
                q_right = work_qs[i + 1]
                result_right = render_optional_slider(q_right, col_right) if q_right.get('type') != 'yesno' else render_optional_yesno(q_right, col_right)
                if result_right is not None:
                    metrics[q_right['key']] = result_right

        st.markdown("---")

        st.subheader("🧘 Additional Wellbeing Signals (optional)")
        for i in range(0, len(individual_optional), 2):
            col_left, col_right = st.columns(2)

            q_left = individual_optional[i]
            result_left = render_optional_slider(q_left, col_left) if q_left.get('type') != 'yesno' else render_optional_yesno(q_left, col_left)
            if result_left is not None:
                metrics[q_left['key']] = result_left

            if i + 1 < len(individual_optional):
                q_right = individual_optional[i + 1]
                result_right = render_optional_slider(q_right, col_right) if q_right.get('type') != 'yesno' else render_optional_yesno(q_right, col_right)
                if result_right is not None:
                    metrics[q_right['key']] = result_right

        current_mode = st.session_state.config_thresholds.get('mode', 'Free')
        if current_mode == 'Claude AI':
            st.markdown("---")
            st.subheader("💬 Additional Context (Optional)")
            context = st.text_area(
                "Describe your current situation, concerns, or anything that might help create a better narrative:",
                height=100,
                key="free_form_context",
                placeholder="Example: 'Had a tough conversation with stakeholder X about deadline Y' or 'Feeling overwhelmed by constant context switching'"
            )
            if context and context.strip():
                metrics['context'] = context.strip()

        submitted = st.form_submit_button(
            "🚀 Analyze & Save",
            use_container_width=True
        )

        if submitted:
            required_missing = []
            for question in adhd_primary:
                widget_key = (
                    f"{question['key']}_required_yesno"
                    if question.get('type') == 'yesno'
                    else f"{question['key']}_required_slider"
                )
                selection = st.session_state.get(widget_key, '-NA')

                if question.get('type') == 'yesno':
                    if selection == '-NA':
                        metrics[question['key']] = None
                        required_missing.append(question['label'])
                    else:
                        metrics[question['key']] = 1 if selection == 'Yes' else 0
                else:
                    if selection == '-NA':
                        metrics[question['key']] = None
                        required_missing.append(question['label'])
                    else:
                        try:
                            metrics[question['key']] = int(selection)
                        except (TypeError, ValueError):
                            metrics[question['key']] = None
                            required_missing.append(question['label'])

            if required_missing:
                missing_list = " • ".join(required_missing)
                st.warning(
                    "⚠️ Complete all ADHD primary signals before saving:\n" +
                    " • " + missing_list
                )
                return

            with st.spinner("🤔 Building your story..."):
                try:
                    # Calculate changes
                    changes = get_metric_changes(metrics, previous)
                    
                    # Get narrative (using selected mode and model)
                    current_mode = st.session_state.config_thresholds.get('mode', 'Free')
                    current_model = st.session_state.config_thresholds.get('claude_model', 'claude-sonnet-4-20250514')
                    
                    # For Free mode, compute severity results with custom thresholds
                    severity_results = None
                    custom_thresholds = None
                    if current_mode == 'Free':
                        # Get custom thresholds from config
                        from modules.config import THRESHOLDS
                        custom_thresholds = THRESHOLDS.copy()
                        # Apply any user overrides from session state
                        for key, value in st.session_state.config_thresholds.items():
                            if key in custom_thresholds:
                                custom_thresholds[key] = value
                        
                        # Compute severity with same thresholds
                        problem_threshold = st.session_state.config_thresholds.get('problem_threshold', 6)
                        increase_threshold = st.session_state.config_thresholds.get('increase_threshold', 1.0)
                        severity_results = analyze_metrics_severity(
                            metrics,
                            previous,
                            problem_threshold=problem_threshold,
                            increase_threshold=increase_threshold,
                            custom_thresholds=custom_thresholds
                        )
                    
                    narrative, error = analyze_with_narrative(
                        metrics, previous, changes, 
                        mode=current_mode, 
                        model=current_model,
                        severity_results=severity_results,
                        custom_thresholds=custom_thresholds
                    )
                    
                    if error:
                        st.error(error)
                        return
                    
                    # Add recommendation to metrics before saving
                    metrics['recommendation'] = narrative

                    # Store in session state for analysis tab (persist after user confirmation)
                    st.session_state.latest_narrative = narrative
                    st.session_state.latest_metrics = dict(metrics)
                    st.session_state.latest_previous = previous
                    st.session_state.latest_changes = changes
                    st.session_state.last_analysis_date = normalize_date_value(metrics.get('date'))
                    st.session_state.pending_save_required = True
                    st.session_state.pending_save_mode = 'new'
                    st.session_state.pending_feedback_text = None
                    st.session_state.checkbox_reset_date = metrics['date']
                    st.session_state.pop('confirm_save_checkbox', None)
                    
                    st.success("✅ Analysis ready!")
                    st.info("☑️ Review the story in the '📖 Analysis' tab and tick the save box to keep it in your history.")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())



def show_analysis_tab():
    """Analysis Tab - 2-Column Layout: Findings (left) + Narrative (right)"""
    st.header("📖 Your Metrics Analysis")
    
    if 'latest_narrative' not in st.session_state:
        df = load_data()
        if len(df) == 0:
            st.info("👈 Submit a new entry first to see your personalized analysis!")
            return

        last_entry = df.iloc[-1]
        last_recommendation = last_entry.get('recommendation')

        if pd.isna(last_recommendation) or last_recommendation in (None, ""):
            st.info("👈 Submit a new entry first to see your personalized analysis!")
            return

        last_entry_dict = last_entry.to_dict()
        last_date_value = last_entry_dict.get('date')
        last_date_str = normalize_date_value(last_date_value)
        last_entry_dict['date'] = last_date_str

        previous_entry = df.iloc[-2].to_dict() if len(df) > 1 else None
        if previous_entry:
            previous_entry['date'] = normalize_date_value(previous_entry.get('date'))

        last_changes = get_metric_changes(last_entry_dict, previous_entry) if previous_entry else None

        st.session_state.latest_narrative = last_recommendation
        st.session_state.latest_metrics = last_entry_dict
        st.session_state.latest_previous = previous_entry
        st.session_state.latest_changes = last_changes
        st.session_state.last_analysis_date = last_date_str
        st.session_state.last_saved_narrative_date = last_date_str
        st.session_state.pending_save_required = False
        st.session_state.pending_save_mode = None
        st.session_state.pending_feedback_text = None
        st.session_state.checkbox_reset_date = last_date_str
        st.session_state.pop('confirm_save_checkbox', None)
    
    if 'last_analysis_date' in st.session_state:
        st.session_state.last_analysis_date = normalize_date_value(st.session_state.last_analysis_date)

    metrics = st.session_state.latest_metrics
    previous = st.session_state.latest_previous
    
    # Get current thresholds from session state
    problem_threshold = st.session_state.config_thresholds['problem_threshold']
    increase_threshold = st.session_state.config_thresholds['increase_threshold']

    from modules.config import THRESHOLDS
    custom_thresholds = THRESHOLDS.copy()
    for key, value in st.session_state.config_thresholds.items():
        if key in custom_thresholds:
            custom_thresholds[key] = value

    def format_metric_value(value, show_sign=False):
        if value is None:
            return "N/A"
        try:
            numeric = float(value)
        except (ValueError, TypeError):
            return "N/A"
        if math.isnan(numeric):
            return "N/A"
        prefix = "+" if show_sign and numeric > 0 else ""
        return f"{prefix}{numeric:.1f}"
    
    # Show parameters being used
    st.markdown(f"""
    <div style="background: #e8f4f8; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-size: 0.85em; border-left: 3px solid #3498db;">
        ⚙️ <strong>Analysis based on:</strong> Problem Threshold = {problem_threshold}, Increase Threshold = {increase_threshold}
        <span style="float: right; color: #3498db; cursor: pointer;">→ Adjust in Configuration tab</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Run severity analysis with custom thresholds
    severity_results = analyze_metrics_severity(
        metrics, 
        previous, 
        problem_threshold=problem_threshold,
        increase_threshold=increase_threshold,
        custom_thresholds=custom_thresholds
    )
    stats = calculate_severity_statistics(severity_results)
    
    # 2-column layout (narrow findings, wider narrative)
    col_findings, col_narrative = st.columns([0.75, 1.25])
    
    # LEFT COLUMN: Findings
    with col_findings:
        st.subheader("🔍 Findings")
        
        # Summary badge
        if stats['problem_percentage'] > 0:
            st.markdown(f"""
            <div style="background: #fff3cd; padding: 12px; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 15px; font-size: 0.9em;">
                📊 {stats['severity_increase_count']} increasing • {stats['continuous_issue_count']} continuous • {stats['safe_count']} safe
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success("✅ All metrics safe")
        
        # 🚨 HIGH SEVERITY (expanded by default)
        severity_increase_issues = [(score, detail) for score, detail in severity_results['severity_increase']]
        if severity_increase_issues:
            with st.expander(f"🚨 Problem Severity Increase ({len(severity_increase_issues)})", expanded=True):
                for score, detail in severity_increase_issues:  # Show ALL, not just 5
                    prev_text = format_metric_value(detail.get('previous'))
                    delta_text = format_metric_value(detail.get('delta'), show_sign=True)
                    
                    st.markdown(f"""
                    <div style="background: #fee; padding: 12px; border-radius: 6px; margin-bottom: 8px; border-left: 4px solid #e74c3c;">
                        <strong style="color: #e74c3c;">{detail['label']}</strong><br>
                        <span style="font-size: 1.1em;">{prev_text} → {detail['current']:.1f}</span> 
                        <span style="color: #e74c3c;">({delta_text})</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        # ⚠️ CONTINUOUS ISSUES (expanded by default now to see what's there)
        continuous_issues = [(score, detail) for score, detail in severity_results['continuous_issue']]
        if continuous_issues:
            with st.expander(f"⚠️ Continuous Issues ({len(continuous_issues)})", expanded=True):  # Changed to expanded=True
                for score, detail in continuous_issues:  # Show ALL, not just 5
                    prev_text = format_metric_value(detail.get('previous'))
                    
                    st.markdown(f"""
                    <div style="background: #fff9e6; padding: 12px; border-radius: 6px; margin-bottom: 8px; border-left: 4px solid #f39c12;">
                        <strong style="color: #f39c12;">{detail['label']}</strong><br>
                        <span style="font-size: 1.1em;">Stable at {detail['current']:.1f}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        # ✅ SAFE ZONE (collapsed by default)
        safe_metrics = severity_results['safe']
        if safe_metrics:
            with st.expander(f"✅ Safe Zone ({len(safe_metrics)})", expanded=False):
                for score, detail in safe_metrics:  # Show ALL safe metrics, not just 5
                    prev_text = format_metric_value(detail.get('previous'))
                    delta_text = format_metric_value(detail.get('delta'), show_sign=True)
                    
                    st.markdown(f"""
                    <div style="background: #eafaf1; padding: 10px; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid #2ecc71;">
                        <strong style="color: #27ae60; font-size: 0.9em;">{detail['label']}</strong><br>
                        <span style="font-size: 0.95em;">{prev_text} → {detail['current']:.1f} ({delta_text})</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Delivery log recommendation (if needed)
        should_recommend, triggered = should_recommend_delivery_log(metrics, st.session_state.config_thresholds)
        if should_recommend:
            st.markdown("---")
            st.markdown(f"""
            <div style="background: #fff3cd; padding: 12px; border-radius: 8px; border-left: 4px solid #ffc107; margin-top: 15px; font-size: 0.9em;">
                📋 <strong>Delivery Log Recommended</strong><br>
                High metrics: {', '.join([t.split('(')[0].strip() for t in triggered])}
            </div>
            """, unsafe_allow_html=True)
    
    # RIGHT COLUMN: Narrative
    with col_narrative:
        st.subheader("� Story")
        
        st.markdown(f"""
        <div style="background: white; padding: 24px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.12); max-height: 640px; overflow-y: auto; font-size: 1.05em; line-height: 1.6;">
            {st.session_state.latest_narrative}
        </div>
        """, unsafe_allow_html=True)

        # Confirmation checkbox logic to persist narrative
        current_story_date = normalize_date_value(st.session_state.get('last_analysis_date'))
        if not current_story_date:
            st.warning("Generate or load an analysis before regenerating the story.")
            return

        st.session_state.last_analysis_date = current_story_date
        pending_save = st.session_state.get('pending_save_required', False)

        # Reset checkbox state when viewing a different story date
        if st.session_state.get('checkbox_reset_date') != current_story_date:
            st.session_state.checkbox_reset_date = current_story_date
            st.session_state.pop('confirm_save_checkbox', None)

        if pending_save:
            st.warning("Review the story above. Tick the box below to save it to your history.")

            confirm_checked = st.checkbox(
                "✅ Save this story to my history",
                key="confirm_save_checkbox"
            )

            if confirm_checked:
                save_mode = st.session_state.get('pending_save_mode', 'new')
                if save_mode == 'update':
                    from modules.data import update_entry_recommendation
                    update_entry_recommendation(current_story_date, st.session_state.latest_narrative)
                else:
                    save_entry(st.session_state.latest_metrics)

                from modules.narratives import save_narrative
                save_narrative(
                    current_story_date,
                    st.session_state.latest_narrative,
                    st.session_state.get('pending_feedback_text')
                )

                st.session_state.pending_save_required = False
                st.session_state.last_saved_narrative_date = current_story_date
                st.session_state.pending_feedback_text = None
                st.session_state.pop('confirm_save_checkbox', None)

                st.success("💾 Story saved to history!")
                st.rerun()
        else:
            if st.session_state.get('last_saved_narrative_date') == current_story_date:
                st.success("💾 Story saved to history.")

        # Feedback section (compact)
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("💬 Feedback & Regenerate", expanded=False):
            st.caption("Provide feedback to regenerate an improved recommendation")
            feedback = st.text_area(
                "Your feedback:",
                placeholder="What was inaccurate? What should be adjusted?",
                key="feedback_input",
                height=100
            )
            
            if st.button("� Regenerate with Feedback", use_container_width=True):
                if feedback.strip():
                    with st.spinner("🤔 Regenerating recommendation with your feedback..."):
                        # Save feedback first
                        update_narrative_with_feedback(current_story_date, feedback)
                        
                        # Get the current mode and model
                        current_mode = st.session_state.config_thresholds.get('mode', 'Free')
                        current_model = st.session_state.config_thresholds.get('claude_model', 'claude-3-5-haiku-20241022')
                        
                        # Regenerate narrative with feedback included
                        from modules.data import get_entry_by_date
                        
                        # Get the entry for this date
                        entry = get_entry_by_date(current_story_date)
                        if entry:
                            # Get previous entry for changes calculation
                            # We need to get the entry BEFORE the current one
                            df = load_data()
                            current_idx = df[df['date'] == current_story_date].index[0]
                            previous = df.iloc[current_idx - 1].to_dict() if current_idx > 0 else None
                            
                            changes = get_metric_changes(entry, previous)
                            
                            # Compute severity if in Free mode
                            severity_results = None
                            custom_thresholds = None
                            if current_mode == 'Free':
                                from modules.config import THRESHOLDS
                                custom_thresholds = THRESHOLDS.copy()
                                for key, value in st.session_state.config_thresholds.items():
                                    if key in custom_thresholds:
                                        custom_thresholds[key] = value
                                
                                problem_threshold = st.session_state.config_thresholds.get('problem_threshold', 6)
                                increase_threshold = st.session_state.config_thresholds.get('increase_threshold', 1.0)
                                severity_results = analyze_metrics_severity(
                                    entry, 
                                    previous,
                                    problem_threshold=problem_threshold,
                                    increase_threshold=increase_threshold,
                                    custom_thresholds=custom_thresholds
                                )
                            
                            # Regenerate narrative (feedback is already saved and will be included)
                            new_narrative, error = analyze_with_narrative(
                                entry, previous, changes,
                                mode=current_mode,
                                model=current_model,
                                severity_results=severity_results,
                                custom_thresholds=custom_thresholds
                            )
                            
                            if error:
                                st.error(error)
                            else:
                                # Update session state with pending regeneration requiring confirmation
                                st.session_state.latest_narrative = new_narrative
                                st.session_state.latest_metrics = dict(entry)
                                st.session_state.latest_metrics['recommendation'] = new_narrative
                                st.session_state.pending_save_required = True
                                st.session_state.pending_save_mode = 'update'
                                st.session_state.pending_feedback_text = feedback
                                st.session_state.checkbox_reset_date = current_story_date
                                st.session_state.pop('confirm_save_checkbox', None)
                                
                                st.success("✅ Story regenerated. Tick the save box to update history.")
                                st.rerun()
                        else:
                            st.error("Could not find entry for this date")
                else:
                    st.warning("Enter feedback first")

def show_dashboard_tab():
    """Dashboard Tab - Visualizations"""
    import pandas as pd
    
    st.header("📊 Metrics Dashboard")
    
    df = load_data()
    
    if len(df) == 0:
        st.warning("No data yet. Fill in your first entry in the 'New Entry' tab!")
        return
    
    df['date'] = pd.to_datetime(df['date'])
    
    latest = df.iloc[-1]
    previous = df.iloc[-2] if len(df) > 1 else None
    
    st.info(f"📊 Total entries: {len(df)} | Latest: {latest['date'].strftime('%Y-%m-%d')}")
    
    # Filter options
    n_entries = st.sidebar.slider("Show last N entries", 1, max(1, len(df)), min(10, len(df)))
    df_display = df.tail(n_entries)
    
    # Key Metrics Cards
    st.markdown("### ADHD Radar Snapshot")
    col1, col2, col3, col4 = st.columns(4)

    def calc_delta(key):
        if previous is not None and key in previous and key in latest:
            try:
                return float(latest[key] - previous[key])
            except Exception:
                return 0
        return 0

    def display_radar_metric(column, key, label):
        with column:
            if key in latest and pd.notna(latest[key]):
                current = float(latest[key])
                delta = calc_delta(key)
                st.metric(label, f"{current:.0f}/10", f"{delta:+.0f}", delta_color="inverse")

    display_radar_metric(col1, 'signal_body_tension', 'Body tension')
    display_radar_metric(col2, 'signal_mind_noise', 'Mind noise')
    display_radar_metric(col3, 'signal_focus_friction', 'Focus friction')
    display_radar_metric(col4, 'signal_energy_drain', 'Energy drain')
    
    # Charts - Selectable Metrics
    st.markdown("---")
    st.subheader("📈 Metric Visualization")
    st.caption("Select metrics to visualize (easier to read individually)")
    
    # Get all available numeric metrics from QUESTIONS
    available_metrics = []
    for q in QUESTIONS:
        if q.get('type') != 'yesno' and q['key'] in df_display.columns and df_display[q['key']].notna().any():
            available_metrics.append({
                'key': q['key'],
                'label': q['label'],
                'category': q.get('category', 'other')
            })
    
    # Group by category
    adhd_metrics = [m for m in available_metrics if m['category'] == 'adhd_primary']
    work_metrics = [m for m in available_metrics if m['category'] == 'work']
    individual_metrics = [m for m in available_metrics if m['category'] == 'individual']

    # ADHD Radar Selection
    if adhd_metrics:
        st.markdown("**🌟 ADHD Radar Signals**")
        adhd_cols = st.columns(4)
        selected_adhd = []
        for idx, metric in enumerate(adhd_metrics):
            with adhd_cols[idx % 4]:
                if st.checkbox(metric['label'], key=f"chart_adhd_{metric['key']}", value=False):
                    selected_adhd.append(metric)

        if selected_adhd:
            fig_adhd = go.Figure()
            colors = ['#ff8fa3', '#f6bd60', '#84a59d', '#f28482', '#f5cac3', '#b8c0ff']

            for i, metric in enumerate(selected_adhd):
                fig_adhd.add_trace(go.Scatter(
                    x=df_display['date'],
                    y=df_display[metric['key']],
                    name=metric['label'],
                    mode='lines+markers',
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=8)
                ))

            fig_adhd.update_layout(
                height=320,
                hovermode='x unified',
                plot_bgcolor='white',
                paper_bgcolor='white',
                yaxis=dict(range=[0, 10], title="Score (0-10)"),
                xaxis=dict(title="Date"),
                showlegend=True
            )

            st.plotly_chart(fig_adhd, use_container_width=True)
    
    # Work Metrics Selection
    if work_metrics:
        st.markdown("**💼 Work Metrics**")
        work_cols = st.columns(4)
        selected_work = []
        for idx, metric in enumerate(work_metrics):
            with work_cols[idx % 4]:
                if st.checkbox(metric['label'], key=f"chart_work_{metric['key']}", value=False):
                    selected_work.append(metric)
        
        if selected_work:
            fig_work = go.Figure()
            colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#fa709a', '#fee140', '#30cfd0']
            
            for i, metric in enumerate(selected_work):
                fig_work.add_trace(go.Scatter(
                    x=df_display['date'],
                    y=df_display[metric['key']],
                    name=metric['label'],
                    mode='lines+markers',
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=8)
                ))
            
            fig_work.update_layout(
                height=400,
                hovermode='x unified',
                plot_bgcolor='white',
                paper_bgcolor='white',
                yaxis=dict(range=[0, 10], title="Score (1-10)"),
                xaxis=dict(title="Date"),
                showlegend=True
            )
            
            st.plotly_chart(fig_work, use_container_width=True)
    
    # Individual Metrics Selection
    if individual_metrics:
        st.markdown("**🧘 Individual Metrics**")
        individual_cols = st.columns(4)
        selected_individual = []
        for idx, metric in enumerate(individual_metrics):
            with individual_cols[idx % 4]:
                if st.checkbox(metric['label'], key=f"chart_individual_{metric['key']}", value=False):
                    selected_individual.append(metric)
        
        if selected_individual:
            fig_individual = go.Figure()
            colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#fa709a', '#fee140', '#30cfd0']
            
            for i, metric in enumerate(selected_individual):
                fig_individual.add_trace(go.Scatter(
                    x=df_display['date'],
                    y=df_display[metric['key']],
                    name=metric['label'],
                    mode='lines+markers',
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=8)
                ))
            
            fig_individual.update_layout(
                height=400,
                hovermode='x unified',
                plot_bgcolor='white',
                paper_bgcolor='white',
                yaxis=dict(range=[0, 10], title="Score (1-10)"),
                xaxis=dict(title="Date"),
                showlegend=True
            )
            
            st.plotly_chart(fig_individual, use_container_width=True)
    
    # Current Insights
    st.markdown("---")
    st.subheader("🎯 Current Status")
    
    # Use custom thresholds from configuration
    from modules.config import THRESHOLDS
    custom_thresholds = THRESHOLDS.copy()
    if 'config_thresholds' in st.session_state:
        for key, value in st.session_state.config_thresholds.items():
            if key in custom_thresholds:
                custom_thresholds[key] = value

    insights = generate_quick_insights(
        latest.to_dict(), 
        previous.to_dict() if previous is not None else None,
        custom_thresholds=custom_thresholds
    )
    for level, text in insights:
        st.markdown(f'<div class="alert-{level}">{text}</div>', unsafe_allow_html=True)
    
    # Raw data
    with st.expander("📋 View Raw Data"):
        st.dataframe(df_display.sort_values('date', ascending=False), use_container_width=True)

def show_about_tab():
    """About Tab"""
    st.header("ℹ️ About This Tracker")
    
    st.markdown("""
    ### 📊 Work & Individual Metrics Tracker
    
    **How it works:**
    1. **New Entry:** Complete the ADHD radar (required) then add any optional context
    2. **AI Narrative:** Claude builds a story connecting your metrics
    3. **Feedback Loop:** Improve future analyses with your context
    4. **Dashboard:** Visualize trends over time
    
    **Key Features:**
    - 📖 **Story-based analysis** - No more threshold lists
    - 💬 **Feedback system** - Help Claude understand your context
    - 📊 **Visual trends** - See patterns over time
    - 🎯 **Quick alerts** - Immediate actionable insights
    
    **Modular Architecture:**
    - `modules/config.py` - Configuration & thresholds
    - `modules/data.py` - Data management
    - `modules/narratives.py` - Story building & feedback
    - `modules/analysis.py` - Claude API calls
    - `modules/insights.py` - Quick insights (no API)
    
    **Data Storage:**
    - `metrics_data.csv` - Your metrics history
    - `narratives.json` - Analysis narratives with feedback
    
    **Cost Efficiency:**
    - Quick insights: No API calls
    - Deep analysis: One API call per submission
    - Feedback: Stored locally, used in future prompts
    """)
    
    st.markdown("---")
    st.caption("Built with Streamlit • Powered by Claude AI • Modular & Efficient")

# Missing import at the top
import pandas as pd

if __name__ == "__main__":
    main()
