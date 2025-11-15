#!/bin/bash
# Interactive Metrics Tracker Scheduler
# Choose between TEST mode (run in N minutes) or PROD mode (weekly schedule)

set -e

echo "════════════════════════════════════════════════════════════"
echo "📊 METRICS TRACKER SCHEDULER"
echo "════════════════════════════════════════════════════════════"
echo ""

cd ~/metrics-tracker

# Step 1: Create notification script if it doesn't exist
if [ ! -f "notify_metrics.sh" ]; then
    echo "Creating notification script..."
    cat > notify_metrics.sh << 'EOF'
#!/bin/bash
# Metrics Tracker Notification Script

echo "[$(date)] ========================================" >> "$HOME/metrics-tracker/notify.log"
echo "[$(date)] Script started" >> "$HOME/metrics-tracker/notify.log"

# Send notification
osascript -e 'display notification "⏰ Time to fill in your metrics!" with title "📊 Metrics Tracker" sound name "Glass"'
echo "[$(date)] Notification sent" >> "$HOME/metrics-tracker/notify.log"

sleep 1

# Check if Streamlit is running
if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "[$(date)] Streamlit is running, opening browser" >> "$HOME/metrics-tracker/notify.log"
    open "http://localhost:8501"
    echo "[$(date)] Browser opened successfully" >> "$HOME/metrics-tracker/notify.log"
else
    echo "[$(date)] ERROR: Streamlit is not running at localhost:8501" >> "$HOME/metrics-tracker/notify.log"
    osascript -e 'display notification "Streamlit is not running! Start it first." with title "❌ Metrics Tracker Error" sound name "Basso"'
fi

echo "[$(date)] Script finished" >> "$HOME/metrics-tracker/notify.log"
EOF
    chmod +x notify_metrics.sh
    echo "✅ Created notify_metrics.sh"
    echo ""
fi

# Step 2: Test the script
echo "🧪 Testing notification script now..."
./notify_metrics.sh
echo ""
echo "Did you see the notification and browser open? (yes/no)"
read -r TEST_RESPONSE

if [ "$TEST_RESPONSE" != "yes" ]; then
    echo ""
    echo "⚠️  Script test failed!"
    echo "Make sure Streamlit is running at http://localhost:8501"
    echo ""
    echo "Start it with:"
    echo "  cd ~/metrics-tracker"
    echo "  streamlit run metrics_app.py"
    echo ""
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "🎯 CHOOSE MODE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "1) TEST MODE    - Run once in N minutes (for testing)"
echo "2) PROD MODE    - Weekly schedule (Tuesdays & Thursdays)"
echo "3) CUSTOM       - Specify your own schedule"
echo "4) REMOVE       - Unload and remove the scheduled task"
echo ""
echo -n "Enter choice (1-4): "
read -r MODE_CHOICE

case $MODE_CHOICE in
    1)
        # TEST MODE
        echo ""
        echo "🧪 TEST MODE"
        echo "─────────────────────────────────────────────────────────"
        echo -n "Repeat every N minutes? (e.g., 3 for every 3 minutes): "
        read -r INTERVAL_MINUTES
        
        # Convert minutes to seconds
        INTERVAL_SECONDS=$((INTERVAL_MINUTES * 60))
        
        echo ""
        echo "Current time: $(date '+%H:%M:%S')"
        echo "Will run every $INTERVAL_MINUTES minutes (starting now)"
        echo ""
        
        # Create plist with StartInterval
        cat > ~/Library/LaunchAgents/com.metricsTracker.test.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.metricsTracker.test</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/alavar/metrics-tracker/notify_metrics.sh</string>
    </array>
    
    <key>StartInterval</key>
    <integer>$INTERVAL_SECONDS</integer>
    
    <key>WorkingDirectory</key>
    <string>/Users/alavar/metrics-tracker</string>
    
    <key>StandardOutPath</key>
    <string>/Users/alavar/metrics-tracker/notify.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/alavar/metrics-tracker/notify.error.log</string>
    
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF
        
        SCHEDULE_DESC="Every $INTERVAL_MINUTES minutes (repeating continuously)"
        ;;
        
    2)
        # PROD MODE
        echo ""
        echo "🚀 PROD MODE - Weekly Schedule"
        echo "─────────────────────────────────────────────────────────"
        echo -n "Enter time (24-hour format, e.g., 10:30): "
        read -r TIME_INPUT
        
        HOUR=$(echo $TIME_INPUT | cut -d':' -f1)
        MINUTE=$(echo $TIME_INPUT | cut -d':' -f2)
        
        echo ""
        echo "Schedule: Tuesdays and Thursdays at $HOUR:$MINUTE"
        echo ""
        
        # Create plist with recurring schedule
        cat > ~/Library/LaunchAgents/com.metricsTracker.test.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.metricsTracker.test</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/alavar/metrics-tracker/notify_metrics.sh</string>
    </array>
    
    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Weekday</key>
            <integer>2</integer>
            <key>Hour</key>
            <integer>$HOUR</integer>
            <key>Minute</key>
            <integer>$MINUTE</integer>
        </dict>
        <dict>
            <key>Weekday</key>
            <integer>4</integer>
            <key>Hour</key>
            <integer>$HOUR</integer>
            <key>Minute</key>
            <integer>$MINUTE</integer>
        </dict>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/Users/alavar/metrics-tracker</string>
    
    <key>StandardOutPath</key>
    <string>/Users/alavar/metrics-tracker/notify.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/alavar/metrics-tracker/notify.error.log</string>
    
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF
        
        SCHEDULE_DESC="Tuesdays & Thursdays at $HOUR:$MINUTE"
        ;;
        
    3)
        # CUSTOM MODE
        echo ""
        echo "🔧 CUSTOM MODE"
        echo "─────────────────────────────────────────────────────────"
        echo "Weekdays: 1=Monday, 2=Tuesday, ..., 7=Sunday"
        echo ""
        echo -n "Enter weekdays (comma-separated, e.g., 1,3,5 for Mon/Wed/Fri): "
        read -r WEEKDAYS_INPUT
        
        echo -n "Enter time (24-hour format, e.g., 14:30): "
        read -r TIME_INPUT
        
        HOUR=$(echo $TIME_INPUT | cut -d':' -f1)
        MINUTE=$(echo $TIME_INPUT | cut -d':' -f2)
        
        # Build the calendar intervals
        CALENDAR_INTERVALS=""
        IFS=',' read -ra WEEKDAYS <<< "$WEEKDAYS_INPUT"
        for day in "${WEEKDAYS[@]}"; do
            CALENDAR_INTERVALS="$CALENDAR_INTERVALS
        <dict>
            <key>Weekday</key>
            <integer>$day</integer>
            <key>Hour</key>
            <integer>$HOUR</integer>
            <key>Minute</key>
            <integer>$MINUTE</integer>
        </dict>"
        done
        
        echo ""
        echo "Schedule: Days $WEEKDAYS_INPUT at $HOUR:$MINUTE"
        echo ""
        
        # Create plist
        cat > ~/Library/LaunchAgents/com.metricsTracker.test.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.metricsTracker.test</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/alavar/metrics-tracker/notify_metrics.sh</string>
    </array>
    
    <key>StartCalendarInterval</key>
    <array>$CALENDAR_INTERVALS
    </array>
    
    <key>WorkingDirectory</key>
    <string>/Users/alavar/metrics-tracker</string>
    
    <key>StandardOutPath</key>
    <string>/Users/alavar/metrics-tracker/notify.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/alavar/metrics-tracker/notify.error.log</string>
    
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF
        
        SCHEDULE_DESC="Custom: Days $WEEKDAYS_INPUT at $HOUR:$MINUTE"
        ;;
        
    4)
        # REMOVE MODE
        echo ""
        echo "🗑️  REMOVE MODE"
        echo "─────────────────────────────────────────────────────────"
        echo "Unloading and removing scheduled task..."
        
        launchctl unload ~/Library/LaunchAgents/com.metricsTracker.test.plist 2>/dev/null || echo "   (not loaded)"
        rm -f ~/Library/LaunchAgents/com.metricsTracker.test.plist
        
        echo "✅ Removed!"
        echo ""
        exit 0
        ;;
        
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Unload old version
echo "Unloading old schedule (if any)..."
launchctl unload ~/Library/LaunchAgents/com.metricsTracker.test.plist 2>/dev/null || echo "   (not loaded)"

# Validate plist
echo "Validating plist..."
if ! plutil ~/Library/LaunchAgents/com.metricsTracker.test.plist; then
    echo "❌ Plist validation failed!"
    exit 1
fi
echo "✅ Plist is valid"

# Load new schedule
echo "Loading new schedule..."
launchctl load ~/Library/LaunchAgents/com.metricsTracker.test.plist

# Verify
echo "Verifying..."
if launchctl list | grep -q com.metricsTracker.test; then
    echo "✅ Successfully loaded!"
else
    echo "❌ Failed to load"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ SETUP COMPLETE!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📅 Schedule: $SCHEDULE_DESC"
echo ""
echo "📋 Logs will be written to:"
echo "   ~/metrics-tracker/notify.log"
echo "   ~/metrics-tracker/notify.error.log"
echo ""

if [ "$MODE_CHOICE" == "1" ]; then
    echo "⏰ TEST MODE: Repeating every $INTERVAL_MINUTES minutes"
    echo ""
    echo "💡 Watch the logs (it should trigger shortly):"
    echo "   tail -f ~/metrics-tracker/notify.log"
    echo ""
    echo "⚠️  Remember to switch to PROD mode when done testing!"
    echo "   ./$(basename "$0")  # and choose option 2"
fi

if [ "$MODE_CHOICE" == "2" ]; then
    echo "🚀 PROD MODE: Active every Tuesday and Thursday at $HOUR:$MINUTE"
    echo ""
    echo "🧪 To test, run this script again in TEST mode"
fi

echo ""
echo "🔍 To check status:"
echo "   launchctl list | grep metricsTracker"
echo ""
echo "🗑️  To remove:"
echo "   ./$(basename "$0")  # and choose option 4"
echo ""
