# Narrative/Severity Consistency Fix

## Problem
The **severity analysis** and **narrative/insights** were using different thresholds, causing a mismatch:

**User Scenario:**
- Set `problem_threshold = 4` in Configuration tab
- All metrics at `5.0`
- **Severity panel showed:** "⚠️ 15 continuous issues"
- **Narrative said:** "✅ All metrics within healthy ranges. Keep it up!"

This was completely broken and confusing!

## Root Cause

### Issue 1: Hardcoded Thresholds in Narrative Generation
`modules/local_narrative.py` used hardcoded threshold values (7 for high, 3 for low) instead of respecting the custom thresholds from the Configuration tab.

### Issue 2: Missing Custom Thresholds in Insights
`generate_quick_insights()` was called without passing custom thresholds, so it always used the defaults from `THRESHOLDS` dict.

### Issue 3: Narrative Built from Scratch Instead of Severity Results
The narrative generation re-computed everything using its own hardcoded logic instead of building the story from the actual severity analysis results that were already computed.

## Solution

### 1. Refactored `build_local_narrative()` 
**Changed from:** Computing severity analysis with hardcoded thresholds
**Changed to:** Accepting pre-computed `severity_results` from caller

```python
def build_local_narrative(
    metrics: Dict[str, int],
    previous: Optional[Dict[str, int]] = None,
    changes: Optional[Dict[str, float]] = None,
    severity_results: Optional[Dict] = None,      # NEW!
    custom_thresholds: Optional[Dict] = None      # NEW!
) -> str:
```

Now the narrative:
- Uses the **exact same severity results** that appear in the severity panel
- Builds the story from **actual flagged issues**, not hardcoded thresholds
- Passes custom thresholds to `generate_quick_insights()` for consistency

### 2. Updated `analyze_with_narrative()`
Added parameters to pass through severity results and custom thresholds:

```python
def analyze_with_narrative(
    metrics: Dict[str, int],
    previous: Optional[Dict[str, int]] = None,
    changes: Optional[Dict[str, float]] = None,
    mode: str = 'Free',
    model: str = 'claude-sonnet-4-20250514',
    severity_results: Optional[Dict] = None,      # NEW!
    custom_thresholds: Optional[Dict] = None      # NEW!
) -> Tuple[Optional[str], Optional[str]]:
```

### 3. Updated Call Sites in `metrics_app.py`

**Input Tab (line ~525):**
```python
# For Free mode, compute severity results with custom thresholds
if current_mode == 'Free':
    custom_thresholds = THRESHOLDS.copy()
    # Apply user overrides
    for key, value in st.session_state.config_thresholds.items():
        if key in custom_thresholds:
            custom_thresholds[key] = value
    
    # Compute severity with same thresholds
    problem_threshold = st.session_state.config_thresholds.get('problem_threshold', 6)
    increase_threshold = st.session_state.config_thresholds.get('increase_threshold', 1.0)
    severity_results = analyze_metrics_severity(
        metrics, previous,
        problem_threshold=problem_threshold,
        increase_threshold=increase_threshold
    )

narrative, error = analyze_with_narrative(
    metrics, previous, changes,
    mode=current_mode,
    model=current_model,
    severity_results=severity_results,       # Pass results
    custom_thresholds=custom_thresholds      # Pass thresholds
)
```

**Dashboard Tab (line ~806):**
```python
# Use custom thresholds from configuration
custom_thresholds = THRESHOLDS.copy()
if 'config_thresholds' in st.session_state:
    for key, value in st.session_state.config_thresholds.items():
        if key in custom_thresholds:
            custom_thresholds[key] = value

insights = generate_quick_insights(
    latest.to_dict(),
    previous.to_dict() if previous is not None else None,
    custom_thresholds=custom_thresholds      # Pass thresholds
)
```

## Verification

### Test 1: Narrative/Severity Consistency
**Scenario:** All metrics at 5.0, problem_threshold=4

**Results:**
```
📊 Severity Analysis Results:
   - 0 severity increases
   - 15 continuous issues
   - 0 safe metrics

📖 Generated Narrative:
⚠️ **Persistent Pressure**: 15 metrics remain elevated, 0 worsening

**Priority Issues:**
- 🟠 **Urgent deadline pressure**: 5.0/10 (persistent)
- 🟠 **Requests I feel I cannot meet**: 5.0/10 (persistent)
- 🟠 **Project chaos**: 5.0/10 (persistent)

**Overall Status:**
- 0 metrics worsening
- 15 metrics persistently elevated
- 0 metrics within safe ranges
```

✅ **PASSED:** Narrative accurately reflects severity analysis!

### Test 2: All Safe Scenario
**Scenario:** All metrics safe with threshold=6

**Results:**
- Narrative says "All Metrics Safe" ✓
- No false positives ✓

### Test 3: Existing Alerting Tests
All 7 alerting tests continue to pass:
- ✅ Threshold Coverage
- ✅ Severity Classification
- ✅ High Value Alerts
- ✅ Low Value Alerts
- ✅ Questions Configuration
- ✅ Insights Coverage
- ✅ Continuous Issue Detection

## Impact

### Before Fix
- **Severity panel:** Shows 15 continuous issues ⚠️
- **Narrative:** "✅ All metrics safe" ✅
- **User:** Completely confused! 😕

### After Fix
- **Severity panel:** Shows 15 continuous issues ⚠️
- **Narrative:** "⚠️ Persistent Pressure: 15 metrics remain elevated" ⚠️
- **Insights:** Lists specific problematic metrics ⚠️
- **User:** Gets consistent, actionable information! 🎯

## Key Takeaway

**Single Source of Truth:** The narrative now builds its story from the **actual severity analysis results** instead of re-computing everything with different thresholds. This ensures:

1. ✅ Severity panel and narrative always match
2. ✅ Custom thresholds from Configuration tab are respected everywhere
3. ✅ No more confusing "everything is safe" when problems exist
4. ✅ Narrative accurately reflects what the user sees in the data

## Testing

Run comprehensive tests:
```bash
make test                              # All preflight checks
uv run python3 test_alerting.py        # Alerting tests (7/7 pass)
uv run python3 test_narrative_consistency.py  # Narrative tests (2/2 pass)
```

All tests pass! ✅
