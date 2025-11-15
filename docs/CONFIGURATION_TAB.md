# Configuration Tab Addition

## Changes Made (13 November 2025 - Phase 4)

### 🎯 Problem Addressed
Users couldn't see what threshold parameters were being used to classify their metrics. The classification seemed like a "black box."

### ✅ Solution Implemented

#### 1. **New Configuration Tab** (First Tab)
Added `⚙️ Configuration` as the first tab to expose all parameters.

**Contents:**
- **Severity Classification Rules**
  - Problem Threshold (currently: 6)
  - Increase Threshold (currently: 1.0)

- **Alert Thresholds** (3-column layout)
  - Work Metrics (chaos, meetings, requests, jira)
  - Well-being Metrics (anxiety, irritability, stress)
  - Productivity Metrics (sleep, quiet blocks, saying no)

- **Classification Logic** (expandable)
  - Explains how each category is determined
  - Shows the scoring formulas
  - Examples of what triggers each alert level

- **API Configuration**
  - Shows if Anthropic API key is configured
  - Masked display for security

- **Configuration Files**
  - Lists all available environment variables
  - Instructions for modification
  - Tips on sensitivity adjustment

#### 2. **Parameters Display in Analysis Tab**
Added a banner at the top of the Analysis tab showing active parameters:

```
⚙️ Classification Parameters: Problem Threshold = 6, Increase Threshold = 1.0
   → See Configuration tab for details
```

This provides:
- ✅ Transparency about what rules are being applied
- ✅ Context for understanding the findings
- ✅ Link to full configuration details

---

## Tab Structure (New)

```
[⚙️ Configuration] [📝 New Entry] [📊 Dashboard] [📖 Analysis] [ℹ️ About]
       ↑
    NEW - First tab
```

---

## Configuration Tab Layout

### Section 1: Severity Classification Rules (2 columns)

```
┌─────────────────────┬─────────────────────┐
│ Problem Threshold   │ Increase Threshold  │
│       6             │       1.0           │
│ Values >= this are  │ Delta >= this is    │
│ problematic         │ significant         │
└─────────────────────┴─────────────────────┘
```

### Section 2: Alert Thresholds (3 columns)

```
┌──────────────┬──────────────┬──────────────┐
│ Work Metrics │ Well-being   │ Productivity │
├──────────────┼──────────────┼──────────────┤
│ Chaos: 7     │ Anxiety: 7   │ Sleep: 4     │
│ Meetings: 6  │ Irritab: 8   │ Quiet: 4     │
│ Requests: 8  │ Stress: 8    │ Saying No: 4 │
│ Jira: 4      │ (etc.)       │ Del Log: 6   │
└──────────────┴──────────────┴──────────────┘
```

### Section 3: Classification Logic (Expandable)

Shows formulas:
- 🚨 Problem Severity Increase: current >= 6 AND delta >= 1.0
- ⚠️ Continuous Issue: current >= 6 AND delta < 1.0
- ✅ Safe: current < 6 OR not increasing

Scoring:
- Problem Severity: `current × 10 + delta × 5`
- Continuous: `current × 5`
- Safe: `0`

---

## Analysis Tab Changes

### Before
```
📖 Your Metrics Analysis

🔍 Findings | 📖 Story
```

### After
```
📖 Your Metrics Analysis

⚙️ Classification Parameters: Problem Threshold = 6, Increase Threshold = 1.0
   → See Configuration tab for details

🔍 Findings | 📖 Story
```

**Benefits:**
- Users know what parameters produced these results
- Can verify thresholds match expectations
- Can adjust .env and restart if needed
- Provides transparency and trust

---

## Environment Variables Exposed

All threshold parameters from `.env`:

### Severity Classification
- `PROBLEM_THRESHOLD` (hardcoded in severity.py: 6)
- `INCREASE_THRESHOLD` (hardcoded in severity.py: 1.0)

### Individual Metric Thresholds
- `ANXIETY_HIGH` (default: 7)
- `ANXIETY_MEDIUM` (default: 5)
- `IRRITABILITY_HIGH` (default: 8)
- `SLEEP_POOR` (default: 4)
- `PROJECT_CHAOS_HIGH` (default: 7)
- `UNWANTED_MEETINGS_HIGH` (default: 6)
- `QUIET_BLOCKS_LOW` (default: 4)
- `SAYING_NO_LOW` (default: 4)
- `UNMET_REQUESTS_HIGH` (default: 8)
- `STRESS_OUTSIDE_HIGH` (default: 8)
- `JIRA_AUTONOMY_LOW` (default: 4)
- `DELIVERY_LOG_THRESHOLD` (default: 6)

### API
- `ANTHROPIC_API_KEY`

---

## How to Modify Thresholds

### Option 1: Edit .env file
```bash
# Make system more sensitive
ANXIETY_HIGH=6  # was 7
PROBLEM_THRESHOLD=5  # Note: Currently hardcoded in severity.py

# Make system less sensitive  
ANXIETY_HIGH=8  # was 7
```

### Option 2: Edit severity.py (for classification thresholds)
```python
# In modules/severity.py
PROBLEM_THRESHOLD = 5  # More sensitive
INCREASE_THRESHOLD = 0.5  # Catch smaller changes
```

After changes:
1. Restart the app (`make start`)
2. Go to Configuration tab to verify
3. Run new analysis to see effect

---

## User Benefits

### 1. **Transparency**
- No more "black box" classifications
- Understand why metrics are red/yellow/green
- See exact thresholds being used

### 2. **Customization**
- Know what to change in .env
- Understand impact of threshold adjustments
- Can tune sensitivity to personal needs

### 3. **Trust**
- See the mechanical rules clearly
- Verify parameters match expectations
- Understand scoring methodology

### 4. **Education**
- Learn how the system works
- Understand classification logic
- See examples of each category

---

## Code Structure

### New Function
```python
def show_configuration_tab():
    """Configuration Tab - View and understand thresholds"""
    # Import thresholds
    from modules.config import THRESHOLDS, ANTHROPIC_API_KEY
    from modules.severity import PROBLEM_THRESHOLD, INCREASE_THRESHOLD
    
    # Display sections:
    # 1. Severity Classification Rules
    # 2. Alert Thresholds (3 columns)
    # 3. Classification Logic (expandable)
    # 4. API Configuration
    # 5. Configuration Files Info
```

### Updated Function
```python
def show_analysis_tab():
    """Analysis Tab - Shows parameters banner"""
    from modules.severity import PROBLEM_THRESHOLD, INCREASE_THRESHOLD
    
    # Display parameters banner
    st.markdown(f"⚙️ Parameters: Problem={PROBLEM_THRESHOLD}, Increase={INCREASE_THRESHOLD}")
    
    # ... rest of analysis
```

---

## Visual Design

### Configuration Tab
- Clean metric cards for thresholds
- 3-column layout for organized viewing
- Help text for each parameter
- Expandable detailed explanation
- Info boxes for tips

### Analysis Tab Banner
- Light blue background (#e8f4f8)
- Blue border on left
- Small font (0.85em) - not distracting
- Link to Configuration tab on right

---

## Files Modified

1. `/Users/alavar/metrics-tracker/metrics_app.py`
   - Added `show_configuration_tab()` function
   - Updated tab structure (5 tabs now)
   - Added parameters banner in `show_analysis_tab()`

---

## Testing Checklist

- [ ] Configuration tab appears first
- [ ] All thresholds display correctly
- [ ] Values match .env file (or defaults)
- [ ] Classification logic expandable works
- [ ] API key shows masked (if configured)
- [ ] Analysis tab shows parameters banner
- [ ] Banner displays correct values
- [ ] 3-column layout looks good
- [ ] Help text appears on hover

---

## Summary

✅ New Configuration tab (first tab)  
✅ Exposes all threshold parameters  
✅ Shows classification logic clearly  
✅ API configuration status visible  
✅ Analysis tab references parameters  
✅ Complete transparency of rules  
✅ Instructions for customization  
✅ Educational about the system
