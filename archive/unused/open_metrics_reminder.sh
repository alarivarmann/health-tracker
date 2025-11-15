#!/bin/bash
# Opens browser to metrics tracker and shows notification

# Check if streamlit is running
if ! lsof -i :8501 > /dev/null 2>&1; then
    # Start streamlit in background if not running
    cd ~/metrics-tracker
    export PATH=$HOME/.local/bin:$PATH
    nohup uv run streamlit run metrics_app.py > /tmp/metrics_streamlit.log 2>&1 &
    sleep 5
fi

# Send notification
osascript -e 'display notification "⏰ Time for your metrics check-in! Fill in your work and individual metrics." with title "Metrics Tracker Reminder 📊" sound name "Glass"'

# Open browser to metrics page
sleep 1
open http://localhost:8501

# Optional: Focus the browser window
osascript -e 'tell application "Google Chrome" to activate' 2>/dev/null || 
osascript -e 'tell application "Safari" to activate' 2>/dev/null

echo "$(date): Opened metrics tracker" >> ~/metrics-tracker/reminder.log
