"""
Local narrative generation using rule-based analysis.
This module generates narratives without requiring Claude API calls.
"""

from typing import Dict, List, Optional, Tuple
from modules.severity import classify_metric_severity, get_top_issues
from modules.insights import generate_quick_insights
from modules.config import QUESTIONS


def _get_metric_name(key: str) -> str:
    """Get human-readable metric name from question key."""
    for q in QUESTIONS:
        if q['key'] == key:
            return q['label']
    return key.replace('_', ' ').title()


def _analyze_trends(metrics: Dict[str, int], previous: Optional[Dict[str, int]]) -> Dict[str, List[str]]:
    """Analyze metric trends across time periods. ALL metrics now follow 'higher = worse' pattern."""
    trends = {
        'increasing': [],
        'decreasing': [],
        'stable_high': [],
        'stable_low': []
    }
    
    if not previous:
        # No previous data, categorize current values
        for key, value in metrics.items():
            # Skip non-numeric fields
            if not isinstance(value, (int, float)):
                continue
            if value >= 7:
                trends['stable_high'].append(key)
            elif value <= 3:
                trends['stable_low'].append(key)
        return trends
    
    for key, current_value in metrics.items():
        # Skip non-numeric fields (like 'date')
        if not isinstance(current_value, (int, float)):
            continue
            
        prev_value = previous.get(key, current_value)
        # Ensure prev_value is also numeric
        if not isinstance(prev_value, (int, float)):
            prev_value = current_value
            
        delta = current_value - prev_value
        
        # ALL metrics follow same pattern: higher = worse
        if delta >= 2:
            trends['increasing'].append(f"{_get_metric_name(key)} (+{delta})")
        elif delta <= -2:
            trends['decreasing'].append(f"{_get_metric_name(key)} ({delta})")
        elif current_value >= 7:
            trends['stable_high'].append(_get_metric_name(key))
        elif current_value <= 3:
            trends['stable_low'].append(_get_metric_name(key))
    
    return trends


def _identify_correlations(metrics: Dict[str, int]) -> List[str]:
    """Identify potential correlations between metrics. ALL metrics now follow 'higher = worse' pattern."""
    correlations = []
    
    # Work chaos → Anxiety/Stress
    if metrics.get('project_chaos', 0) >= 7 and metrics.get('anxiety', 0) >= 7:
        correlations.append("High project chaos correlates with elevated anxiety")
    
    # Meetings → Insufficient quiet blocks
    if metrics.get('unwanted_meetings', 0) >= 7 and metrics.get('quiet_blocks_insufficient', 0) >= 7:
        correlations.append("Excessive meetings correlate with insufficient quiet work time")
    
    # Sleep issues → Other problems (INVERTED: now sleep_issues with high = bad)
    if metrics.get('sleep_issues', 0) >= 7:
        if metrics.get('anxiety', 0) >= 7:
            correlations.append("Sleep issues correlate with elevated anxiety")
        if metrics.get('irritability', 0) >= 7:
            correlations.append("Sleep issues correlate with increased irritability")
    
    # Cannot say no → Chaos/Requests (INVERTED: now cannot_say_no with high = bad)
    if metrics.get('cannot_say_no', 0) >= 7 and metrics.get('unmet_requests', 0) >= 7:
        correlations.append("Difficulty saying no correlates with high unmet requests")
    
    # Stress spillover
    if metrics.get('stress_outside', 0) >= 7 and metrics.get('irritability', 0) >= 7:
        correlations.append("External stress correlates with increased irritability")
    
    return correlations


def _generate_insights(metrics: Dict[str, int], previous: Optional[Dict[str, int]], trends: Dict[str, List[str]]) -> List[str]:
    """Generate actionable insights based on patterns."""
    insights = []
    
    # Check for severity increases
    if trends['increasing']:
        insights.append(f"**Escalating concerns**: {len(trends['increasing'])} metrics show significant increases")
    
    # Identify primary stress sources
    high_issues = []
    for key, value in metrics.items():
        # Skip non-numeric fields
        if isinstance(value, (int, float)) and value >= 8:
            high_issues.append(_get_metric_name(key))
    
    if high_issues:
        insights.append(f"**Critical areas** requiring immediate attention: {', '.join(high_issues[:3])}")
    
    # Positive trends
    if trends['decreasing']:
        insights.append(f"**Improving areas**: {len(trends['decreasing'])} metrics show positive decreases")
    
    # Stability concerns
    if len(trends['stable_high']) >= 3:
        insights.append(f"**Persistent issues**: {len(trends['stable_high'])} metrics remain consistently elevated")
    
    return insights


def _generate_recommendations(metrics: Dict[str, int], correlations: List[str]) -> List[str]:
    """Generate evidence-based recommendations. ALL metrics now follow 'higher = worse' pattern."""
    recommendations = []
    
    # Sleep intervention (INVERTED: now sleep_issues with high = bad)
    if metrics.get('sleep_issues', 0) >= 7:
        recommendations.append("🛌 **Address sleep issues** - impacts physical health, energy, and cognitive function")
    
    # Boundary setting (INVERTED: now cannot_say_no with high = bad)
    if metrics.get('cannot_say_no', 0) >= 7 and (metrics.get('unmet_requests', 0) >= 7 or metrics.get('unwanted_meetings', 0) >= 7):
        recommendations.append("🚫 **Practice boundary-setting** - declining low-value commitments can reduce overwhelm")
    
    # Chaos management
    if metrics.get('project_chaos', 0) >= 7:
        recommendations.append("📋 **Address project chaos** - clarify priorities, scope, and communication channels")
    
    # Stress management
    if metrics.get('anxiety', 0) >= 7 or metrics.get('stress_outside', 0) >= 7:
        recommendations.append("🧘 **Stress management techniques** - consider mindfulness, exercise, or therapy support")
    
    # Quiet blocks (INVERTED: now quiet_blocks_insufficient with high = bad)
    if metrics.get('quiet_blocks_insufficient', 0) >= 7:
        recommendations.append("⚡ **Protect deep work time** - schedule breaks, reduce meeting load, guard 2-hour quiet blocks")
    
    # Jira blocked (INVERTED: now jira_blocked with high = bad)
    if metrics.get('jira_blocked', 0) >= 7:
        recommendations.append("🎯 **Unblock work** - discuss dependencies and task assignment process with leadership")
    
    return recommendations[:4]  # Limit to top 4


def build_local_narrative(
    metrics: Dict[str, int],
    previous: Optional[Dict[str, int]] = None,
    changes: Optional[Dict[str, float]] = None,
    severity_results: Optional[Dict] = None,
    custom_thresholds: Optional[Dict] = None
) -> str:
    """
    Generate rule-based narrative without AI API calls.
    
    Args:
        metrics: Current metric values
        previous: Previous metric values (optional)
        changes: Calculated changes (optional)
        severity_results: Pre-computed severity analysis results (optional)
        custom_thresholds: Custom threshold dict for insights (optional)
    
    Returns:
        Formatted narrative string
    """
    # Use provided severity results or compute them
    if severity_results is None:
        from modules.severity import analyze_metrics_severity
        severity_results = analyze_metrics_severity(metrics, previous)
    
    # Extract top issues from severity results
    top_issues = []
    for score, detail in severity_results['severity_increase'][:3]:
        top_issues.append(('severity_increase', score, detail))
    
    # Add top continuous issues if we have fewer than 3 severity increases
    if len(top_issues) < 3:
        for score, detail in severity_results['continuous_issue'][:3 - len(top_issues)]:
            top_issues.append(('continuous_issue', score, detail))
    
    # Count problem metrics
    problem_count = len(severity_results['severity_increase']) + len(severity_results['continuous_issue'])
    increasing_count = len(severity_results['severity_increase'])
    continuous_count = len(severity_results['continuous_issue'])
    safe_count = len(severity_results['safe'])
    
    # Build narrative sections based on actual severity results
    narrative_parts = []
    
    # 1. Theme/Summary (based on actual flagged issues)
    if problem_count == 0:
        theme = "✅ **All Metrics Safe**: No issues detected - all metrics within healthy ranges"
    elif increasing_count > 0 and increasing_count >= continuous_count:
        theme = f"📈 **Escalation Alert**: {increasing_count} metrics rising, {continuous_count} persistently elevated"
    elif continuous_count > 0:
        theme = f"⚠️ **Persistent Pressure**: {continuous_count} metrics remain elevated, {increasing_count} worsening"
    else:
        theme = f"📊 **Mixed State**: {problem_count} issues detected, {safe_count} metrics safe"
    
    narrative_parts.append(theme)
    narrative_parts.append("")
    
    # 2. Top Issues (from actual severity results)
    if top_issues:
        narrative_parts.append("**Priority Issues:**")
        for severity_type, score, detail in top_issues:
            emoji = "🔴" if severity_type == 'severity_increase' else "🟠"
            metric_name = detail.get('label', detail.get('key', 'Unknown'))
            current = detail.get('current', '?')
            delta = detail.get('delta', 0)
            
            if severity_type == 'severity_increase':
                narrative_parts.append(f"- {emoji} **{metric_name}**: {current}/10 (↗ +{delta})")
            else:
                narrative_parts.append(f"- {emoji} **{metric_name}**: {current}/10 (persistent)")
        narrative_parts.append("")
    
    # 3. Summary Statistics
    if problem_count > 3:
        narrative_parts.append("**Overall Status:**")
        narrative_parts.append(f"- {increasing_count} metrics worsening")
        narrative_parts.append(f"- {continuous_count} metrics persistently elevated")
        narrative_parts.append(f"- {safe_count} metrics within safe ranges")
        narrative_parts.append("")
    
    # 4. Identify correlations from top issues
    correlations = _identify_correlations(metrics)
    if correlations:
        narrative_parts.append("**Pattern Recognition:**")
        for corr in correlations[:3]:
            narrative_parts.append(f"- 🔗 {corr}")
        narrative_parts.append("")
    
    # 5. Recommendations based on top issues
    if top_issues:
        recommendations = _generate_recommendations(metrics, correlations)
        if recommendations:
            narrative_parts.append("**Recommended Actions:**")
            for rec in recommendations[:4]:
                narrative_parts.append(f"- {rec}")
            narrative_parts.append("")
    
    # 6. Quick insights with custom thresholds
    quick_insights = generate_quick_insights(metrics, previous, custom_thresholds=custom_thresholds)
    high_medium_insights = [(sev, text) for sev, text in quick_insights if sev in ['high', 'medium']]
    
    if high_medium_insights:
        narrative_parts.append("**Immediate Alerts:**")
        for severity, insight_text in high_medium_insights[:5]:
            narrative_parts.append(f"- {insight_text}")
    
    return "\n".join(narrative_parts)
