#!/usr/bin/env python3
"""Complete Metrics Tracker - Streamlit App"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / 'metrics_data.csv'

# Load thresholds from .env
THRESHOLDS = {
    'anxiety_high': int(os.getenv('ANXIETY_HIGH', 7)),
    'sleep_poor': int(os.getenv('SLEEP_POOR', 4)),
    'chaos_high': int(os.getenv('PROJECT_CHAOS_HIGH', 7)),
    'meetings_high': int(os.getenv('UNWANTED_MEETINGS_HIGH', 6)),
    'quiet_low': int(os.getenv('QUIET_BLOCKS_LOW', 4)),
    'requests_high': int(os.getenv('UNMET_REQUESTS_HIGH', 8)),
    'delivery_log': int(os.getenv('DELIVERY_LOG_THRESHOLD', 6))
}

PROMPT_WEEKDAYS = [int(d) for d in os.getenv('PROMPT_WEEKDAYS', '2,4').split(',')]
