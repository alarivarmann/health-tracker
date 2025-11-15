#!/bin/bash
# File: ~/metrics-tracker/notify_metrics.sh

# Send macOS notification
osascript -e 'display notification "Time to fill in your metrics!" with title "📊 Metrics Tracker" sound name "Glass"'

# Wait 2 seconds for user to see notification
sleep 2

# Open Streamlit app in default browser
open "http://localhost:8501"