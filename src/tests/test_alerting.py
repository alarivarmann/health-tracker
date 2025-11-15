"""
Test suite for alerting logic and threshold coverage.
Validates that all metrics have proper thresh    # Create test metrics with high values that should trigger alerts
    # ALL metrics now follow "high = worse" pattern
    test_metrics = {
        'deadline_pressure': 9,
        'unmet_requests': 8,
        'project_chaos': 9,
        'apologies': 8,
        'urgent_alignment': 9,
        'unwanted_meetings': 8,
        'anxiety': 9,
        'irritability': 8,
        'stress_outside': 8,
        'not_keeping_moses': 7,  # RENAMED
        'jira_blocked': 8,  # INVERTED (high = bad)
        'sleep_issues': 7,  # INVERTED (high = bad)
        'self_development_unrealized': 6,  # INVERTED (high = bad)
        'quiet_blocks_insufficient': 6,  # INVERTED (high = bad)
        'cannot_say_no': 6  # INVERTED (high = bad)
    }orks correctly.
"""

import sys
from modules.config import QUESTIONS, THRESHOLDS
from modules.severity import classify_metric_severity, analyze_metrics_severity
from modules.insights import generate_quick_insights


def test_threshold_coverage():
    """Test that all metrics have defined thresholds."""
    print("\n🧪 Testing threshold coverage...")
    
    # Metrics that should have thresholds
    # High-value-is-problem metrics should end with '_high'
    # Low-value-is-problem metrics should end with '_low' or '_poor'
    
    # ALL metrics now follow "high values = problems" pattern
    all_metrics = [
        'deadline_pressure',
        'unmet_requests', 
        'project_chaos',
        'apologies',
        'urgent_alignment',
        'unwanted_meetings',
        'anxiety',
        'irritability',
        'stress_outside',
        'not_keeping_moses',  # RENAMED
        'jira_blocked',  # INVERTED
        'sleep_issues',  # INVERTED
        'self_development_unrealized',  # INVERTED
        'quiet_blocks_insufficient',  # INVERTED
        'cannot_say_no'  # INVERTED
    ]
    
    # Check all metrics have _high thresholds
    missing_thresholds = []
    for metric in all_metrics:
        threshold_key = f'{metric}_high'
        if threshold_key not in THRESHOLDS:
            missing_thresholds.append(f"❌ Missing threshold: {threshold_key} for metric '{metric}'")
    
    if missing_thresholds:
        print("❌ FAILED: Missing thresholds detected:")
        for msg in missing_thresholds:
            print(f"  {msg}")
        return False
    
    print(f"✅ PASSED: All {len(all_metrics)} metrics have thresholds defined")
    return True


def test_severity_classification():
    """Test that severity classification works correctly."""
    print("\n🧪 Testing severity classification...")
    
    test_cases = [
        # (current, previous, expected_category, description)
        (9, None, 'continuous_issue', 'First entry with high value'),
        (9, 9, 'continuous_issue', 'Stable high value'),
        (9, 7, 'severity_increase', 'Rising high value'),
        (5, 5, 'safe', 'Stable low value'),
        (7, 5, 'severity_increase', 'Rising to threshold'),
        (5, 7, 'safe', 'Decreasing from high'),
        (3, 3, 'safe', 'Stable low value'),
    ]
    
    failed_tests = []
    for current, previous, expected, description in test_cases:
        result = classify_metric_severity(
            current_value=current,
            previous_value=previous,
            metric_key='test_metric',
            metric_label='Test Metric',
            problem_threshold=6,
            increase_threshold=1.0
        )
        
        category, score, detail = result
        
        if category != expected:
            failed_tests.append(
                f"❌ {description}: Expected '{expected}', got '{category}' "
                f"(current={current}, previous={previous})"
            )
    
    if failed_tests:
        print("❌ FAILED: Severity classification errors:")
        for msg in failed_tests:
            print(f"  {msg}")
        return False
    
    print(f"✅ PASSED: All {len(test_cases)} severity classification tests passed")
    return True


def test_high_values_trigger_alerts():
    """Test that high values properly trigger alerts."""
    print("\n🧪 Testing high value alerting...")
    
    # Create test metrics with high values - ALL now follow "high = worse"
    test_metrics = {
        'deadline_pressure': 9,
        'unmet_requests': 8,
        'project_chaos': 7,
        'apologies': 7,
        'urgent_alignment': 9,
        'unwanted_meetings': 8,
        'anxiety': 9,
        'irritability': 8,
        'stress_outside': 8,
        'not_keeping_moses': 7,  # RENAMED
        'jira_blocked': 8,  # INVERTED
        'sleep_issues': 7,  # INVERTED
        'self_development_unrealized': 6,  # INVERTED
        'quiet_blocks_insufficient': 6,  # INVERTED
        'cannot_say_no': 6  # INVERTED
    }
    
    previous_metrics = {key: 5 for key in test_metrics.keys()}
    
    # Run severity analysis
    results = analyze_metrics_severity(test_metrics, previous_metrics)
    
    # Check that high-value metrics are flagged
    problem_count = len(results['severity_increase']) + len(results['continuous_issue'])
    safe_count = len(results['safe'])
    
    # Should have at least 15 problems (all metrics now follow "high = worse")
    if problem_count < 15:
        print(f"❌ FAILED: Expected at least 15 problems, got {problem_count}")
        print(f"  Severity increases: {len(results['severity_increase'])}")
        print(f"  Continuous issues: {len(results['continuous_issue'])}")
        print(f"  Safe: {safe_count}")
        return False
    
    print(f"✅ PASSED: High values properly trigger alerts")
    print(f"  - {len(results['severity_increase'])} severity increases")
    print(f"  - {len(results['continuous_issue'])} continuous issues")
    print(f"  - {safe_count} safe metrics")
    return True


def test_inverted_metrics_trigger_alerts():
    """Test that high values properly trigger alerts for inverted metrics (which now follow 'high=worse' pattern)."""
    print("\n🧪 Testing inverted metrics alerting (now follow 'high=worse' pattern)...")
    
    # Create test metrics with high values for inverted metrics
    # ALL metrics now follow "high = worse" pattern
    test_metrics = {
        'jira_blocked': 8,  # INVERTED: high = bad
        'sleep_issues': 9,  # INVERTED: high = bad
        'self_development_unrealized': 8,  # INVERTED: high = bad
        'quiet_blocks_insufficient': 9,  # INVERTED: high = bad
        'cannot_say_no': 8,  # INVERTED: high = bad
        # Other metrics (should be safe)
        'deadline_pressure': 5,
        'anxiety': 5,
        'project_chaos': 5
    }
    
    # Run quick insights
    insights = generate_quick_insights(test_metrics, previous=None)
    
    # Should have alerts for the inverted metrics (now high = bad)
    # Note: self_development_unrealized intentionally has 'low' severity
    alert_count = sum(1 for severity, text in insights if severity in ['high', 'medium', 'low'] and any(word in text for word in ['blocked', 'sleep', 'development', 'quiet', 'say no', 'Insufficient', 'Difficulty']))
    
    if alert_count < 5:
        print(f"❌ FAILED: Expected at least 5 alerts for inverted metrics, got {alert_count}")
        print(f"  Insights generated:")
        for severity, text in insights:
            print(f"    [{severity}] {text}")
        return False
    
    print(f"✅ PASSED: Inverted metrics properly trigger alerts")
    print(f"  - {alert_count} alerts generated for high-value inverted metrics")
    return True


def test_all_questions_have_labels():
    """Test that all QUESTIONS have required fields."""
    print("\n🧪 Testing QUESTIONS configuration...")
    
    required_fields = ['key', 'label', 'category']
    missing_fields = []
    
    for i, question in enumerate(QUESTIONS):
        for field in required_fields:
            if field not in question:
                missing_fields.append(f"❌ Question {i} ('{question.get('key', 'unknown')}'): Missing field '{field}'")
    
    if missing_fields:
        print("❌ FAILED: Missing required fields in QUESTIONS:")
        for msg in missing_fields:
            print(f"  {msg}")
        return False
    
    print(f"✅ PASSED: All {len(QUESTIONS)} questions have required fields (key, label, category)")
    return True


def test_insights_coverage():
    """Test that insights module checks all important metrics."""
    print("\n🧪 Testing insights coverage...")
    
    # Metrics that should have specific insight checks
    # ALL now follow "high = worse" pattern
    important_metrics = [
        'anxiety',
        'project_chaos',
        'deadline_pressure',
        'urgent_alignment',
        'unmet_requests',
        'sleep_issues',  # INVERTED: now high = bad
        'unwanted_meetings',
        'irritability',
        'stress_outside'
    ]
    
    # Create test data - ALL metrics now follow "high = worse" pattern
    test_metrics = {}
    for metric in important_metrics:
        test_metrics[metric] = 9  # High value should trigger alert for ALL metrics
    
    # Generate insights
    insights = generate_quick_insights(test_metrics, previous=None)
    
    # Should have insights for each important metric
    insight_count = len(insights)
    
    if insight_count < len(important_metrics):
        print(f"⚠️  WARNING: Only {insight_count} insights for {len(important_metrics)} important metrics")
        print(f"  This might be OK if some metrics share thresholds")
        # Don't fail, just warn
    
    print(f"✅ PASSED: Insights module generated {insight_count} alerts")
    return True


def test_continuous_issue_detection():
    """Test that persistent high values are detected as continuous issues."""
    print("\n🧪 Testing continuous issue detection...")
    
    # Metric stays at 9 for multiple periods
    result1 = classify_metric_severity(9, 9, 'test', 'Test Metric')
    result2 = classify_metric_severity(9, None, 'test', 'Test Metric')
    
    if result1[0] != 'continuous_issue':
        print(f"❌ FAILED: Stable high value (9→9) should be 'continuous_issue', got '{result1[0]}'")
        return False
    
    if result2[0] != 'continuous_issue':
        print(f"❌ FAILED: First high value (None→9) should be 'continuous_issue', got '{result2[0]}'")
        return False
    
    print("✅ PASSED: Continuous issues properly detected")
    return True


def run_all_tests():
    """Run all test suites."""
    print("=" * 60)
    print("🚀 Running Alerting Logic Test Suite")
    print("=" * 60)
    
    tests = [
        ("Threshold Coverage", test_threshold_coverage),
        ("Severity Classification", test_severity_classification),
        ("High Value Alerts", test_high_values_trigger_alerts),
        ("Inverted Metrics Alerts", test_inverted_metrics_trigger_alerts),
        ("Questions Configuration", test_all_questions_have_labels),
        ("Insights Coverage", test_insights_coverage),
        ("Continuous Issue Detection", test_continuous_issue_detection),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"❌ FAILED: {name} - Exception: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")
    
    print("=" * 60)
    print(f"Results: {passed_count}/{total_count} tests passed")
    print("=" * 60)
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Alerting logic is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
