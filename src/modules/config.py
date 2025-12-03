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
    # ADHD primary signals (high values = problems)
    'signal_body_tension_high': int(os.getenv('SIGNAL_BODY_TENSION_HIGH', 7)),
    'signal_mind_noise_high': int(os.getenv('SIGNAL_MIND_NOISE_HIGH', 7)),
    'signal_focus_friction_high': int(os.getenv('SIGNAL_FOCUS_FRICTION_HIGH', 7)),
    'signal_emotion_wave_high': int(os.getenv('SIGNAL_EMOTION_WAVE_HIGH', 7)),
    'signal_energy_drain_high': int(os.getenv('SIGNAL_ENERGY_DRAIN_HIGH', 7)),
    'signal_tension_headache_high': int(os.getenv('SIGNAL_TENSION_HEADACHE_HIGH', 7)),
    'flag_rushing_loop_high': int(os.getenv('FLAG_RUSHING_LOOP_HIGH', 1)),
    'flag_skipped_reset_high': int(os.getenv('FLAG_SKIPPED_RESET_HIGH', 1)),
    'flag_people_pleasing_high': int(os.getenv('FLAG_PEOPLE_PLEASING_HIGH', 1)),
    'flag_physical_exercise_high': int(os.getenv('FLAG_PHYSICAL_EXERCISE_HIGH', 1)),

    # Work metrics (ALL follow "high values = problems" pattern)
    'deadline_pressure_high': int(os.getenv('DEADLINE_PRESSURE_HIGH', 7)),
    'unmet_requests_high': int(os.getenv('UNMET_REQUESTS_HIGH', 7)),
    'project_chaos_high': int(os.getenv('PROJECT_CHAOS_HIGH', 7)),
    'apologies_high': int(os.getenv('APOLOGIES_HIGH', 6)),
    'urgent_alignment_high': int(os.getenv('URGENT_ALIGNMENT_HIGH', 7)),
    'unwanted_meetings_high': int(os.getenv('UNWANTED_MEETINGS_HIGH', 6)),
    'jira_blocked_high': int(os.getenv('JIRA_BLOCKED_HIGH', 7)),  # INVERTED: was jira_autonomy_low

    # Individual optional metrics (ALL follow "high values = problems" pattern)
    'anxiety_high': int(os.getenv('ANXIETY_HIGH', 7)),
    'anxiety_medium': int(os.getenv('ANXIETY_MEDIUM', 5)),
    'irritability_high': int(os.getenv('IRRITABILITY_HIGH', 7)),
    'stress_outside_high': int(os.getenv('STRESS_OUTSIDE_HIGH', 7)),
    'no_ownership_high': int(os.getenv('NO_OWNERSHIP_HIGH', 7)),
    'sleep_issues_high': int(os.getenv('SLEEP_ISSUES_HIGH', 7)),
    'quiet_blocks_insufficient_high': int(os.getenv('QUIET_BLOCKS_INSUFFICIENT_HIGH', 7)),
    'cannot_say_no_high': int(os.getenv('CANNOT_SAY_NO_HIGH', 7)),
    'self_development_unrealized_high': int(os.getenv('SELF_DEVELOPMENT_UNREALIZED_HIGH', 7)),
    'schedule_not_following_high': int(os.getenv('SCHEDULE_NOT_FOLLOWING_HIGH', 7)),
    'pain_levels_high': int(os.getenv('PAIN_LEVELS_HIGH', 6)),

    # Special thresholds
    'delivery_log': int(os.getenv('DELIVERY_LOG_THRESHOLD', 6))
}

PROMPT_WEEKDAYS = [int(d) for d in os.getenv('PROMPT_WEEKDAYS', '2,4').split(',')]

QUESTIONS = [
    # ADHD primary metrics (required)
    {
        'key': 'signal_body_tension',
        'label': 'Body tension / restlessness',
        'category': 'adhd_primary',
        'required': True,
        'type': 'slider',
        'min': 0,
        'max': 10,
        'description': 'How tight or restless does your body feel right now? 0 = relaxed, 10 = jittery or clenched.'
    },
    {
        'key': 'signal_mind_noise',
        'label': 'Mind noise / racing thoughts',
        'category': 'adhd_primary',
        'required': True,
        'type': 'slider',
        'min': 0,
        'max': 10,
        'description': 'Are your thoughts calm or racing? 0 = calm/steady, 10 = swirling or loud.'
    },
    {
        'key': 'signal_focus_friction',
        'label': 'Focus friction (task switching feels sticky)',
        'category': 'adhd_primary',
        'required': True,
        'type': 'slider',
        'min': 0,
        'max': 10,
        'description': 'Notice how easy it is to start or switch tasks. 0 = smooth, 10 = stuck or avoidant.'
    },
    {
        'key': 'signal_emotion_wave',
        'label': 'Emotional swell / irritability',
        'category': 'adhd_primary',
        'required': True,
        'type': 'slider',
        'min': 0,
        'max': 10,
        'description': 'How strong are emotional swings right now? 0 = level, 10 = high spikes or sharp edges.'
    },
    {
        'key': 'signal_energy_drain',
        'label': 'Battery already drained?',
        'category': 'adhd_primary',
        'required': True,
        'type': 'slider',
        'min': 0,
        'max': 10,
        'description': 'Where is your energy? 0 = charged, 10 = nearly empty even before midday.'
    },
    {
        'key': 'signal_tension_headache',
        'label': 'Tension headache intensity',
        'category': 'adhd_primary',
        'required': True,
        'type': 'slider',
        'min': 0,
        'max': 10,
        'description': 'Notice any tightness or pressure in your head/neck. 0 = relaxed, 10 = severe tension headache.'
    },
    {
        'key': 'flag_rushing_loop',
        'label': "I'm rushing or stacking tasks to catch up",
        'category': 'adhd_primary',
        'required': True,
        'type': 'yesno',
        'description': 'Answer yes if you notice yourself speeding up, skipping steps, or multitasking frantically.'
    },
    {
        'key': 'flag_skipped_reset',
        'label': 'Skipped a reset or bio break',
        'category': 'adhd_primary',
        'required': True,
        'type': 'yesno',
        'description': 'Did you skip a planned pause, meal, or movement that usually keeps you balanced?'
    },
    {
        'key': 'flag_people_pleasing',
        'label': 'Said yes while already overloaded',
        'category': 'adhd_primary',
        'required': True,
        'type': 'yesno',
        'description': 'Mark yes if you agreed to something mainly to avoid friction, even though you lacked capacity.'
    },
    {
        'key': 'flag_physical_exercise',
        'label': 'Did physical exercise today',
        'category': 'adhd_primary',
        'required': True,
        'type': 'yesno',
        'description': 'Did you do any intentional physical activity today? (walk, run, gym, sports, etc.)'
    },

    # Work metrics (all optional, higher = worse)
    {'key': 'deadline_pressure', 'label': 'Urgent deadline pressure', 'category': 'work', 'required': False, 'type': 'slider', 'min': 0, 'max': 10},
    {'key': 'unmet_requests', 'label': 'Requests I feel I cannot meet', 'category': 'work', 'required': False, 'type': 'slider', 'min': 0, 'max': 10},
    {'key': 'project_chaos', 'label': 'Project chaos', 'category': 'work', 'required': False, 'type': 'slider', 'min': 0, 'max': 10},
    {'key': 'apologies', 'label': 'Apologies made in client meetings', 'category': 'work', 'required': False, 'type': 'slider', 'min': 0, 'max': 10},
    {'key': 'jira_blocked', 'label': 'Jira stories blocked by others', 'category': 'work', 'required': False, 'type': 'slider', 'min': 0, 'max': 10},
    {'key': 'urgent_alignment', 'label': 'Urgent stakeholder alignment required', 'category': 'work', 'required': False, 'type': 'slider', 'min': 0, 'max': 10},
    {'key': 'unwanted_meetings', 'label': 'Unwanted meetings attended', 'category': 'work', 'required': False, 'type': 'slider', 'min': 0, 'max': 10},

    # Individual optional metrics (legacy signals)
    {'key': 'anxiety', 'label': 'Anxiety', 'category': 'individual', 'required': False, 'type': 'slider', 'min': 0, 'max': 10},
    {'key': 'irritability', 'label': 'Irritability', 'category': 'individual', 'required': False, 'type': 'slider', 'min': 0, 'max': 10},
    {'key': 'stress_outside', 'label': 'Stress outside work', 'category': 'individual', 'required': False, 'type': 'slider', 'min': 0, 'max': 10},
    {'key': 'sleep_issues', 'label': 'Sleep issues', 'category': 'individual', 'required': False, 'type': 'slider', 'min': 0, 'max': 10},
    {'key': 'self_development_unrealized', 'label': 'Self-development time not realized', 'category': 'individual', 'required': False, 'type': 'slider', 'min': 0, 'max': 10},
    {'key': 'schedule_not_following', 'label': 'Not following daily schedule', 'category': 'individual', 'required': False, 'type': 'slider', 'min': 0, 'max': 10},
    {'key': 'pain_levels', 'label': 'Average pain levels', 'category': 'individual', 'required': False, 'type': 'slider', 'min': 0, 'max': 10},
    {'key': 'new_horizon', 'label': 'New project horizon emerging?', 'category': 'individual', 'type': 'yesno', 'required': False},
    {'key': 'quiet_blocks_insufficient', 'label': 'Insufficient quiet work blocks', 'category': 'individual', 'required': False, 'type': 'slider', 'min': 0, 'max': 10},
    {'key': 'cannot_say_no', 'label': 'Cannot say no to unwanted requests', 'category': 'individual', 'required': False, 'type': 'slider', 'min': 0, 'max': 10},
    {'key': 'no_ownership', 'label': 'No Ownership (even self-development)', 'category': 'individual', 'required': False, 'type': 'slider', 'min': 0, 'max': 10}
]
