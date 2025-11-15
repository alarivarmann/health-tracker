#!/usr/bin/env python3
"""
Test user's specific scenario: urgent_alignment = 9 should trigger alerts
"""
from modules.config import THRESHOLDS
from modules.insights import generate_quick_insights
from modules.severity import analyze_metrics_severity

def test_urgent_alignment_alert():
    """Test that urgent_alignment = 9 triggers an alert."""
    print("🧪 Testing user scenario: urgent_alignment = 9")
    print(f"   Threshold: {THRESHOLDS.get('urgent_alignment_high', 'NOT FOUND')}")
    
    # User's scenario
    metrics = {
        'urgent_alignment': 9,
        'deadline_pressure': 5,
        'unmet_requests': 5,
        'project_chaos': 5,
        'apologies': 5,
        'unwanted_meetings': 5,
        'anxiety': 5,
        'irritability': 5,
        'stress_outside': 5,
        'not_keeping_moses': 5,  # RENAMED
        'sleep_issues': 3,  # INVERTED: low = good
        'jira_blocked': 3,  # INVERTED: low = good
        'quiet_blocks_insufficient': 3,  # INVERTED: low = good
        'cannot_say_no': 3,  # INVERTED: low = good
        'self_development_unrealized': 3  # INVERTED: low = good
    }
    
    previous_metrics = {key: 5.0 for key in metrics.keys()}
    
    # Test 1: Severity analysis
    print("\n📊 Severity Analysis:")
    results = analyze_metrics_severity(metrics, previous_metrics)
    
    found_urgent_alignment = False
    for classification, items in results.items():
        for severity_score, detail in items:
            if detail and detail.get('key') == 'urgent_alignment':
                print(f"   ✅ urgent_alignment found in '{classification}' category")
                print(f"      Severity Score: {severity_score}")
                print(f"      Current: {detail.get('current')}/10")
                print(f"      Delta: {detail.get('delta', 'N/A')}")
                found_urgent_alignment = True
    
    if not found_urgent_alignment:
        print("   ❌ urgent_alignment NOT FOUND in severity analysis!")
        print(f"   Results:")
        for cat, items in results.items():
            print(f"      {cat}: {len(items)} items")
            for score, detail in items[:2]:  # Show first 2 items
                print(f"         - {detail.get('key', 'unknown')}: {detail.get('current')}")
        return False
    
    # Test 2: Quick insights
    print("\n💡 Quick Insights:")
    insights = generate_quick_insights(metrics, previous_metrics)
    
    found_insight = False
    for severity, text in insights:
        if 'urgent' in text.lower() or 'alignment' in text.lower():
            print(f"   ✅ [{severity}] {text}")
            found_insight = True
    
    if not found_insight:
        print("   ❌ No insights generated for urgent_alignment!")
        print(f"   All insights: {insights}")
        return False
    
    print("\n🎉 SUCCESS: urgent_alignment = 9 properly triggers alerts!")
    return True

if __name__ == "__main__":
    success = test_urgent_alignment_alert()
    exit(0 if success else 1)
