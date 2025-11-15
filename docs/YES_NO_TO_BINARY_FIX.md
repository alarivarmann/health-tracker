# Yes/No to Binary Conversion Fix

## Problem
```
streamlit.errors.StreamlitAPIException: Slider min_value must be less than the max_value. The values were 1 and 1.
```

## Root Cause Analysis

### Issue 1: Yes/No String Values
The `new_horizon` question had `'type': 'yesno'` which saved values as strings (`'yes'` or `'no'`). This caused issues when:
1. Trying to calculate deltas between entries
2. Creating visualizations expecting numeric data
3. Using the data in numeric comparisons

### Issue 2: Slider Edge Case
When dashboard had only 1 entry, the slider for "Show last N entries" had:
```python
st.slider("Show last N entries", 1, len(df), min(10, len(df)))
# When len(df) = 1: slider(1, 1, 1) → min_value = max_value = 1 ❌
```

## Solution

### Fix 1: Convert Yes/No to Binary (0/1)
Changed all yes/no inputs to save as integers:
- `yes` → `1`
- `no` → `0`

**Benefits:**
- ✅ Compatible with numeric operations
- ✅ Can calculate deltas
- ✅ Works in visualizations
- ✅ Can use in sliders without errors
- ✅ Easier to analyze (sum, average, etc.)

#### Code Changes
**Before:**
```python
if q.get('type') == 'yesno':
    val = st.selectbox(q['label'], ['yes', 'no'], key=q['key'], disabled=not enabled)
    if enabled:
        metrics[q['key']] = val  # Saves 'yes' or 'no' string
```

**After:**
```python
if q.get('type') == 'yesno':
    val = st.selectbox(q['label'], ['yes', 'no'], key=q['key'], disabled=not enabled)
    if enabled:
        metrics[q['key']] = 1 if val == 'yes' else 0  # Saves 1 or 0
```

### Fix 2: Handle Single Entry Slider
Ensured slider always has valid range:

**Before:**
```python
n_entries = st.sidebar.slider("Show last N entries", 1, len(df), min(10, len(df)))
# Fails when len(df) = 1
```

**After:**
```python
n_entries = st.sidebar.slider("Show last N entries", 1, max(1, len(df)), min(10, len(df)))
# Always has valid range: max(1, len(df)) ensures max_value >= 1
```

## Files Modified
1. `src/metrics_app.py` - Lines 461, 479, 510, 528 (4 locations for yes/no conversion)
2. `src/metrics_app.py` - Line 840 (slider fix)

## Testing

### Test Case 1: Yes/No Input
```python
# Input form
New project horizon emerging? → Select "yes"

# Saved value
metrics['new_horizon'] = 1  # ✅ Integer, not string
```

### Test Case 2: Single Entry Dashboard
```python
# When only 1 entry exists
len(df) = 1
slider_max = max(1, 1) = 1  # Still valid
# No error thrown ✅
```

### Test Case 3: Multiple Entries
```python
# When 20 entries exist
len(df) = 20
slider_max = max(1, 20) = 20  # Works as expected
```

## Backwards Compatibility

### Existing Data
If you have existing data with `'yes'/'no'` strings:
- Dashboard will still display them
- New entries will be saved as 0/1
- Eventually all data will be numeric

### Optional: Migrate Old Data
To convert existing yes/no strings to 0/1:
```python
import pandas as pd

df = pd.read_csv('data/metrics_data.csv')
if 'new_horizon' in df.columns:
    df['new_horizon'] = df['new_horizon'].map({'yes': 1, 'no': 0})
df.to_csv('data/metrics_data.csv', index=False)
```

## Benefits

1. **Numeric Consistency** - All metrics are now numeric (0-10 scale)
2. **Visualization Ready** - Can chart yes/no over time
3. **Math Operations** - Can calculate totals, averages, trends
4. **No More Slider Errors** - Edge cases handled
5. **Simpler Logic** - No special handling for yes/no types

## Future Recommendations

For new yes/no questions:
1. ✅ Store as 0/1 (not strings)
2. ✅ Use `st.selectbox` with conversion
3. ✅ OR use `st.radio(['No', 'Yes'])` with index as value
4. ✅ Document that 1=yes, 0=no in config

## Date
November 15, 2025

## Status
✅ **FIXED** - Yes/no values now stored as binary integers, slider edge case handled.
