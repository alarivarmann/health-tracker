# Alerting Logic Test Suite

## Overview
Comprehensive test suite that validates threshold coverage and alerting logic for all metrics in the metrics tracker application.

## Test Files

### `test_alerting.py`
Main test suite with 7 comprehensive tests:

1. **Threshold Coverage Test**
   - Validates that all metrics have defined thresholds
   - Checks both high-value-is-problem metrics (e.g., anxiety, chaos)
   - Checks low-value-is-problem metrics (e.g., sleep, autonomy)

2. **Severity Classification Test**
   - Tests the core logic for classifying metrics into categories
   - Validates: severity_increase, continuous_issue, safe
   - Covers edge cases: first entry, stable values, rising values

3. **High Value Alert Test**
   - Ensures metrics >= threshold trigger alerts
   - Tests with values like anxiety=9, chaos=7, etc.

4. **Low Value Alert Test**
   - Ensures inverse metrics trigger alerts when too low
   - Tests sleep_quality=2, jira_autonomy=3, etc.

5. **Questions Configuration Test**
   - Validates QUESTIONS array has all required fields
   - Checks: key, label, category for all 16 metrics

6. **Insights Coverage Test**
   - Verifies insights module checks important metrics
   - Ensures actionable recommendations are generated

7. **Continuous Issue Detection Test**
   - Validates persistent high values are flagged
   - Tests both stable values (9→9) and first entries (None→9)

## Running Tests

### Automatic (with preflight checks)
```bash
make start
```
Tests run automatically before the app starts.

### Manual Execution
```bash
# Using the shell script
./test_alerting.sh

# Or directly with Python
uv run python test_alerting.py

# Or with standard Python
python test_alerting.py
```

## Test Output

### Success
```
🚀 Running Alerting Logic Test Suite
============================================================

🧪 Testing threshold coverage...
✅ PASSED: All 15 metrics have thresholds defined

🧪 Testing severity classification...
✅ PASSED: All 7 severity classification tests passed

... (more tests)

============================================================
📊 Test Summary
============================================================
✅ PASSED: Threshold Coverage
✅ PASSED: Severity Classification
✅ PASSED: High Value Alerts
✅ PASSED: Low Value Alerts
✅ PASSED: Questions Configuration
✅ PASSED: Insights Coverage
✅ PASSED: Continuous Issue Detection
============================================================
Results: 7/7 tests passed
============================================================

🎉 All tests passed! Alerting logic is working correctly.
```

### Failure
When tests fail, you'll see detailed output:
```
❌ FAILED: Missing thresholds detected:
  ❌ Missing threshold: urgent_alignment_high for metric 'urgent_alignment'
  ❌ Missing threshold: deadline_pressure_high for metric 'deadline_pressure'
```

## Adding New Tests

To add a new test:

1. Create a test function in `test_alerting.py`:
```python
def test_my_new_feature():
    """Test description."""
    print("\n🧪 Testing my new feature...")
    
    # Your test logic here
    if something_wrong:
        print("❌ FAILED: Description")
        return False
    
    print("✅ PASSED: Description")
    return True
```

2. Add it to the `run_all_tests()` function:
```python
tests = [
    # ... existing tests
    ("My New Feature", test_my_new_feature),
]
```

## Integration with Makefile

The `Makefile` automatically runs these tests via `preflight_check.py`:

```makefile
start: test
    @echo "🚀 Starting Metrics Tracker..."
    @uv run streamlit run metrics_app.py
```

If tests fail, the app won't start and you'll see the error output.

## Continuous Integration

These tests ensure:
- ✅ No metric is left without a threshold
- ✅ All alerting logic works correctly
- ✅ High and low values trigger appropriate alerts
- ✅ Severity classification is consistent
- ✅ Configuration is complete and valid

Run tests before committing changes to ensure no regressions.
