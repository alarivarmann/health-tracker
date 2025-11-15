# Quick Reference: Severity Classification System

## Thresholds (modules/severity.py)

```python
PROBLEM_THRESHOLD = 6      # Values >= 6 are problematic
INCREASE_THRESHOLD = 1.0   # Delta >= 1.0 is significant
```

## Classification Logic

| Current Value | Delta | Category | Priority | Color |
|--------------|-------|----------|----------|-------|
| >= 6 | >= +1.0 | Problem Severity Increase | 🚨 Highest | Red |
| >= 6 | < 1.0 (stable) | Continuous Issue | ⚠️ Medium | Yellow |
| < 6 | any | Safe | ✅ Low | Green |

## Scoring Formula

- **Problem Severity Increase**: `current * 10 + delta * 5`
- **Continuous Issue**: `current * 5`
- **Safe**: `0`

Higher score = shown first in top 5 list

## Example Scenarios

### Scenario 1: Rising Problem
- **Anxiety**: 6 → 8 (+2)
- **Classification**: Problem Severity Increase
- **Score**: 8*10 + 2*5 = 90
- **Display**: 🚨 Red card, top of list

### Scenario 2: Stuck Problem
- **Project Chaos**: 7 → 7 (0)
- **Classification**: Continuous Issue
- **Score**: 7*5 = 35
- **Display**: ⚠️ Yellow card, after severity increases

### Scenario 3: Safe Metric
- **Sleep Quality**: 4 → 3 (-1)
- **Classification**: Safe (below threshold)
- **Score**: 0
- **Display**: ✅ Green section, collapsed

## Adjusting Sensitivity

### More Sensitive (catch more issues)
```python
PROBLEM_THRESHOLD = 5    # Lower bar
INCREASE_THRESHOLD = 0.5 # Smaller changes matter
```

### Less Sensitive (only critical issues)
```python
PROBLEM_THRESHOLD = 7    # Higher bar
INCREASE_THRESHOLD = 2.0 # Larger changes required
```

## Module Responsibilities

- **severity.py**: Classification rules (no AI)
- **narratives.py**: AI storytelling instructions
- **insights.py**: Quick threshold alerts
- **metrics_app.py**: UI display orchestration
