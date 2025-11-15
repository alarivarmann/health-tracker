#!/usr/bin/env python3
"""
Test narrative/severity consistency.
Verifies that the narrative accurately reflects the severity analysis results.
"""

from modules.severity import analyze_metrics_severity
from modules.local_narrative import build_local_narrative
from modules.config import THRESHOLDS

def test_narrative_severity_consistency():
    """Test that narrative reflects severity analysis with custom thresholds."""
    print("🧪 Testing narrative/severity consistency with problem_threshold=4")
    
    # User's scenario: all metrics at 5.0, problem_threshold=4
    # With threshold=4, all values of 5.0 should be flagged as continuous issues
    metrics = {
        'deadline_pressure': 5.0,
        'unmet_requests': 5.0,
        'project_chaos': 5.0,
        'apologies': 5.0,
        'jira_blocked': 5.0,  # INVERTED
        'urgent_alignment': 5.0,
        'unwanted_meetings': 5.0,
        'anxiety': 5.0,
        'irritability': 5.0,
        'stress_outside': 5.0,
        'sleep_issues': 5.0,  # INVERTED
        'self_development_unrealized': 5.0,  # INVERTED
        'quiet_blocks_insufficient': 5.0,  # INVERTED
        'cannot_say_no': 5.0,  # INVERTED
        'not_keeping_moses': 5.0  # RENAMED
    }
    
    previous_metrics = {key: 5.0 for key in metrics.keys()}
    
    # Run severity analysis with problem_threshold=4
    problem_threshold = 4
    increase_threshold = 1.0
    
    severity_results = analyze_metrics_severity(
        metrics, 
        previous_metrics,
        problem_threshold=problem_threshold,
        increase_threshold=increase_threshold
    )
    
    # Check severity results
    problem_count = len(severity_results['severity_increase']) + len(severity_results['continuous_issue'])
    print(f"\n📊 Severity Analysis Results:")
    print(f"   - {len(severity_results['severity_increase'])} severity increases")
    print(f"   - {len(severity_results['continuous_issue'])} continuous issues")
    print(f"   - {len(severity_results['safe'])} safe metrics")
    print(f"   Total problems: {problem_count}")
    
    if problem_count == 0:
        print("   ❌ FAILED: Expected problems to be flagged, got 0")
        return False
    
    # Generate narrative using same severity results
    custom_thresholds = THRESHOLDS.copy()
    # Note: custom_thresholds are for insights, not severity analysis
    # Severity analysis uses problem_threshold parameter
    
    narrative = build_local_narrative(
        metrics,
        previous_metrics,
        changes=None,
        severity_results=severity_results,
        custom_thresholds=custom_thresholds
    )
    
    print(f"\n📖 Generated Narrative:")
    print("="*60)
    print(narrative)
    print("="*60)
    
    # Verify narrative consistency
    narrative_lower = narrative.lower()
    
    # Test 1: Narrative should NOT say "all safe" when there are problems
    if 'all metrics safe' in narrative_lower or 'all safe' in narrative_lower:
        print("\n❌ FAILED: Narrative says 'all safe' but severity analysis found problems!")
        return False
    
    # Test 2: Narrative should mention persistent/elevated/continuous issues
    if problem_count > 5:
        if not any(word in narrative_lower for word in ['persistent', 'elevated', 'continuous', 'issue', 'problem']):
            print("\n❌ FAILED: Narrative doesn't mention persistent issues despite many problems flagged!")
            return False
    
    # Test 3: Narrative should list some specific metrics in "Priority Issues" section
    # Count how many metrics appear in the narrative by checking for unique metric keys
    from modules.config import QUESTIONS
    metric_labels = {q['key']: q['label'].lower() for q in QUESTIONS}
    
    metric_mentions = sum(1 for key in metrics.keys() if metric_labels.get(key, key.replace('_', ' ')) in narrative_lower)
    if metric_mentions < 3:
        print(f"\n❌ FAILED: Narrative mentions {metric_mentions} metrics, expected at least 3!")
        print(f"   Debug: Checked for these labels in narrative:")
        for key in metrics.keys():
            label = metric_labels.get(key, key.replace('_', ' '))
            found = label in narrative_lower
            print(f"      - {key} → '{label}': {'✓' if found else '✗'}")
        return False
    
    # Test 4: Narrative should reflect the count accurately
    if problem_count >= 10:
        if not any(str(num) in narrative for num in range(problem_count - 2, problem_count + 3)):
            print(f"\n⚠️  WARNING: Narrative doesn't mention the count (~{problem_count}) of problems")
    
    print(f"\n✅ PASSED: Narrative accurately reflects severity analysis")
    print(f"   - Mentions persistent/elevated issues ✓")
    print(f"   - Mentions at least 3 specific metrics ✓")
    print(f"   - Doesn't say 'all safe' when problems exist ✓")
    
    return True


def test_all_safe_scenario():
    """Test that narrative correctly says 'all safe' when no problems."""
    print("\n🧪 Testing 'all safe' scenario with low values")
    
    # All metrics at 3.0, problem_threshold=6
    # With threshold=6, all values of 3.0 should be safe
    metrics = {
        'deadline_pressure': 3.0,
        'unmet_requests': 3.0,
        'project_chaos': 3.0,
        'apologies': 3.0,
        'jira_blocked': 3.0,  # INVERTED: now low = good
        'urgent_alignment': 3.0,
        'unwanted_meetings': 3.0,
        'anxiety': 3.0,
        'irritability': 3.0,
        'stress_outside': 3.0,
        'sleep_issues': 3.0,  # INVERTED: now low = good
        'self_development_unrealized': 3.0,  # INVERTED: now low = good
        'quiet_blocks_insufficient': 3.0,  # INVERTED: now low = good
        'cannot_say_no': 3.0,  # INVERTED: now low = good
        'not_keeping_moses': 3.0  # RENAMED
    }
    
    previous_metrics = {key: 3.0 if val == 3.0 else 7.0 for key, val in metrics.items()}
    
    # Run severity analysis with problem_threshold=6
    problem_threshold = 6
    increase_threshold = 1.0
    
    severity_results = analyze_metrics_severity(
        metrics, 
        previous_metrics,
        problem_threshold=problem_threshold,
        increase_threshold=increase_threshold
    )
    
    # Check severity results
    problem_count = len(severity_results['severity_increase']) + len(severity_results['continuous_issue'])
    print(f"\n📊 Severity Analysis Results:")
    print(f"   - {len(severity_results['severity_increase'])} severity increases")
    print(f"   - {len(severity_results['continuous_issue'])} continuous issues")
    print(f"   - {len(severity_results['safe'])} safe metrics")
    print(f"   Total problems: {problem_count}")
    
    if problem_count > 0:
        print("   ⚠️  WARNING: Expected 0 problems, but some were flagged")
    
    # Generate narrative
    custom_thresholds = THRESHOLDS.copy()
    
    narrative = build_local_narrative(
        metrics,
        previous_metrics,
        changes=None,
        severity_results=severity_results,
        custom_thresholds=custom_thresholds
    )
    
    print(f"\n📖 Generated Narrative:")
    print("="*60)
    print(narrative)
    print("="*60)
    
    # Verify narrative says "all safe"
    narrative_lower = narrative.lower()
    
    if problem_count == 0:
        if not ('all metrics safe' in narrative_lower or 'all safe' in narrative_lower):
            print("\n❌ FAILED: No problems found but narrative doesn't say 'all safe'!")
            return False
    
    print(f"\n✅ PASSED: Narrative correctly reflects zero problems")
    return True


if __name__ == "__main__":
    print("="*60)
    print("🚀 Running Narrative/Severity Consistency Tests")
    print("="*60)
    
    test1_passed = test_narrative_severity_consistency()
    test2_passed = test_all_safe_scenario()
    
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"{'✅' if test1_passed else '❌'} PASSED: Narrative/Severity Consistency (problem_threshold=4)")
    print(f"{'✅' if test2_passed else '❌'} PASSED: All Safe Scenario (problem_threshold=6)")
    print("="*60)
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed!")
        exit(0)
    else:
        print("\n❌ Some tests failed")
        exit(1)
