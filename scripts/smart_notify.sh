#!/bin/bash
LOG_FILE="$HOME/metrics-tracker/logs/notify_prod.log"
LAST_RUN_FILE="$HOME/metrics-tracker/data/.last_prod_run"
PLIST_FILE="$HOME/Library/LaunchAgents/com.metricsTracker.prod.plist"

echo "[$(date)] ========================================" >> "$LOG_FILE"
echo "[$(date)] 🚀 PROD - smart_notify.sh started" >> "$LOG_FILE"

CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_TIME=$(date '+%H:%M')
CURRENT_DAY=$(date +%u)
CURRENT_HOUR=$(date +%H)
CURRENT_MINUTE=$(date +%M)

echo "[$(date)] Current: $(date +%A) ($CURRENT_DAY), Time=$CURRENT_TIME" >> "$LOG_FILE"

# Check if we already ran today
if [ -f "$LAST_RUN_FILE" ]; then
    LAST_RUN_DATE=$(cat "$LAST_RUN_FILE")
    echo "[$(date)] Last run was: $LAST_RUN_DATE" >> "$LOG_FILE"
    
    if [ "$LAST_RUN_DATE" == "$CURRENT_DATE" ]; then
        echo "[$(date)] ⚠️  Already ran today. Skipping." >> "$LOG_FILE"
        exit 0
    fi
fi

echo "[$(date)] ✅ Running metrics notification" >> "$LOG_FILE"

osascript -e 'display notification "⏰ Time to log your metrics!" with title "📊 Metrics Tracker" sound name "Glass"'
echo "[$(date)] ✅ Notification sent" >> "$LOG_FILE"

sleep 1

# Check if Streamlit is running
if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "[$(date)] ✅ Streamlit running, opening browser" >> "$LOG_FILE"
    open "http://localhost:8501"
    echo "[$(date)] ✅ Browser opened" >> "$LOG_FILE"
else
    echo "[$(date)] ⚠️  Streamlit not running, attempting to start..." >> "$LOG_FILE"
    cd "$HOME/metrics-tracker"
    export PATH="$HOME/.local/bin:$PATH"
    nohup uv run streamlit run src/metrics_app.py > /tmp/metrics_streamlit.log 2>&1 &
    sleep 5
    
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        echo "[$(date)] ✅ Streamlit started successfully" >> "$LOG_FILE"
        open "http://localhost:8501"
    else
        echo "[$(date)] ❌ Failed to start Streamlit" >> "$LOG_FILE"
        osascript -e 'display notification "Failed to start Streamlit!" with title "❌ Error" sound name "Basso"'
    fi
fi

echo "$CURRENT_DATE" > "$LAST_RUN_FILE"
echo "[$(date)] ✅ Recorded run for $CURRENT_DATE" >> "$LOG_FILE"
