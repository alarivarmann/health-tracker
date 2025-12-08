"""
Data module - handles loading, saving, and managing metrics data
"""
import pandas as pd
from datetime import datetime
from .config import DATA_FILE, QUESTIONS

def load_data():
    if not DATA_FILE.exists():
        return pd.DataFrame()
    df = pd.read_csv(DATA_FILE)
    for q in QUESTIONS:
        if q.get('type') != 'yesno' and q['key'] in df.columns:
            df[q['key']] = pd.to_numeric(df[q['key']], errors='coerce')
    return df

def save_entry(metrics):
    df = load_data()
    new_entry = pd.DataFrame([metrics])
    if len(df) == 0:
        df = new_entry
    else:
        df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def get_previous_entry():
    df = load_data()
    if len(df) < 1:
        return None
    return df.iloc[-1].to_dict()

def should_prompt_today():
    from .config import PROMPT_WEEKDAYS
    today = datetime.now()
    weekday = today.isoweekday()
    if weekday not in PROMPT_WEEKDAYS:
        return False, "Not a scheduled day"
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        if len(df) > 0:
            df['date'] = pd.to_datetime(df['date'])
            last_entry = df.iloc[-1]['date'].date()
            if last_entry == today.date():
                return False, "Already filled today"
    return True, "Ready for input!"

def get_metric_changes(current, previous):
    changes = {}
    if not previous:
        return changes
    for q in QUESTIONS:
        if q.get('type') != 'yesno' and q['key'] in current and q['key'] in previous:
            try:
                current_val = float(current[q['key']])
                prev_val = float(previous[q['key']])
                changes[q['key']] = {
                    'current': current_val,
                    'previous': prev_val,
                    'delta': current_val - prev_val,
                    'label': q['label']
                }
            except (ValueError, TypeError):
                pass
    return changes

def update_entry_recommendation(date, recommendation):
    """
    Update the recommendation for a specific date entry.
    Overwrites the existing recommendation (one recommendation per date).
    
    Args:
        date: Date string (YYYY-MM-DD) of the entry to update
        recommendation: New recommendation text to store
    """
    df = load_data()
    if len(df) == 0:
        return False
    
    # Find the row with matching date
    normalized_date = str(date)
    mask = df['date'].astype(str) == normalized_date
    if not mask.any():
        return False
    
    # Update the recommendation column
    df.loc[mask, 'recommendation'] = recommendation
    df.to_csv(DATA_FILE, index=False)
    return True

def get_entry_by_date(date):
    """
    Get a specific entry by date.
    
    Args:
        date: Date string (YYYY-MM-DD)
    
    Returns:
        Dict with entry data, or None if not found
    """
    df = load_data()
    if len(df) == 0:
        return None
    
    mask = df['date'].astype(str) == str(date)
    if not mask.any():
        return None
    
    return df[mask].iloc[0].to_dict()
