# Metrics Tracker - Severity Classification Update

## Changes Made (13 November 2025 - Phase 2)

### 🎯 **Problem Statement**
The previous implementation showed ALL metric changes equally, making it hard to focus on what matters. The old three-column layout (Rising/Declining/Stable) didn't distinguish between:
- A metric rising from 3 to 4 (not problematic)
- A metric rising from 7 to 8 (serious issue)
- A metric stable at 7 (continuous problem that needs attention)

### ✅ **Solution: Mechanical Severity Classification**

Inspired by statistical anomaly detection patterns from the `technical-debt` project, we now use **mechanical rules** to classify metrics intelligently.

---

## New Module: `modules/severity.py`

### Classification Rules (Thresholds & Logic)

```python
PROBLEM_THRESHOLD = 6  # Values >= 6 are problematic
INCREASE_THRESHOLD = 1.0  # Delta >= 1.0 is significant increase
```

### Three Categories

#### 1. **Problem Severity Increase** 🚨 (Highest Priority)
- **Rule**: Current value >= 6 AND increasing by >= 1.0
- **Visual**: Red/pink background, red border
- **Example**: Anxiety goes from 6 → 8 (+2)
- **Severity Score**: `current * 10 + delta * 5` (prioritizes high + increasing)

#### 2. **Continuous Issues** ⚠️ (Medium Priority)
- **Rule**: Current value >= 6 AND stable (change < 1.0)
- **Visual**: Yellow/orange background, orange border
- **Example**: Project chaos stable at 7
- **Severity Score**: `current * 5` (prioritizes by absolute value)

#### 3. **Safe** ✅ (Low Priority)
- **Rule**: Current value < 6 OR (below threshold and not increasing)
- **Visual**: Green background, collapsed by default
- **Example**: Sleep quality at 4, Anxiety at 3
- **Severity Score**: 0 (no action needed)

### Key Functions

```python
def classify_metric_severity(current_value, previous_value, metric_key, metric_label)
    # Classifies a single metric using mechanical rules
    # Returns: (category, severity_score, detail_dict)

def analyze_metrics_severity(metrics, previous)
    # Analyzes all metrics
    # Returns: dict with 'severity_increase', 'continuous_issue', 'safe' lists

def get_top_issues(severity_results, max_items=5)
    # Gets top N most important issues
    # Prioritizes severity_increase > continuous_issue
```

---

## Updated Analysis Tab Display

### Before
- Showed ALL metrics in 3 columns (Rising/Declining/Stable)
- No distinction between problematic and non-problematic changes
- Equal visual weight for all items
- Cluttered with unimportant information

### After
- **Top 5 Priority Issues Only** (mechanical selection)
- Clear visual hierarchy:
  1. 🚨 **Problem Severity Increase** - Large red cards, most prominent
  2. ⚠️ **Continuous Issues** - Yellow cards, noticeable but less alarming
  3. ✅ **Safe Zone** - Collapsed expander (low visual weight)
- **Summary Statistics**: Shows count of each category
- **Focus on Action**: Only see what needs attention

### Visual Design

```
📊 Status: 2 increasing problems, 1 continuous issues, 12 metrics in safe zone

┌─────────────────────────────────────────┐
│ 🚨 #1: Anxiety                         │  ← Red/pink, large, prominent
│ 6.0 → 8.0 (+2.0)                       │
│ Category: Problem Severity Increase    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ ⚠️ #2: Project Chaos                   │  ← Yellow, noticeable
│ Stable at 7.0                          │
│ Category: Continuous Issue             │
└─────────────────────────────────────────┘

▼ ✅ Safe Zone (12 metrics)              ← Collapsed, low priority
```

---

## Updated AI Narrative Instructions

### Removed
- "Generate metric changes tables"
- "List individual metric values"
- Instructions to enumerate Rising/Declining/Stable

### Added
```
## NOTE
The UI will automatically display:
- Top priority issues (severity increases, continuous problems)
- Mechanical classification of safe vs problem metrics
- Statistical trend analysis

Your role is to tell the STORY behind the data, not list the data itself.
```

### New Focus
- **Pure storytelling**: Connect metrics causally
- **No data listing**: UI handles the numbers mechanically
- **Pattern recognition**: What influences what?
- **Root causes**: Systemic issues, not individual values

---

## Modular Architecture Maintained

### Separation of Concerns

```
modules/severity.py     ← NEW: Mechanical classification rules
    ↓ uses
modules/config.py       ← Thresholds, questions config
    ↓
metrics_app.py          ← UI display logic
    ↓ calls
modules/analysis.py     ← Claude API for narrative
    ↓ uses
modules/narratives.py   ← Prompt instructions
```

### Why This Structure?

1. **`modules/severity.py`**: All mechanical rules in ONE place
   - Easy to adjust thresholds
   - Test independently
   - No AI calls, pure logic

2. **`modules/narratives.py`**: AI instructions
   - Focuses on storytelling
   - Doesn't duplicate UI logic

3. **`metrics_app.py`**: Display orchestration
   - Combines mechanical + narrative
   - Clean separation of visual concerns

---

## Inspiration: Technical Debt Project

Borrowed concepts from `/technical-debt-main/src/`:

### `calculator.py`
- `dynamic_normalize()`: Adaptive boundary adjustment
- `detect_large_weekly_increase()`: Anomaly detection with thresholds
- Concept: **Mechanical rules + statistical features**

### `tech_debt.py`
- `trend_conclusion()`: Multi-threshold decision logic
- `calculate_top_k_correlations()`: Prioritization by score
- Concept: **Severity scoring + ranking**

### Applied to Metrics Tracker
- ✅ Threshold-based classification (PROBLEM_THRESHOLD = 6)
- ✅ Delta-based anomaly detection (INCREASE_THRESHOLD = 1.0)
- ✅ Severity scoring for prioritization
- ✅ Top-N selection (max 5 issues)
- ✅ Statistical features (current value, delta, trend)

---

## Code Cleanup

### Moved to `cleanup/` folder:
- `metrics-tracker.js` (old Node.js version)
- `metrics-tracker.js.backup`
- `setup.js` (old JavaScript setup script)

**Reason**: Project is now fully Python/Streamlit-based. JavaScript files were from an earlier iteration and are no longer used.

---

## Benefits

### 1. **Focus on What Matters**
- Only see top 5 issues
- Mechanical ranking ensures objectivity
- No cognitive overload from 15+ metrics

### 2. **Clear Severity Levels**
- Visual hierarchy matches urgency
- Red = act now, Yellow = monitor, Green = ignore
- Continuous issues get proper attention (not hidden as "stable")

### 3. **Maintainable Rules**
- All thresholds in one place (`modules/severity.py`)
- Easy to adjust: `PROBLEM_THRESHOLD`, `INCREASE_THRESHOLD`
- Testable without AI API calls

### 4. **Separation of Concerns**
- Mechanical rules: `modules/severity.py`
- AI storytelling: `modules/narratives.py`
- Display logic: `metrics_app.py`
- Each module has ONE job

### 5. **Inspired by Proven Patterns**
- Uses same approach as technical debt analyzer
- Statistical features + mechanical rules
- Anomaly detection with configurable thresholds

---

## Configuration

### Adjusting Thresholds

Edit `modules/severity.py`:

```python
# Make classification more sensitive
PROBLEM_THRESHOLD = 5  # Instead of 6
INCREASE_THRESHOLD = 0.5  # Instead of 1.0

# Or less sensitive
PROBLEM_THRESHOLD = 7
INCREASE_THRESHOLD = 2.0
```

### Changing Top-N Display

Edit `metrics_app.py`:

```python
# Show more/fewer issues
top_issues = get_top_issues(severity_results, max_items=3)  # Instead of 5
```

---

## Testing Recommendations

1. **Submit entry with mixed metrics**:
   - Some high and increasing (anxiety 6→8)
   - Some high but stable (project chaos at 7)
   - Some low (sleep at 3)

2. **Verify top 5 display**:
   - Should show only most severe
   - Red cards for increasing problems
   - Yellow cards for continuous issues
   - Green section collapsed

3. **Check narrative**:
   - Should tell story, not list metrics
   - Should connect patterns
   - Should not duplicate the visual metric display

4. **Adjust thresholds** (in `modules/severity.py`):
   - Test sensitivity
   - Verify ranking changes appropriately

---

## Files Modified

1. **NEW**: `/Users/alavar/metrics-tracker/modules/severity.py`
2. **UPDATED**: `/Users/alavar/metrics-tracker/metrics_app.py`
3. **UPDATED**: `/Users/alavar/metrics-tracker/modules/narratives.py`
4. **MOVED**: JavaScript files to `cleanup/` folder

---

## Summary

✅ Mechanical severity classification (inspired by technical-debt analyzer)  
✅ Top 5 priority issues only  
✅ Clear visual hierarchy (Red > Yellow > Green)  
✅ Modular architecture maintained  
✅ AI focuses on storytelling, not data listing  
✅ Continuous issues properly identified  
✅ JavaScript cleanup completed  
✅ All thresholds configurable in one place
