"""
Insights module - generates quick insights without API calls
"""
from .config import THRESHOLDS

def generate_quick_insights(metrics, previous, custom_thresholds=None):
    # Use custom thresholds if provided, otherwise use defaults from config
    thresholds = custom_thresholds if custom_thresholds else THRESHOLDS
    
    insights = []
    
    # ALL metrics now follow "high values = problems" pattern
    if metrics.get('anxiety') and metrics['anxiety'] >= thresholds.get('anxiety_high', 7):
        insights.append(('high', f"⚠️ High anxiety ({metrics['anxiety']}/10). Use nVNS + 10 min walk."))
    if metrics.get('project_chaos') and metrics['project_chaos'] >= thresholds.get('project_chaos_high', 7):
        insights.append(('high', f"⚠️ High project chaos ({metrics['project_chaos']}/10). Activate Anti-Chaos Routine."))
    if metrics.get('deadline_pressure') and metrics['deadline_pressure'] >= thresholds.get('deadline_pressure_high', 7):
        insights.append(('high', f"⚠️ High deadline pressure ({metrics['deadline_pressure']}/10). Review priorities."))
    if metrics.get('urgent_alignment') and metrics['urgent_alignment'] >= thresholds.get('urgent_alignment_high', 7):
        insights.append(('high', f"⚠️ High urgent alignment needed ({metrics['urgent_alignment']}/10). Schedule stakeholder sync."))
    if metrics.get('unmet_requests') and metrics['unmet_requests'] >= thresholds.get('unmet_requests_high', 7):
        insights.append(('high', f"⚠️ High unmet requests ({metrics['unmet_requests']}/10). Consider delegation or pushback."))
    if metrics.get('irritability') and metrics['irritability'] >= thresholds.get('irritability_high', 7):
        insights.append(('medium', f"⚡ High irritability ({metrics['irritability']}/10). Take a break."))
    if metrics.get('stress_outside') and metrics['stress_outside'] >= thresholds.get('stress_outside_high', 7):
        insights.append(('medium', f"⚡ High external stress ({metrics['stress_outside']}/10). Practice self-care."))
    if metrics.get('apologies') and metrics['apologies'] >= thresholds.get('apologies_high', 6):
        insights.append(('medium', f"⚡ Many apologies ({metrics['apologies']}/10). Review commitments."))
    if metrics.get('unwanted_meetings') and metrics['unwanted_meetings'] >= thresholds.get('unwanted_meetings_high', 6):
        insights.append(('medium', f"⚡ Many unwanted meetings ({metrics['unwanted_meetings']}/10). Use skip-meeting template."))
    
    # INVERTED metrics (now follow "high = worse" pattern like all others)
    if metrics.get('not_keeping_moses') and metrics['not_keeping_moses'] >= thresholds.get('not_keeping_moses_high', 7):
        insights.append(('medium', f"⚡ Struggling to keep Moses at bay ({metrics['not_keeping_moses']}/10). Address root causes."))
    if metrics.get('sleep_issues') and metrics['sleep_issues'] >= thresholds.get('sleep_issues_high', 7):
        insights.append(('high', f"⚠️ Significant sleep issues ({metrics['sleep_issues']}/10). Review Sleep Recovery Plan."))
    if metrics.get('jira_blocked') and metrics['jira_blocked'] >= thresholds.get('jira_blocked_high', 7):
        insights.append(('medium', f"⚡ Many Jira stories blocked ({metrics['jira_blocked']}/10). Discuss with leadership."))
    if metrics.get('quiet_blocks_insufficient') and metrics['quiet_blocks_insufficient'] >= thresholds.get('quiet_blocks_insufficient_high', 7):
        insights.append(('medium', f"⚡ Insufficient quiet work blocks ({metrics['quiet_blocks_insufficient']}/10). Protect your 2-hour deep work anchor."))
    if metrics.get('cannot_say_no') and metrics['cannot_say_no'] >= thresholds.get('cannot_say_no_high', 7):
        insights.append(('medium', f"⚡ Difficulty saying no ({metrics['cannot_say_no']}/10). Practice setting boundaries."))
    if metrics.get('self_development_unrealized') and metrics['self_development_unrealized'] >= thresholds.get('self_development_unrealized_high', 7):
        insights.append(('low', f"💡 Self-development time not realized ({metrics['self_development_unrealized']}/10). Schedule learning blocks."))
    # Positive trends (all metrics use same pattern now: decrease = improvement)
    if previous:
        if metrics.get('anxiety') and previous.get('anxiety'):
            try:
                if float(metrics['anxiety']) < float(previous['anxiety']):
                    delta = float(previous['anxiety']) - float(metrics['anxiety'])
                    insights.append(('low', f"✅ Anxiety decreased by {delta:.1f} - great progress!"))
            except:
                pass
        if metrics.get('sleep_issues') and previous.get('sleep_issues'):
            try:
                if float(metrics['sleep_issues']) < float(previous['sleep_issues']):
                    delta = float(previous['sleep_issues']) - float(metrics['sleep_issues'])
                    insights.append(('low', f"✅ Sleep issues decreased by {delta:.1f} - improving!"))
            except:
                pass
    if not insights:
        insights.append(('low', '✅ All metrics within healthy ranges. Keep it up!'))
    return insights

def should_recommend_delivery_log(metrics, custom_thresholds=None):
    # Use custom thresholds if provided, otherwise use defaults from config
    thresholds = custom_thresholds if custom_thresholds else THRESHOLDS
    delivery_threshold = thresholds.get('delivery_log', THRESHOLDS['delivery_log'])
    
    triggered = []
    check_metrics = [
        ('deadline_pressure', 'Urgent deadline pressure'),
        ('unmet_requests', 'Unmet requests'),
        ('project_chaos', 'Project chaos'),
        ('unwanted_meetings', 'Unwanted meetings'),
        ('anxiety', 'Anxiety'),
        ('irritability', 'Irritability')
    ]
    for key, label in check_metrics:
        if metrics.get(key) and metrics[key] >= delivery_threshold:
            triggered.append(f"{label} ({metrics[key]}/10)")
    return len(triggered) > 0, triggered
