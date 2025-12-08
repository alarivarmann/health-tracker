#!/usr/bin/env python3
"""
Metrics Tracker - Mobile Version
Simplified single-column layout optimized for phone screens
Shares backend with desktop version (metrics_app.py)

Version: 1.0.2 (Force deployment - added physical exercise field)
"""

import math
import streamlit as st
import pandas as pd
from datetime import datetime

# Import shared modules (no changes to existing code)
from modules.config import QUESTIONS
from modules.data import (
    load_data, save_entry, get_previous_entry,
    should_prompt_today, get_metric_changes
)
from modules.analysis import analyze_with_narrative, update_narrative_with_feedback
from modules.severity import analyze_metrics_severity, calculate_severity_statistics

# Page config optimized for mobile
st.set_page_config(
    page_title="📊 Metrics (Mobile)",
    page_icon="📱",
    layout="centered",  # Better for mobile
    initial_sidebar_state="collapsed"  # Hide sidebar on mobile by default
)

# Simpler mobile-friendly CSS
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
    h1, h2, h3 {color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);}
    .stButton>button {width: 100%; padding: 15px; font-size: 1.1em;}
    .narrative-box {background: white; padding: 20px; border-radius: 12px; margin: 15px 0;}
</style>
""", unsafe_allow_html=True)


def normalize_date_value(date_value):
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

def main():
    st.title("📱 Metrics Tracker")
    st.caption("Mobile Version")
    
    # Initialize session state for thresholds
    if 'config_thresholds' not in st.session_state:
        from modules.config import THRESHOLDS, ANTHROPIC_API_KEY
        default_mode = 'Claude AI' if (ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != 'your_key_here') else 'Free'
        
        st.session_state.config_thresholds = {
            'mode': default_mode,
            'claude_model': 'claude-3-5-haiku-20241022',
            'problem_threshold': 6,
            'increase_threshold': 1.0,
            **{f'{k}_high': THRESHOLDS.get(f'{k}_high', 7) for k in [
                'signal_body_tension', 'signal_mind_noise', 'signal_focus_friction',
                'signal_emotion_wave', 'signal_energy_drain', 'anxiety', 'irritability',
                'sleep_issues', 'project_chaos', 'unwanted_meetings'
            ]}
        }
    
    # Reset ADHD widgets on fresh load
    if 'adhd_widgets_initialized' not in st.session_state:
        adhd_primary = [q for q in QUESTIONS if q.get('category') == 'adhd_primary']
        for question in adhd_primary:
            if question.get('type') == 'yesno':
                st.session_state[f"{question['key']}_mobile_yesno"] = '-NA'
            else:
                st.session_state[f"{question['key']}_mobile_slider"] = '-NA'
        st.session_state.adhd_widgets_initialized = True
    
    # Simple tab navigation
    tab_entry, tab_analysis = st.tabs(["📝 New Entry", "📖 Last Analysis"])
    
    with tab_entry:
        show_entry_tab()
    
    with tab_analysis:
        show_analysis_tab()

def show_entry_tab():
    """Mobile-optimized entry form - single column, touch-friendly"""
    st.header("Daily Check-In")
    
    previous = get_previous_entry()
    if previous:
        st.caption(f"📅 Last entry: {previous.get('date', 'Unknown')}")
    
    metrics = {'date': datetime.now().strftime('%Y-%m-%d')}
    adhd_primary = [q for q in QUESTIONS if q.get('category') == 'adhd_primary']
    
    with st.form("mobile_metrics_form"):
        st.subheader("🌟 ADHD Signals")
        st.caption("Complete all 8 signals before saving")
        
        # Single-column layout for mobile
        for question in adhd_primary:
            help_text = question.get('description')
            
            if question.get('type') == 'yesno':
                st.radio(
                    question['label'],
                    options=['-NA', 'No', 'Yes'],
                    index=0,
                    horizontal=True,
                    key=f"{question['key']}_mobile_yesno",
                    help=help_text
                )
            else:
                min_val = int(question.get('min', 0))
                max_val = int(question.get('max', 10))
                options = ['-NA'] + [str(v) for v in range(min_val, max_val + 1)]
                
                st.select_slider(
                    question['label'],
                    options=options,
                    value='-NA',
                    key=f"{question['key']}_mobile_slider",
                    help=help_text
                )
            
            # Add spacing between questions
            st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
        
        # Optional context
        current_mode = st.session_state.config_thresholds.get('mode', 'Free')
        if current_mode == 'Claude AI':
            st.markdown("---")
            st.subheader("💬 Additional Context (Optional)")
            context = st.text_area(
                "Describe your current situation:",
                height=100,
                key="mobile_context",
                placeholder="E.g., 'Had difficult meeting', 'Feeling overwhelmed'"
            )
            if context and context.strip():
                metrics['context'] = context.strip()
        
        submitted = st.form_submit_button("🚀 Analyze & Save", use_container_width=True)
        
        if submitted:
            # Validate all required fields
            required_missing = []
            for question in adhd_primary:
                if question.get('type') == 'yesno':
                    key = f"{question['key']}_mobile_yesno"
                else:
                    key = f"{question['key']}_mobile_slider"
                
                selection = st.session_state.get(key, '-NA')
                
                if selection == '-NA':
                    required_missing.append(question['label'])
                elif question.get('type') == 'yesno':
                    metrics[question['key']] = 1 if selection == 'Yes' else 0
                else:
                    try:
                        metrics[question['key']] = int(selection)
                    except (TypeError, ValueError):
                        required_missing.append(question['label'])
            
            if required_missing:
                st.warning(f"⚠️ Complete all signals:\n• " + "\n• ".join(required_missing))
                return
            
            with st.spinner("🤔 Building your story..."):
                try:
                    previous = get_previous_entry()
                    changes = get_metric_changes(metrics, previous) if previous else None
                    
                    current_mode = st.session_state.config_thresholds.get('mode', 'Free')
                    current_model = st.session_state.config_thresholds.get('claude_model', 'claude-3-5-haiku-20241022')
                    
                    severity_results = None
                    custom_thresholds = None
                    if current_mode == 'Free':
                        from modules.config import THRESHOLDS
                        custom_thresholds = THRESHOLDS.copy()
                        problem_threshold = st.session_state.config_thresholds.get('problem_threshold', 6)
                        increase_threshold = st.session_state.config_thresholds.get('increase_threshold', 1.0)
                        severity_results = analyze_metrics_severity(
                            metrics, previous,
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
                    
                    metrics['recommendation'] = narrative
                    
                    # Store for analysis tab
                    st.session_state.latest_narrative = narrative
                    st.session_state.latest_metrics = dict(metrics)
                    st.session_state.latest_previous = previous
                    st.session_state.latest_changes = changes
                    analysis_date = normalize_date_value(metrics.get('date'))
                    st.session_state.last_analysis_date = analysis_date
                    st.session_state.pending_save_required = True
                    st.session_state.pending_save_mode = 'new'
                    st.session_state.pending_feedback_text = None
                    st.session_state.checkbox_reset_date = analysis_date
                    st.session_state.pop('confirm_save_mobile', None)
                    
                    st.success("✅ Analysis ready!")
                    st.info("☑️ Go to 'Last Analysis' tab to review and save")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

def show_analysis_tab():
    """Mobile-optimized analysis view - single column, narrative focus"""
    st.header("📖 Your Analysis")
    
    # Auto-load last saved analysis if none in session
    if 'latest_narrative' not in st.session_state:
        df = load_data()
        if len(df) == 0:
            st.info("👈 Submit your first entry to see analysis")
            return
        
        last_entry = df.iloc[-1]
        last_recommendation = last_entry.get('recommendation')
        
        if pd.isna(last_recommendation) or last_recommendation in (None, ""):
            st.info("👈 Submit your first entry to see analysis")
            return
        
        # Hydrate session state from saved data
        last_entry_dict = last_entry.to_dict()
        last_date = normalize_date_value(last_entry_dict.get('date'))
        last_entry_dict['date'] = last_date

        previous_entry = df.iloc[-2].to_dict() if len(df) > 1 else None
        if previous_entry:
            previous_entry['date'] = normalize_date_value(previous_entry.get('date'))
        
        last_changes = get_metric_changes(last_entry_dict, previous_entry) if previous_entry else None
        
        st.session_state.latest_narrative = last_recommendation
        st.session_state.latest_metrics = last_entry_dict
        st.session_state.latest_previous = previous_entry
        st.session_state.latest_changes = last_changes
        st.session_state.last_analysis_date = last_date
        st.session_state.last_saved_narrative_date = last_date
        st.session_state.pending_save_required = False
        st.session_state.pop('confirm_save_mobile', None)
    
    if 'last_analysis_date' in st.session_state:
        st.session_state.last_analysis_date = normalize_date_value(st.session_state.last_analysis_date)

    # Display narrative
    st.markdown(f"""
    <div class="narrative-box">
        {st.session_state.latest_narrative}
    </div>
    """, unsafe_allow_html=True)
    
    # Save confirmation
    current_story_date = normalize_date_value(st.session_state.get('last_analysis_date'))
    if not current_story_date:
        st.warning("Generate or load an analysis before regenerating the story.")
        return

    st.session_state.last_analysis_date = current_story_date
    pending_save = st.session_state.get('pending_save_required', False)
    
    if st.session_state.get('checkbox_reset_date') != current_story_date:
        st.session_state.checkbox_reset_date = current_story_date
        st.session_state.pop('confirm_save_mobile', None)
    
    if pending_save:
        st.warning("Review the story above. Tick to save.")
        
        if st.checkbox("✅ Save this story", key="confirm_save_mobile"):
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
            st.session_state.pop('confirm_save_mobile', None)
            
            st.success("💾 Story saved!")
            st.rerun()
    else:
        if st.session_state.get('last_saved_narrative_date') == current_story_date:
            st.success("💾 Saved to history")
    
    # Compact feedback section
    st.markdown("---")
    with st.expander("💬 Regenerate with Feedback"):
        st.caption("Not satisfied? Provide feedback to improve")
        feedback = st.text_area(
            "Your feedback:",
            height=80,
            key="mobile_feedback",
            placeholder="What should be different?"
        )
        
        if st.button("🔄 Regenerate", use_container_width=True):
            if feedback.strip():
                with st.spinner("🤔 Regenerating..."):
                    update_narrative_with_feedback(current_story_date, feedback)
                    
                    current_mode = st.session_state.config_thresholds.get('mode', 'Free')
                    current_model = st.session_state.config_thresholds.get('claude_model', 'claude-3-5-haiku-20241022')
                    
                    from modules.data import get_entry_by_date
                    entry = get_entry_by_date(current_story_date)
                    
                    if entry:
                        df = load_data()
                        current_idx = df[df['date'] == current_story_date].index[0]
                        previous = df.iloc[current_idx - 1].to_dict() if current_idx > 0 else None
                        changes = get_metric_changes(entry, previous)
                        
                        new_narrative, error = analyze_with_narrative(
                            entry, previous, changes,
                            mode=current_mode,
                            model=current_model
                        )
                        
                        if error:
                            st.error(error)
                        else:
                            st.session_state.latest_narrative = new_narrative
                            st.session_state.latest_metrics = dict(entry)
                            st.session_state.latest_metrics['recommendation'] = new_narrative
                            st.session_state.pending_save_required = True
                            st.session_state.pending_save_mode = 'update'
                            st.session_state.pending_feedback_text = feedback
                            st.session_state.pop('confirm_save_mobile', None)
                            
                            st.success("✅ Story regenerated. Review and save.")
                            st.rerun()
            else:
                st.warning("Enter feedback first")

if __name__ == "__main__":
    main()
