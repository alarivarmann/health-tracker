"""
Severity classifier - mechanical rules to identify critical issues
Inspired by statistical anomaly detection patterns
"""
import math

from .config import THRESHOLDS

# Severity classification constants
PROBLEM_THRESHOLD = 6  # Values at or above this are problematic
SAFE_THRESHOLD = 6     # Values below this are safe
INCREASE_THRESHOLD = 1.0  # Delta indicating significant increase

def classify_metric_severity(current_value, previous_value, metric_key, metric_label, 
                           problem_threshold=None, increase_threshold=None):
    """
    Classify a single metric into severity categories using mechanical rules.
    
    Rules:
    1. Problem Severity Increase: Rising AND currently >= problem_threshold
    2. Continuous Issues: Static (or minor change) AND currently >= problem_threshold 
    3. Safe: Below problem_threshold AND not significantly increasing
    
    Args:
        current_value: Current metric value
        previous_value: Previous metric value
        metric_key: Metric identifier
        metric_label: Human-readable metric name
        problem_threshold: Override default PROBLEM_THRESHOLD
        increase_threshold: Override default INCREASE_THRESHOLD
    
    Returns:
        tuple: (category, severity_score, detail_dict)
        category: 'severity_increase' | 'continuous_issue' | 'safe'
        severity_score: float for ranking importance
    """
    # Use provided thresholds or fall back to defaults
    prob_thresh = problem_threshold if problem_threshold is not None else PROBLEM_THRESHOLD
    incr_thresh = increase_threshold if increase_threshold is not None else INCREASE_THRESHOLD
    
    # Handle None/missing values
    if current_value is None:
        return 'safe', 0, None

    try:
        current = float(current_value)
    except (ValueError, TypeError):
        return 'safe', 0, None

    if math.isnan(current):
        return 'safe', 0, None

    # Calculate delta and normalize previous value
    previous = None
    delta = 0.0

    if previous_value is not None:
        try:
            previous_candidate = float(previous_value)
            if not math.isnan(previous_candidate):
                previous = previous_candidate
                delta = current - previous
        except (ValueError, TypeError):
            previous = None
            delta = 0.0
    
    # Classification logic
    is_high = current >= prob_thresh
    is_rising = delta >= incr_thresh if previous is not None else False
    is_stable = abs(delta) < incr_thresh if previous is not None else False
    
    detail = {
        'key': metric_key,
        'label': metric_label,
        'current': current,
        'previous': previous,
        'delta': delta if previous is not None else None,
        'is_high': is_high,
        'is_rising': is_rising
    }
    
    # Rule 1: Problem Severity Increase (worst case)
    if is_rising and is_high:
        # Severity score: higher value + higher delta = more severe
        severity_score = current * 10 + delta * 5
        return 'severity_increase', severity_score, detail
    
    # Rule 2: Continuous Issues (medium severity)
    if is_stable and is_high:
        # Severity score based on how high the value is
        severity_score = current * 5
        return 'continuous_issue', severity_score, detail
    
    # Rule 2b: First-time high value (treat as continuous issue)
    if is_high and previous is None:
        severity_score = current * 5
        return 'continuous_issue', severity_score, detail
    
    # Rule 3: Safe (low priority)
    # Below threshold OR not significantly problematic
    return 'safe', 0, detail


def analyze_metrics_severity(metrics, previous, problem_threshold=None, increase_threshold=None, custom_thresholds=None):
    """
    Analyze all metrics and classify them into severity categories.
    
    Args:
        metrics: Current metrics dict
        previous: Previous metrics dict
        problem_threshold: Override default PROBLEM_THRESHOLD
        increase_threshold: Override default INCREASE_THRESHOLD
    
    Returns:
        dict with keys:
        - 'severity_increase': list of (severity_score, detail_dict)
        - 'continuous_issue': list of (severity_score, detail_dict)
        - 'safe': list of (severity_score, detail_dict)
    """
    from .config import QUESTIONS
    thresholds_map = custom_thresholds if custom_thresholds is not None else THRESHOLDS
    
    results = {
        'severity_increase': [],
        'continuous_issue': [],
        'safe': []
    }
    
    # Build a map of metric keys to labels
    metric_labels = {q['key']: q['label'] for q in QUESTIONS}
    
    for key, current_value in metrics.items():
        if key == 'date' or key not in metric_labels:
            continue
        
        # Skip yes/no metrics
        if isinstance(current_value, str):
            continue
        
        previous_value = previous.get(key) if previous else None
        
        threshold_key = f"{key}_high"
        metric_threshold = None
        if threshold_key in thresholds_map:
            metric_threshold = thresholds_map.get(threshold_key)

        category, severity_score, detail = classify_metric_severity(
            current_value, 
            previous_value, 
            key, 
            metric_labels.get(key, key),
            problem_threshold=metric_threshold if metric_threshold is not None else problem_threshold,
            increase_threshold=increase_threshold
        )
        
        if detail:
            results[category].append((severity_score, detail))
    
    # Sort each category by severity score (descending)
    for category in results:
        results[category].sort(key=lambda x: x[0], reverse=True)
    
    return results


def get_top_issues(severity_results, max_items=5):
    """
    Get the top N most important issues across all categories.
    Priority: severity_increase > continuous_issue > safe
    
    Returns:
        list of tuples: (category, severity_score, detail_dict)
    """
    # Collect all non-safe issues with their category
    all_issues = []
    
    # Add severity increases (highest priority)
    for score, detail in severity_results['severity_increase']:
        all_issues.append(('severity_increase', score, detail))
    
    # Add continuous issues (medium priority)
    for score, detail in severity_results['continuous_issue']:
        all_issues.append(('continuous_issue', score, detail))
    
    # Sort by score (already sorted within categories, but merge them)
    all_issues.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N
    return all_issues[:max_items]


def calculate_severity_statistics(severity_results):
    """
    Calculate summary statistics about severity distribution.
    
    Returns:
        dict with counts and percentages
    """
    total_metrics = (
        len(severity_results['severity_increase']) +
        len(severity_results['continuous_issue']) +
        len(severity_results['safe'])
    )
    
    if total_metrics == 0:
        return {
            'total': 0,
            'severity_increase_count': 0,
            'continuous_issue_count': 0,
            'safe_count': 0,
            'problem_percentage': 0
        }
    
    severity_count = len(severity_results['severity_increase'])
    continuous_count = len(severity_results['continuous_issue'])
    safe_count = len(severity_results['safe'])
    
    problem_count = severity_count + continuous_count
    problem_percentage = (problem_count / total_metrics) * 100 if total_metrics > 0 else 0
    
    return {
        'total': total_metrics,
        'severity_increase_count': severity_count,
        'continuous_issue_count': continuous_count,
        'safe_count': safe_count,
        'problem_percentage': problem_percentage
    }
