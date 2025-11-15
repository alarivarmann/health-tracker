#!/bin/bash
LOG_FILE="$HOME/metrics-tracker/notify_prod.log"
LAST_RUN_FILE="$HOME/metrics-tracker/.last_prod_run"
SCHEDULED_TIME_FILE="$HOME/metrics-tracker/.sleep_test_time"

echo "[$(date)] ========================================" >> "$LOG_FILE"
echo "[$(date)] 🧪 SLEEP TEST - smart_notify.sh started" >> "$LOG_FILE"

CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_TIME=$(date '+%H:%M')
CURRENT_MINS=$((10#$(date +%H) * 60 + 10#$(date +%M)))

echo "[$(date)] Current: $(date +%A), Time=$CURRENT_TIME" >> "$LOG_FILE"

# Check if we already ran today
if [ -f "$LAST_RUN_FILE" ]; then
    LAST_RUN_DATE=$(cat "$LAST_RUN_FILE")
    echo "[$(date)] Last run was: $LAST_RUN_DATE" >> "$LOG_FILE"
    
    if [ "$LAST_RUN_DATE" == "$CURRENT_DATE" ]; then
        echo "[$(date)] ⚠️  Already ran today. Skipping." >> "$LOG_FILE"
        exit 0
    fi
fi

# Read the scheduled time
if [ ! -f "$SCHEDULED_TIME_FILE" ]; then
    echo "[$(date)] ❌ No scheduled time file found" >> "$LOG_FILE"
    exit 1
fi

SCHEDULED_TIME=$(cat "$SCHEDULED_TIME_FILE")
SCHEDULED_HOUR=$(echo $SCHEDULED_TIME | cut -d: -f1)
SCHEDULED_MINUTE=$(echo $SCHEDULED_TIME | cut -d: -f2)
SCHEDULED_MINS=$((10#$SCHEDULED_HOUR * 60 + 10#$SCHEDULED_MINUTE))
GRACE_PERIOD_MINS=1440  # 1 day grace period for missed schedules

echo "[$(date)] Scheduled time: $SCHEDULED_TIME (mins: $SCHEDULED_MINS)" >> "$LOG_FILE"
echo "[$(date)] Current time: $CURRENT_TIME (mins: $CURRENT_MINS)" >> "$LOG_FILE"

# Calculate time difference
TIME_DIFF=$((CURRENT_MINS - SCHEDULED_MINS))

# Check if within grace period
if [ $TIME_DIFF -lt 0 ]; then
    echo "[$(date)] ⏰ Not yet time. Scheduled: $SCHEDULED_TIME, Current: $CURRENT_TIME" >> "$LOG_FILE"
    echo "[$(date)] Skipping (will run at scheduled time)" >> "$LOG_FILE"
    exit 0
elif [ $TIME_DIFF -gt $GRACE_PERIOD_MINS ]; then
    echo "[$(date)] ⏭️  Too late. $TIME_DIFF mins after scheduled time (grace period: $GRACE_PERIOD_MINS mins expired)" >> "$LOG_FILE"
    exit 0
fi

echo "[$(date)] ✅ SLEEP TEST: Within grace period ($TIME_DIFF mins after scheduled time)" >> "$LOG_FILE"

osascript -e 'display notification "⏰ SLEEP TEST: Woke up after scheduled time!" with title "📊 Metrics Tracker TEST" sound name "Glass"'
echo "[$(date)] ✅ Notification sent" >> "$LOG_FILE"

sleep 1

if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "[$(date)] ✅ Streamlit running, opening browser" >> "$LOG_FILE"
    open "http://localhost:8501"
    echo "[$(date)] ✅ Browser opened" >> "$LOG_FILE"
else
    echo "[$(date)] ⚠️  Streamlit not running" >> "$LOG_FILE"
    osascript -e 'display notification "Streamlit not running!" with title "❌ Error" sound name "Basso"'
fi

echo "$CURRENT_DATE" > "$LAST_RUN_FILE"
echo "[$(date)] ✅ Recorded run" >> "$LOG_FILE"
