# Dynamic Configuration - Real-time Threshold Adjustment

## Changes Made (13 November 2025 - Phase 5)

### 🎯 Problem Addressed
Configuration parameters were read-only from `.env` file. Users couldn't experiment with different sensitivity levels without restarting the app.

### ✅ Solution Implemented

**Made ALL thresholds adjustable in real-time via the UI.**

The `.env` file now provides **starting values only**. Users can adjust any parameter during their session and see immediate results in their analysis.

---

## Key Features

### 1. **Session State Storage**
All thresholds are stored in `st.session_state.config_thresholds`:
- Initialized from `.env` defaults on first load
- Persists across tab switches
- Updated in real-time as sliders/inputs change

### 2. **Editable Configuration Tab**
```
⚙️ Configuration

[🔄 Reset to Defaults]  ← Restore .env values

🎯 Severity Classification Rules
┌────────────────┬────────────────┐
│ Problem: [6  ] │ Increase: [1.0]│  ← Number inputs
└────────────────┴────────────────┘

🚨 Alert Thresholds
┌───────────────────────────────────┐
│ [Slider: Project Chaos High]      │  ← Interactive sliders
│ [Slider: Anxiety High]            │
│ [Slider: Sleep Poor]              │
│ ...12 more sliders...             │
└───────────────────────────────────┘
```

### 3. **Dynamic Analysis**
Analysis tab uses current session state values:
```
⚙️ Analysis based on: Problem Threshold = 5, Increase Threshold = 0.5
   → Adjust in Configuration tab
```

### 4. **Reset to Defaults**
One-click button restores all `.env` values.

---

## Architecture Changes

### Session State Structure
```python
st.session_state.config_thresholds = {
    'problem_threshold': 6,        # Core classification
    'increase_threshold': 1.0,     # Core classification
    'anxiety_high': 7,             # Alert threshold
    'anxiety_medium': 5,           # Alert threshold
    'irritability_high': 8,
    'sleep_poor': 4,
    'chaos_high': 7,
    'meetings_high': 6,
    'quiet_low': 4,
    'saying_no_low': 4,
    'requests_high': 8,
    'stress_high': 8,
    'jira_low': 4,
    'delivery_log': 6
}
```

### Function Signature Updates

#### modules/severity.py
```python
# BEFORE
def classify_metric_severity(current_value, previous_value, metric_key, metric_label):

# AFTER
def classify_metric_severity(current_value, previous_value, metric_key, metric_label,
                           problem_threshold=None, increase_threshold=None):

# BEFORE
def analyze_metrics_severity(metrics, previous):

# AFTER
def analyze_metrics_severity(metrics, previous, 
                            problem_threshold=None, increase_threshold=None):
```

#### modules/insights.py
```python
# BEFORE
def generate_quick_insights(metrics, previous):

# AFTER
def generate_quick_insights(metrics, previous, custom_thresholds=None):

# BEFORE
def should_recommend_delivery_log(metrics):

# AFTER
def should_recommend_delivery_log(metrics, custom_thresholds=None):
```

### Call Chain
```
Configuration Tab (UI)
    ↓ updates
Session State (st.session_state.config_thresholds)
    ↓ read by
Analysis Tab
    ↓ passes to
analyze_metrics_severity(problem_threshold=..., increase_threshold=...)
    ↓ passes to
classify_metric_severity(problem_threshold=..., increase_threshold=...)
    ↓ uses for classification
```

---

## User Workflows

### Workflow 1: Increase Sensitivity
**Goal:** Catch issues earlier

1. Go to Configuration tab
2. Adjust **Problem Threshold** from 6 → **5**
3. Adjust **Increase Threshold** from 1.0 → **0.5**
4. Adjust individual metrics (e.g., Anxiety High from 7 → **6**)
5. Go to Analysis tab
6. See more issues flagged as red/yellow

### Workflow 2: Decrease Sensitivity
**Goal:** Reduce noise, focus on severe issues only

1. Go to Configuration tab
2. Adjust **Problem Threshold** from 6 → **7**
3. Adjust **Increase Threshold** from 1.0 → **2.0**
4. Adjust individual metrics (e.g., Chaos High from 7 → **8**)
5. Go to Analysis tab
6. See fewer issues, only most critical

### Workflow 3: Experiment & Reset
**Goal:** Test different configurations

1. Adjust multiple thresholds
2. Run analysis, see results
3. Click **🔄 Reset to Defaults**
4. Back to original `.env` values
5. Compare results

---

## Implementation Details

### Initialization (main function)
```python
if 'config_thresholds' not in st.session_state:
    from modules.config import THRESHOLDS
    st.session_state.config_thresholds = {
        'problem_threshold': 6,
        'increase_threshold': 1.0,
        # ... all other thresholds from THRESHOLDS dict
    }
```

### Configuration Tab - Core Parameters
```python
st.session_state.config_thresholds['problem_threshold'] = st.number_input(
    "Problem Threshold",
    min_value=1,
    max_value=10,
    value=st.session_state.config_thresholds['problem_threshold'],
    key="problem_threshold_input"
)
```

### Configuration Tab - Alert Thresholds
```python
st.session_state.config_thresholds['anxiety_high'] = st.slider(
    "Anxiety (High)",
    1, 10,
    st.session_state.config_thresholds['anxiety_high'],
    key="anxiety_high_slider"
)
```

### Analysis Tab - Using Custom Thresholds
```python
problem_threshold = st.session_state.config_thresholds['problem_threshold']
increase_threshold = st.session_state.config_thresholds['increase_threshold']

severity_results = analyze_metrics_severity(
    metrics, 
    previous, 
    problem_threshold=problem_threshold,
    increase_threshold=increase_threshold
)

should_recommend, triggered = should_recommend_delivery_log(
    metrics, 
    st.session_state.config_thresholds
)
```

### Reset Button
```python
if st.button("🔄 Reset to Defaults"):
    st.session_state.config_thresholds = {
        'problem_threshold': 6,
        'increase_threshold': 1.0,
        'anxiety_high': THRESHOLDS['anxiety_high'],
        # ... restore all from .env
    }
    st.success("✅ Reset to defaults")
    st.rerun()
```

---

## Backward Compatibility

### .env File Still Works
All defaults are read from `.env` on first load:
```bash
ANXIETY_HIGH=7
PROJECT_CHAOS_HIGH=7
SLEEP_POOR=4
# ... etc
```

### No Breaking Changes
- Modules still have default parameters
- Functions fall back to module constants if thresholds not provided
- Old code would still work (though not using dynamic values)

---

## Benefits

### 1. **Real-time Experimentation**
- Adjust sensitivity on the fly
- See immediate impact on classification
- No app restart needed

### 2. **Personalization**
- Different users can have different sensitivity
- Fine-tune to personal tolerance levels
- Adapt as circumstances change

### 3. **Education**
- Learn how thresholds affect results
- Understand severity classification better
- See cause-and-effect of parameter changes

### 4. **Flexibility**
- `.env` = starting point
- Session = experimental playground
- Can always reset to defaults

### 5. **Transparency**
- Analysis shows which parameters were used
- Users know exactly what rules produced results
- Full control over classification logic

---

## Edge Cases Handled

### 1. **Missing Session State**
Initialized on first load from `.env` defaults

### 2. **Invalid Values**
Number inputs and sliders constrain to valid ranges (1-10, 0.1-5.0)

### 3. **Reset During Active Session**
`st.rerun()` ensures clean state after reset

### 4. **Tab Switching**
Session state persists across tabs

### 5. **Multiple Analyses**
Each analysis uses current session state values

---

## Testing Checklist

### Configuration Tab
- [ ] All thresholds editable via sliders/inputs
- [ ] Values persist when switching tabs
- [ ] Reset button restores .env defaults
- [ ] Classification logic expandable shows current values
- [ ] No errors on value changes

### Analysis Tab
- [ ] Banner shows current threshold values
- [ ] Classification uses session state thresholds
- [ ] Changing config and re-analyzing shows different results
- [ ] Alert thresholds respect session state

### Experimentation
- [ ] Lower problem threshold → more red issues
- [ ] Lower increase threshold → more sensitive to changes
- [ ] Higher thresholds → fewer issues flagged
- [ ] Reset works correctly

---

## Files Modified

1. **metrics_app.py**
   - `main()`: Initialize session state for thresholds
   - `show_configuration_tab()`: Made all parameters editable
   - `show_analysis_tab()`: Use session state thresholds

2. **modules/severity.py**
   - `classify_metric_severity()`: Accept custom thresholds
   - `analyze_metrics_severity()`: Accept custom thresholds

3. **modules/insights.py**
   - `generate_quick_insights()`: Accept custom thresholds
   - `should_recommend_delivery_log()`: Accept custom thresholds

---

## Performance Impact

- ✅ No additional API calls
- ✅ No file I/O during adjustment
- ✅ Minimal memory (small dict in session state)
- ✅ Instant UI updates (Streamlit reactivity)

---

## Summary

✅ All thresholds now adjustable in real-time  
✅ .env file provides starting values only  
✅ Session state stores user adjustments  
✅ Analysis uses current session values  
✅ Reset button restores defaults  
✅ No app restart needed  
✅ Backward compatible  
✅ Full transparency of active parameters
