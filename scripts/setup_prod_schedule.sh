#!/bin/bash
# Production Schedule Setup - Interactive configuration

echo "🚀 PRODUCTION SCHEDULE SETUP"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Configure when you want metrics reminders to trigger."
echo ""
echo "Weekday numbers:"
echo "  1 = Monday"
echo "  2 = Tuesday"
echo "  3 = Wednesday"
echo "  4 = Thursday"
echo "  5 = Friday"
echo "  6 = Saturday"
echo "  7 = Sunday"
echo ""

# Backup existing files
if [ ! -f smart_notify.sh.backup ]; then
    [ -f smart_notify.sh ] && cp smart_notify.sh smart_notify.sh.backup
fi

if [ -f ~/Library/LaunchAgents/com.metricsTracker.prod.plist ] && [ ! -f ~/Library/LaunchAgents/com.metricsTracker.prod.plist.backup ]; then
    cp ~/Library/LaunchAgents/com.metricsTracker.prod.plist ~/Library/LaunchAgents/com.metricsTracker.prod.plist.backup
fi

# Get schedule entries
SCHEDULE_ENTRIES=()
ENTRY_COUNT=0

while true; do
    echo "────────────────────────────────────────────────────────────"
    echo "Schedule Entry #$((ENTRY_COUNT + 1))"
    echo ""
    
    read -p "Weekday (1-7, or press Enter to finish): " WEEKDAY
    
    # If empty, we're done
    if [ -z "$WEEKDAY" ]; then
        if [ $ENTRY_COUNT -eq 0 ]; then
            echo "❌ You must add at least one schedule entry."
            continue
        fi
        break
    fi
    
    # Validate weekday
    if ! [[ "$WEEKDAY" =~ ^[1-7]$ ]]; then
        echo "❌ Invalid weekday. Must be 1-7."
        continue
    fi
    
    read -p "Hour (0-23): " HOUR
    
    # Validate hour
    if ! [[ "$HOUR" =~ ^[0-9]+$ ]] || [ "$HOUR" -lt 0 ] || [ "$HOUR" -gt 23 ]; then
        echo "❌ Invalid hour. Must be 0-23."
        continue
    fi
    
    read -p "Minute (0-59): " MINUTE
    
    # Validate minute
    if ! [[ "$MINUTE" =~ ^[0-9]+$ ]] || [ "$MINUTE" -lt 0 ] || [ "$MINUTE" -gt 59 ]; then
        echo "❌ Invalid minute. Must be 0-59."
        continue
    fi
    
    # Get weekday name for display
    case $WEEKDAY in
        1) WEEKDAY_NAME="Monday" ;;
        2) WEEKDAY_NAME="Tuesday" ;;
        3) WEEKDAY_NAME="Wednesday" ;;
        4) WEEKDAY_NAME="Thursday" ;;
        5) WEEKDAY_NAME="Friday" ;;
        6) WEEKDAY_NAME="Saturday" ;;
        7) WEEKDAY_NAME="Sunday" ;;
    esac
    
    echo "✅ Added: $WEEKDAY_NAME at $(printf '%02d:%02d' $HOUR $MINUTE)"
    
    # Store the entry
    SCHEDULE_ENTRIES+=("$WEEKDAY:$HOUR:$MINUTE")
    ENTRY_COUNT=$((ENTRY_COUNT + 1))
    echo ""
done

echo ""
echo "════════════════════════════════════════════════════════════"
echo "📅 SCHEDULE SUMMARY"
echo "════════════════════════════════════════════════════════════"
for entry in "${SCHEDULE_ENTRIES[@]}"; do
    WEEKDAY=$(echo $entry | cut -d: -f1)
    HOUR=$(echo $entry | cut -d: -f2)
    MINUTE=$(echo $entry | cut -d: -f3)
    
    case $WEEKDAY in
        1) WEEKDAY_NAME="Monday" ;;
        2) WEEKDAY_NAME="Tuesday" ;;
        3) WEEKDAY_NAME="Wednesday" ;;
        4) WEEKDAY_NAME="Thursday" ;;
        5) WEEKDAY_NAME="Friday" ;;
        6) WEEKDAY_NAME="Saturday" ;;
        7) WEEKDAY_NAME="Sunday" ;;
    esac
    
    echo "  • $WEEKDAY_NAME at $(printf '%02d:%02d' $HOUR $MINUTE)"
done
echo "════════════════════════════════════════════════════════════"
echo ""

read -p "Proceed with this schedule? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Setting up production schedule..."
echo ""

# Create the smart notification script
cat > scripts/smart_notify.sh << 'EOF'
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
EOF

chmod +x scripts/smart_notify.sh
echo "✅ Created scripts/smart_notify.sh"
echo ""

# Create the plist with multiple StartCalendarInterval entries
cat > ~/Library/LaunchAgents/com.metricsTracker.prod.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.metricsTracker.prod</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$HOME/metrics-tracker/scripts/smart_notify.sh</string>
    </array>
    
    <key>StartCalendarInterval</key>
    <array>
EOF

# Add each schedule entry
for entry in "${SCHEDULE_ENTRIES[@]}"; do
    WEEKDAY=$(echo $entry | cut -d: -f1)
    HOUR=$(echo $entry | cut -d: -f2)
    MINUTE=$(echo $entry | cut -d: -f3)
    
    cat >> ~/Library/LaunchAgents/com.metricsTracker.prod.plist << EOF
        <dict>
            <key>Weekday</key>
            <integer>$WEEKDAY</integer>
            <key>Hour</key>
            <integer>$HOUR</integer>
            <key>Minute</key>
            <integer>$MINUTE</integer>
        </dict>
EOF
done

# Close the plist
cat >> ~/Library/LaunchAgents/com.metricsTracker.prod.plist << EOF
    </array>
    
    <key>RunAtLoad</key>
    <false/>
    
    <key>WorkingDirectory</key>
    <string>$HOME/metrics-tracker</string>
    
    <key>StandardOutPath</key>
    <string>$HOME/metrics-tracker/logs/notify_prod.log</string>
    
    <key>StandardErrorPath</key>
    <string>$HOME/metrics-tracker/logs/notify_prod.error.log</string>
</dict>
</plist>
EOF

echo "✅ Created plist with $ENTRY_COUNT schedule entries"
echo ""

# Clear last run so it can trigger on next scheduled time
rm -f .last_prod_run
echo "✅ Cleared last run tracking"
echo ""

# Load the schedule
launchctl unload ~/Library/LaunchAgents/com.metricsTracker.prod.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.metricsTracker.prod.plist

if launchctl list | grep -q com.metricsTracker.prod; then
    echo "✅ Schedule loaded successfully!"
else
    echo "❌ Failed to load schedule"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "🎉 PRODUCTION SCHEDULE ACTIVATED!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Your schedule:"
for entry in "${SCHEDULE_ENTRIES[@]}"; do
    WEEKDAY=$(echo $entry | cut -d: -f1)
    HOUR=$(echo $entry | cut -d: -f2)
    MINUTE=$(echo $entry | cut -d: -f3)
    
    case $WEEKDAY in
        1) WEEKDAY_NAME="Monday" ;;
        2) WEEKDAY_NAME="Tuesday" ;;
        3) WEEKDAY_NAME="Wednesday" ;;
        4) WEEKDAY_NAME="Thursday" ;;
        5) WEEKDAY_NAME="Friday" ;;
        6) WEEKDAY_NAME="Saturday" ;;
        7) WEEKDAY_NAME="Sunday" ;;
    esac
    
    echo "  • $WEEKDAY_NAME at $(printf '%02d:%02d' $HOUR $MINUTE)"
done
echo ""
echo "💡 How it works:"
echo "   - Notification triggers at scheduled times"
echo "   - Opens Streamlit automatically"
echo "   - Won't run twice on the same day"
echo "   - Catches up on wake if Mac was asleep"
echo ""
echo "📋 Logs: ~/metrics-tracker/notify_prod.log"
echo "🛑 Stop: make schedule-stop-prod"
echo "📊 Status: make schedule-status"
echo ""
echo "════════════════════════════════════════════════════════════"
