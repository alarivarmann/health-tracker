"""
Configuration module - loads environment variables and thresholds
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent.parent  # Go up to project root
DATA_FILE = BASE_DIR / 'data' / 'metrics_data.csv'
NARRATIVES_FILE = BASE_DIR / 'data' / 'narratives.json'

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

THRESHOLDS = {
    # Work metrics (ALL follow "high values = problems" pattern)
    'deadline_pressure_high': int(os.getenv('DEADLINE_PRESSURE_HIGH', 7)),
    'unmet_requests_high': int(os.getenv('UNMET_REQUESTS_HIGH', 7)),
    'project_chaos_high': int(os.getenv('PROJECT_CHAOS_HIGH', 7)),
    'apologies_high': int(os.getenv('APOLOGIES_HIGH', 6)),
    'urgent_alignment_high': int(os.getenv('URGENT_ALIGNMENT_HIGH', 7)),
    'unwanted_meetings_high': int(os.getenv('UNWANTED_MEETINGS_HIGH', 6)),
    'jira_blocked_high': int(os.getenv('JIRA_BLOCKED_HIGH', 7)),  # INVERTED: was jira_autonomy_low
    
    # Individual metrics (ALL follow "high values = problems" pattern)
    'anxiety_high': int(os.getenv('ANXIETY_HIGH', 7)),
    'anxiety_medium': int(os.getenv('ANXIETY_MEDIUM', 5)),
    'irritability_high': int(os.getenv('IRRITABILITY_HIGH', 7)),
    'stress_outside_high': int(os.getenv('STRESS_OUTSIDE_HIGH', 7)),
    'not_keeping_moses_high': int(os.getenv('NOT_KEEPING_MOSES_HIGH', 7)),  # RENAMED: was keeping_moses_high
    'sleep_issues_high': int(os.getenv('SLEEP_ISSUES_HIGH', 7)),  # INVERTED: was sleep_quality_poor
    'quiet_blocks_insufficient_high': int(os.getenv('QUIET_BLOCKS_INSUFFICIENT_HIGH', 7)),  # INVERTED: was quiet_blocks_low
    'cannot_say_no_high': int(os.getenv('CANNOT_SAY_NO_HIGH', 7)),  # INVERTED: was saying_no_low
    'self_development_unrealized_high': int(os.getenv('SELF_DEVELOPMENT_UNREALIZED_HIGH', 7)),  # INVERTED: was self_development_low
    'schedule_not_following_high': int(os.getenv('SCHEDULE_NOT_FOLLOWING_HIGH', 7)),  # Measures deviation from daily schedule
    'pain_levels_high': int(os.getenv('PAIN_LEVELS_HIGH', 6)),  # Average pain levels throughout the day
    
    # Special thresholds
    'delivery_log': int(os.getenv('DELIVERY_LOG_THRESHOLD', 6))
}

PROMPT_WEEKDAYS = [int(d) for d in os.getenv('PROMPT_WEEKDAYS', '2,4').split(',')]

QUESTIONS = [
    # Work metrics (all follow "higher = worse" pattern)
    {'key': 'deadline_pressure', 'label': 'Urgent deadline pressure', 'category': 'work'},
    {'key': 'unmet_requests', 'label': 'Requests I feel I cannot meet', 'category': 'work'},
    {'key': 'project_chaos', 'label': 'Project chaos', 'category': 'work'},
    {'key': 'apologies', 'label': 'Apologies made in client meetings', 'category': 'work'},
    {'key': 'jira_blocked', 'label': 'Jira stories blocked by others', 'category': 'work'},
    {'key': 'urgent_alignment', 'label': 'Urgent stakeholder alignment required', 'category': 'work'},
    {'key': 'unwanted_meetings', 'label': 'Unwanted meetings attended', 'category': 'work'},
    
    # Individual metrics (all follow "higher = worse" pattern)
    {'key': 'anxiety', 'label': 'Anxiety', 'category': 'individual'},
    {'key': 'irritability', 'label': 'Irritability', 'category': 'individual'},
    {'key': 'stress_outside', 'label': 'Stress outside work', 'category': 'individual'},
    {'key': 'sleep_issues', 'label': 'Sleep issues', 'category': 'individual'},
    {'key': 'self_development_unrealized', 'label': 'Self-development time not realized', 'category': 'individual'},
    {'key': 'schedule_not_following', 'label': 'Not following daily schedule', 'category': 'individual'},
    {'key': 'pain_levels', 'label': 'Average pain levels', 'category': 'individual'},
    {'key': 'new_horizon', 'label': 'New project horizon emerging?', 'category': 'individual', 'type': 'yesno'},
    {'key': 'quiet_blocks_insufficient', 'label': 'Insufficient quiet work blocks', 'category': 'individual'},
    {'key': 'cannot_say_no', 'label': 'Cannot say no to unwanted requests', 'category': 'individual'},
    {'key': 'not_keeping_moses', 'label': 'Not keeping Moses at bay', 'category': 'individual'}
]
