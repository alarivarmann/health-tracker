#!/usr/bin/env python3
"""
Metrics Tracker - Main Streamlit App (Modular Version)
Uses story-based narratives with feedback loop
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

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
    st.title("📊 Work & Individual Metrics Tracker")
    
    # Initialize session state for checkboxes
    if 'checkboxes' not in st.session_state:
        st.session_state.checkboxes = {q['key']: True for q in QUESTIONS}
    
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
            'anxiety_high': THRESHOLDS['anxiety_high'],
            'anxiety_medium': THRESHOLDS['anxiety_medium'],
            'irritability_high': THRESHOLDS['irritability_high'],
            'sleep_issues_high': THRESHOLDS['sleep_issues_high'],
            'project_chaos_high': THRESHOLDS['project_chaos_high'],
            'unwanted_meetings_high': THRESHOLDS['unwanted_meetings_high'],
            'quiet_blocks_insufficient_high': THRESHOLDS['quiet_blocks_insufficient_high'],
            'cannot_say_no_high': THRESHOLDS['cannot_say_no_high'],
            'unmet_requests_high': THRESHOLDS['unmet_requests_high'],
            'stress_outside_high': THRESHOLDS['stress_outside_high'],
            'jira_blocked_high': THRESHOLDS['jira_blocked_high'],
            'no_ownership_high': THRESHOLDS['no_ownership_high'],
            'urgent_alignment_high': THRESHOLDS['urgent_alignment_high'],
            'self_development_unrealized_high': THRESHOLDS['self_development_unrealized_high'],
            'deadline_pressure_high': THRESHOLDS['deadline_pressure_high'],
            'apologies_high': THRESHOLDS['apologies_high']
        }
    
    # Check if input needed
    needs_prompt, reason = should_prompt_today()
    
    # Tab navigation
    tab0, tab1, tab2, tab3, tab4 = st.tabs(["⚙️ Configuration", "📝 New Entry", "📊 Dashboard", "📖 Analysis", "ℹ️ About"])
    
    with tab0:
        show_configuration_tab()
    
    with tab1:
        show_input_tab(needs_prompt)
    
    with tab2:
        show_dashboard_tab()
    
    with tab3:
        show_analysis_tab()
    
    with tab4:
        show_about_tab()

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
                'anxiety_high': THRESHOLDS['anxiety_high'],
                'anxiety_medium': THRESHOLDS['anxiety_medium'],
                'irritability_high': THRESHOLDS['irritability_high'],
                'sleep_issues_high': THRESHOLDS['sleep_issues_high'],
                'project_chaos_high': THRESHOLDS['project_chaos_high'],
                'unwanted_meetings_high': THRESHOLDS['unwanted_meetings_high'],
                'quiet_blocks_insufficient_high': THRESHOLDS['quiet_blocks_insufficient_high'],
                'cannot_say_no_high': THRESHOLDS['cannot_say_no_high'],
                'unmet_requests_high': THRESHOLDS['unmet_requests_high'],
                'stress_outside_high': THRESHOLDS['stress_outside_high'],
                'jira_blocked_high': THRESHOLDS['jira_blocked_high'],
                'no_ownership_high': THRESHOLDS['no_ownership_high'],
                'urgent_alignment_high': THRESHOLDS['urgent_alignment_high'],
                'self_development_unrealized_high': THRESHOLDS['self_development_unrealized_high'],
                'deadline_pressure_high': THRESHOLDS['deadline_pressure_high'],
                'apologies_high': THRESHOLDS['apologies_high']
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
    if needs_prompt:
        st.markdown('<div class="prompt-banner">🔔 Time for your metrics check-in!</div>', unsafe_allow_html=True)
    
    st.header("Input Your Metrics")
    st.markdown("**Select which metrics to fill** (uncheck to skip)")
    
    previous = get_previous_entry()
    if previous:
        st.info(f"📅 Last entry: {previous.get('date', 'Unknown')}")
    
    metrics = {'date': datetime.now().strftime('%Y-%m-%d')}
    
    with st.form("metrics_form"):
        # Work Metrics
        st.subheader("💼 Work Metrics")
        work_qs = [q for q in QUESTIONS if q.get('category') == 'work']
        
        # Process in pairs for 2-column layout
        for i in range(0, len(work_qs), 2):
            col_left, col_right = st.columns(2)
            
            # Left metric
            with col_left:
                q = work_qs[i]
                col1, col2 = st.columns([0.5, 4])
                with col1:
                    enabled = st.checkbox("✓", value=st.session_state.checkboxes.get(q['key'], True), key=f"enable_{q['key']}")
                    st.session_state.checkboxes[q['key']] = enabled
                
                with col2:
                    if q.get('type') == 'yesno':
                        val = st.selectbox(q['label'], ['yes', 'no'], key=q['key'], disabled=not enabled)
                        if enabled:
                            metrics[q['key']] = 1 if val == 'yes' else 0
                    else:
                        val = st.slider(q['label'], 1, 10, 5, key=q['key'], disabled=not enabled)
                        if enabled:
                            metrics[q['key']] = val
            
            # Right metric (if exists)
            if i + 1 < len(work_qs):
                with col_right:
                    q = work_qs[i + 1]
                    col1, col2 = st.columns([0.5, 4])
                    with col1:
                        enabled = st.checkbox("✓", value=st.session_state.checkboxes.get(q['key'], True), key=f"enable_{q['key']}")
                        st.session_state.checkboxes[q['key']] = enabled
                    
                    with col2:
                        if q.get('type') == 'yesno':
                            val = st.selectbox(q['label'], ['yes', 'no'], key=q['key'], disabled=not enabled)
                            if enabled:
                                metrics[q['key']] = 1 if val == 'yes' else 0
                        else:
                            val = st.slider(q['label'], 1, 10, 5, key=q['key'], disabled=not enabled)
                            if enabled:
                                metrics[q['key']] = val
        
        st.markdown("---")
        
        # Individual Metrics
        st.subheader("🧘 Individual Metrics")
        individual_qs = [q for q in QUESTIONS if q.get('category') == 'individual']
        
        # Process in pairs for 2-column layout
        for i in range(0, len(individual_qs), 2):
            col_left, col_right = st.columns(2)
            
            # Left metric
            with col_left:
                q = individual_qs[i]
                col1, col2 = st.columns([0.5, 4])
                with col1:
                    enabled = st.checkbox("✓", value=st.session_state.checkboxes.get(q['key'], True), key=f"enable_{q['key']}")
                    st.session_state.checkboxes[q['key']] = enabled
                
                with col2:
                    if q.get('type') == 'yesno':
                        val = st.selectbox(q['label'], ['yes', 'no'], key=q['key'], disabled=not enabled)
                        if enabled:
                            metrics[q['key']] = 1 if val == 'yes' else 0
                    else:
                        val = st.slider(q['label'], 1, 10, 5, key=q['key'], disabled=not enabled)
                        if enabled:
                            metrics[q['key']] = val
            
            # Right metric (if exists)
            if i + 1 < len(individual_qs):
                with col_right:
                    q = individual_qs[i + 1]
                    col1, col2 = st.columns([0.5, 4])
                    with col1:
                        enabled = st.checkbox("✓", value=st.session_state.checkboxes.get(q['key'], True), key=f"enable_{q['key']}")
                        st.session_state.checkboxes[q['key']] = enabled
                    
                    with col2:
                        if q.get('type') == 'yesno':
                            val = st.selectbox(q['label'], ['yes', 'no'], key=q['key'], disabled=not enabled)
                            if enabled:
                                metrics[q['key']] = 1 if val == 'yes' else 0
                        else:
                            val = st.slider(q['label'], 1, 10, 5, key=q['key'], disabled=not enabled)
                            if enabled:
                                metrics[q['key']] = val
        
        # Free-form context (only visible in AI mode)
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
        
        submitted = st.form_submit_button("🚀 Analyze & Save", use_container_width=True)
        
        if submitted:
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
                            increase_threshold=increase_threshold
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
                    
                    # Save metrics with recommendation
                    save_entry(metrics)
                    
                    # Also save narrative to narratives.json (for feedback history)
                    from modules.narratives import save_narrative
                    save_narrative(metrics['date'], narrative)
                    
                    # Store in session state for analysis tab
                    st.session_state.latest_narrative = narrative
                    st.session_state.latest_metrics = metrics
                    st.session_state.latest_previous = previous
                    st.session_state.latest_changes = changes
                    st.session_state.last_analysis_date = metrics['date']
                    
                    st.success("✅ Analysis complete and saved!")
                    st.info("💡 Go to the '📖 Analysis' tab to see your story and insights!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())



def show_analysis_tab():
    """Analysis Tab - 2-Column Layout: Findings (left) + Narrative (right)"""
    st.header("📖 Your Metrics Analysis")
    
    if 'latest_narrative' not in st.session_state:
        st.info("👈 Submit a new entry first to see your personalized analysis!")
        return
    
    metrics = st.session_state.latest_metrics
    previous = st.session_state.latest_previous
    
    # Get current thresholds from session state
    problem_threshold = st.session_state.config_thresholds['problem_threshold']
    increase_threshold = st.session_state.config_thresholds['increase_threshold']
    
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
        increase_threshold=increase_threshold
    )
    stats = calculate_severity_statistics(severity_results)
    
    # 2-column layout
    col_findings, col_narrative = st.columns([1, 1])
    
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
                    prev_text = f"{detail['previous']:.1f}" if detail['previous'] is not None else "N/A"
                    delta_text = f"+{detail['delta']:.1f}" if detail['delta'] > 0 else f"{detail['delta']:.1f}"
                    
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
                    prev_text = f"{detail['previous']:.1f}" if detail['previous'] is not None else "N/A"
                    
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
                    prev_text = f"{detail['previous']:.1f}" if detail['previous'] is not None else "N/A"
                    delta_text = f"+{detail['delta']:.1f}" if detail['delta'] > 0 else f"{detail['delta']:.1f}"
                    
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
        <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); max-height: 600px; overflow-y: auto;">
            {st.session_state.latest_narrative}
        </div>
        """, unsafe_allow_html=True)
        
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
                        update_narrative_with_feedback(st.session_state.last_analysis_date, feedback)
                        
                        # Get the current mode and model
                        current_mode = st.session_state.config_thresholds.get('mode', 'Free')
                        current_model = st.session_state.config_thresholds.get('claude_model', 'claude-3-5-haiku-20241022')
                        
                        # Regenerate narrative with feedback included
                        from modules.data import get_metric_changes, update_entry_recommendation, get_entry_by_date, load_data
                        
                        # Get the entry for this date
                        entry = get_entry_by_date(st.session_state.last_analysis_date)
                        if entry:
                            # Get previous entry for changes calculation
                            # We need to get the entry BEFORE the current one
                            df = load_data()
                            current_idx = df[df['date'] == st.session_state.last_analysis_date].index[0]
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
                                    increase_threshold=increase_threshold
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
                                # Update the recommendation in the CSV (overwrite for same date)
                                update_entry_recommendation(st.session_state.last_analysis_date, new_narrative)
                                
                                # Update session state
                                st.session_state.latest_narrative = new_narrative
                                
                                # Save to narratives.json
                                from modules.narratives import save_narrative
                                save_narrative(st.session_state.last_analysis_date, new_narrative, feedback)
                                
                                st.success("✅ Recommendation regenerated and updated!")
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
    st.markdown("### Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    def calc_delta(key):
        if previous is not None and key in previous and key in latest:
            try:
                return float(latest[key] - previous[key])
            except:
                return 0
        return 0
    
    with col1:
        if 'anxiety' in latest and pd.notna(latest['anxiety']):
            st.metric("Anxiety", f"{latest['anxiety']:.1f}", f"{calc_delta('anxiety'):+.1f}", delta_color="inverse")
    
    with col2:
        if 'project_chaos' in latest and pd.notna(latest['project_chaos']):
            st.metric("Project Chaos", f"{latest['project_chaos']:.1f}", f"{calc_delta('project_chaos'):+.1f}", delta_color="inverse")
    
    with col3:
        if 'sleep_quality' in latest and pd.notna(latest['sleep_quality']):
            st.metric("Sleep Quality", f"{latest['sleep_quality']:.1f}", f"{calc_delta('sleep_quality'):+.1f}")
    
    with col4:
        if 'quiet_blocks' in latest and pd.notna(latest['quiet_blocks']):
            st.metric("Quiet Blocks", f"{latest['quiet_blocks']:.1f}", f"{calc_delta('quiet_blocks'):+.1f}")
    
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
    work_metrics = [m for m in available_metrics if m['category'] == 'work']
    individual_metrics = [m for m in available_metrics if m['category'] == 'individual']
    
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
    # Apply any user overrides from session state
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
    1. **New Entry:** Fill in metrics (selective via checkboxes)
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
