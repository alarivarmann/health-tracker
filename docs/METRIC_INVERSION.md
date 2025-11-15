# Metric Inversion Summary

## Changes Made

All inverse metrics have been **inverted** so that **ALL metrics now follow the same pattern: higher = worse**.

### Metric Renames

| Old Name (inverse logic) | New Name (consistent logic) | Change |
|-------------------------|----------------------------|---------|
| `jira_autonomy` (high=good) | `jira_blocked` (high=bad) | INVERTED |
| `sleep_quality` (high=good) | `sleep_issues` (high=bad) | INVERTED |
| `self_development` (high=good) | `self_development_unrealized` (high=bad) | INVERTED |
| `saying_no` (high=good) | `cannot_say_no` (high=bad) | INVERTED |
| `quiet_blocks` (high=good) | `quiet_blocks_insufficient` (high=bad) | INVERTED |
| `keeping_moses` (low=bad) | `not_keeping_moses` (high=bad) | RENAMED for clarity |

### Label Updates

| Metric Key | New Label |
|-----------|-----------|
| `jira_blocked` | "Jira stories blocked by others" |
| `sleep_issues` | "Sleep issues" |
| `self_development_unrealized` | "Self-development time not realized" |
| `cannot_say_no` | "Cannot say no to unwanted requests" |
| `quiet_blocks_insufficient` | "Insufficient quiet work blocks" |
| `not_keeping_moses` | "Not keeping Moses at bay" |

### Threshold Changes

**Before:** Mixed suffixes (`_high`, `_low`, `_poor`)
```python
'sleep_quality_poor': 4  # Low value = problem
'jira_autonomy_low': 4   # Low value = problem
'saying_no_low': 4       # Low value = problem
```

**After:** Unified `_high` suffix only
```python
'sleep_issues_high': 7  # High value = problem
'jira_blocked_high': 7  # High value = problem
'cannot_say_no_high': 7  # High value = problem
```

### Logic Changes

**Before:**
- High-value metrics: `value >= threshold` → problem
- Low-value metrics: `value <= threshold` → problem
- Two different comparison operators

**After:**
- ALL metrics: `value >= threshold` → problem
- Single unified comparison operator
- Much simpler and less error-prone!

## Files Modified

### Configuration
- ✅ `modules/config.py` - Updated QUESTIONS and THRESHOLDS

### Logic Modules
- ✅ `modules/insights.py` - Changed all `<=` to `>=`, updated metric names
- ✅ `modules/local_narrative.py` - Removed special handling for inverse metrics

### Tests
- ✅ `test_alerting.py` - Updated all test data and expectations
- ✅ `test_user_scenario.py` - Updated metric names
- ✅ `test_narrative_consistency.py` - Updated metric names

## Benefits

### 1. Simplified Logic
- **Before:** Need to check if metric is "inverse" before comparing
- **After:** Always use `>=` for all metrics

### 2. Consistent Mental Model
- **Before:** "High anxiety is bad, but high sleep quality is good"
- **After:** "High values are ALWAYS bad for ALL metrics"

### 3. Easier Threshold Configuration
- **Before:** Remember which metrics use `_high`, `_low`, or `_poor`
- **After:** ALL metrics use `_high` suffix

### 4. Fewer Bugs
- **Before:** Easy to use wrong comparison operator
- **After:** Impossible to get wrong - always use `>=`

## Test Results

All 7 alerting tests pass:
- ✅ Threshold Coverage (15 metrics)
- ✅ Severity Classification
- ✅ High Value Alerts
- ✅ Inverted Metrics Alerts
- ✅ Questions Configuration
- ✅ Insights Coverage
- ✅ Continuous Issue Detection

## Migration Guide

If you have existing data with old metric names:

```python
# Add this to data loading code to handle legacy data:
METRIC_RENAMES = {
    'jira_autonomy': 'jira_blocked',
    'sleep_quality': 'sleep_issues',
    'self_development': 'self_development_unrealized',
    'saying_no': 'cannot_say_no',
    'quiet_blocks': 'quiet_blocks_insufficient',
    'keeping_moses': 'not_keeping_moses'
}

METRIC_INVERSIONS = {
    'jira_autonomy': True,    # Invert: 10 - value
    'sleep_quality': True,    # Invert: 10 - value
    'self_development': True,  # Invert: 10 - value
    'saying_no': True,        # Invert: 10 - value
    'quiet_blocks': True,     # Invert: 10 - value
    'keeping_moses': False    # Just rename, don't invert
}

# When loading old data:
for old_name, new_name in METRIC_RENAMES.items():
    if old_name in row:
        if METRIC_INVERSIONS[old_name]:
            row[new_name] = 10 - row[old_name]  # Invert the value
        else:
            row[new_name] = row[old_name]       # Just rename
        del row[old_name]
```

## What's Next

The app is ready to use with the new simplified metric system! All metrics now follow the same "higher = worse" pattern.

Run `make start` to launch the app!
