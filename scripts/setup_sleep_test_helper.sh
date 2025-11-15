#!/bin/bash
# SLEEP TEST - Schedule for FUTURE time, trigger only after wake

CURRENT_DAY=$(date +%u)
CURRENT_HOUR=$(date +%H)
CURRENT_MINUTE=$(date +%M)

echo "🧪 SLEEP/WAKE TEST SETUP"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Current time: $CURRENT_HOUR:$CURRENT_MINUTE"
echo ""
echo "This test simulates:"
echo "  1. You put Mac to sleep NOW"
echo "  2. While asleep, the scheduled time passes"
echo "  3. You wake Mac later"
echo "  4. Script detects missed time and triggers notification"
echo ""
echo "Enter the time you want to schedule for (while Mac will be asleep):"
echo ""
read -p "Hour (0-23): " SCHEDULED_HOUR
read -p "Minute (0-59): " SCHEDULED_MINUTE

# Validate input
if ! [[ "$SCHEDULED_HOUR" =~ ^[0-9]+$ ]] || [ "$SCHEDULED_HOUR" -lt 0 ] || [ "$SCHEDULED_HOUR" -gt 23 ]; then
    echo "❌ Invalid hour. Must be 0-23."
    exit 1
fi

if ! [[ "$SCHEDULED_MINUTE" =~ ^[0-9]+$ ]] || [ "$SCHEDULED_MINUTE" -lt 0 ] || [ "$SCHEDULED_MINUTE" -gt 59 ]; then
    echo "❌ Invalid minute. Must be 0-59."
    exit 1
fi

echo ""
echo "Scheduled time: $SCHEDULED_HOUR:$SCHEDULED_MINUTE"
echo ""

# Check if scheduled time is in the past
SCHEDULED_MINS=$((SCHEDULED_HOUR * 60 + SCHEDULED_MINUTE))
CURRENT_MINS=$((CURRENT_HOUR * 60 + CURRENT_MINUTE))

if [ $SCHEDULED_MINS -le $CURRENT_MINS ]; then
    echo "⚠️  WARNING: Scheduled time ($SCHEDULED_HOUR:$SCHEDULED_MINUTE) is in the PAST or NOW"
    echo ""
    echo "For proper sleep test, schedule a time in the FUTURE."
    echo "Example: If it's 14:30 now, schedule for 14:35 or later."
    echo ""
    read -p "Continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        echo "Cancelled."
        exit 0
    fi
fi

echo ""

# Backup
if [ ! -f smart_notify.sh.backup ]; then
    cp smart_notify.sh smart_notify.sh.backup
    echo "✅ Backed up smart_notify.sh"
fi

if [ -f ~/Library/LaunchAgents/com.metricsTracker.prod.plist ] && [ ! -f ~/Library/LaunchAgents/com.metricsTracker.prod.plist.backup ]; then
    cp ~/Library/LaunchAgents/com.metricsTracker.prod.plist ~/Library/LaunchAgents/com.metricsTracker.prod.plist.backup
    echo "✅ Backed up plist"
fi
echo ""

# Create test script that only runs if scheduled time was missed
cat > smart_notify.sh << EOF
#!/bin/bash
LOG_FILE="\$HOME/metrics-tracker/notify_prod.log"
LAST_RUN_FILE="\$HOME/metrics-tracker/.last_prod_run"
SCHEDULED_TIME_FILE="\$HOME/metrics-tracker/.sleep_test_time"

echo "[\$(date)] ========================================" >> "\$LOG_FILE"
echo "[\$(date)] 🧪 SLEEP TEST - smart_notify.sh started" >> "\$LOG_FILE"

CURRENT_DATE=\$(date +%Y-%m-%d)
CURRENT_TIME=\$(date '+%H:%M')
CURRENT_MINS=\$((10#\$(date +%H) * 60 + 10#\$(date +%M)))

echo "[\$(date)] Current: \$(date +%A), Time=\$CURRENT_TIME" >> "\$LOG_FILE"

# Check if we already ran today
if [ -f "\$LAST_RUN_FILE" ]; then
    LAST_RUN_DATE=\$(cat "\$LAST_RUN_FILE")
    echo "[\$(date)] Last run was: \$LAST_RUN_DATE" >> "\$LOG_FILE"
    
    if [ "\$LAST_RUN_DATE" == "\$CURRENT_DATE" ]; then
        echo "[\$(date)] ⚠️  Already ran today. Skipping." >> "\$LOG_FILE"
        exit 0
    fi
fi

# Read the scheduled time
if [ ! -f "\$SCHEDULED_TIME_FILE" ]; then
    echo "[\$(date)] ❌ No scheduled time file found" >> "\$LOG_FILE"
    exit 1
fi

SCHEDULED_TIME=\$(cat "\$SCHEDULED_TIME_FILE")
SCHEDULED_HOUR=\$(echo \$SCHEDULED_TIME | cut -d: -f1)
SCHEDULED_MINUTE=\$(echo \$SCHEDULED_TIME | cut -d: -f2)
SCHEDULED_MINS=\$((10#\$SCHEDULED_HOUR * 60 + 10#\$SCHEDULED_MINUTE))
GRACE_PERIOD_MINS=1440  # 1 day grace period for missed schedules

echo "[\$(date)] Scheduled time: \$SCHEDULED_TIME (mins: \$SCHEDULED_MINS)" >> "\$LOG_FILE"
echo "[\$(date)] Current time: \$CURRENT_TIME (mins: \$CURRENT_MINS)" >> "\$LOG_FILE"

# Calculate time difference
TIME_DIFF=\$((CURRENT_MINS - SCHEDULED_MINS))

# Check if within grace period
if [ \$TIME_DIFF -lt 0 ]; then
    echo "[\$(date)] ⏰ Not yet time. Scheduled: \$SCHEDULED_TIME, Current: \$CURRENT_TIME" >> "\$LOG_FILE"
    echo "[\$(date)] Skipping (will run at scheduled time)" >> "\$LOG_FILE"
    exit 0
elif [ \$TIME_DIFF -gt \$GRACE_PERIOD_MINS ]; then
    echo "[\$(date)] ⏭️  Too late. \$TIME_DIFF mins after scheduled time (grace period: \$GRACE_PERIOD_MINS mins expired)" >> "\$LOG_FILE"
    exit 0
fi

echo "[\$(date)] ✅ SLEEP TEST: Within grace period (\$TIME_DIFF mins after scheduled time)" >> "\$LOG_FILE"

osascript -e 'display notification "⏰ SLEEP TEST: Woke up after scheduled time!" with title "📊 Metrics Tracker TEST" sound name "Glass"'
echo "[\$(date)] ✅ Notification sent" >> "\$LOG_FILE"

sleep 1

if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "[\$(date)] ✅ Streamlit running, opening browser" >> "\$LOG_FILE"
    open "http://localhost:8501"
    echo "[\$(date)] ✅ Browser opened" >> "\$LOG_FILE"
else
    echo "[\$(date)] ⚠️  Streamlit not running" >> "\$LOG_FILE"
    osascript -e 'display notification "Streamlit not running!" with title "❌ Error" sound name "Basso"'
fi

echo "\$CURRENT_DATE" > "\$LAST_RUN_FILE"
echo "[\$(date)] ✅ Recorded run" >> "\$LOG_FILE"
EOF

chmod +x smart_notify.sh
echo "✅ Created test script with scheduled time check"
echo ""

# Save scheduled time for the script to check
echo "$SCHEDULED_HOUR:$SCHEDULED_MINUTE" > .sleep_test_time
echo "✅ Saved scheduled time: $SCHEDULED_HOUR:$SCHEDULED_MINUTE"
echo ""

# Create plist WITHOUT RunAtLoad (so it doesn't trigger immediately)
# Will only trigger at the scheduled interval
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
        <string>$HOME/metrics-tracker/smart_notify.sh</string>
    </array>
    
    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Hour</key>
            <integer>$SCHEDULED_HOUR</integer>
            <key>Minute</key>
            <integer>$SCHEDULED_MINUTE</integer>
        </dict>
    </array>
    
    <key>WorkingDirectory</key>
    <string>$HOME/metrics-tracker</string>
    
    <key>StandardOutPath</key>
    <string>$HOME/metrics-tracker/notify_prod.log</string>
    
    <key>StandardErrorPath</key>
    <string>$HOME/metrics-tracker/notify_prod.error.log</string>
</dict>
</plist>
EOF

echo "✅ Created plist for $SCHEDULED_HOUR:$SCHEDULED_MINUTE (NO RunAtLoad)"
echo ""

# Clear last run
rm -f .last_prod_run
echo "✅ Cleared last run tracking"
echo ""

# Load schedule
launchctl unload ~/Library/LaunchAgents/com.metricsTracker.prod.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.metricsTracker.prod.plist

if launchctl list | grep -q com.metricsTracker.prod; then
    echo "✅ Schedule loaded"
else
    echo "❌ Failed to load"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "🎯 SLEEP TEST READY!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Scheduled time: $SCHEDULED_HOUR:$SCHEDULED_MINUTE"
echo "Current time: $(date '+%H:%M')"
echo ""
echo "📋 TEST STEPS:"
echo ""
echo "1. 😴 PUT MAC TO SLEEP NOW"
echo "   (Close lid or use sleep option)"
echo ""
echo "2. ⏰ WAIT until AFTER $SCHEDULED_HOUR:$SCHEDULED_MINUTE"
echo "   (Mac must be asleep when scheduled time passes)"
echo ""
echo "3. 👋 WAKE MAC (after scheduled time)"
echo ""
echo "4. ⏱️  LaunchAgent will trigger at scheduled time or shortly after wake"
echo ""
echo "5. ✅ You should see:"
echo "   - Notification: 'Woke up after scheduled time!'"
echo "   - Browser opens to Streamlit"
echo ""
echo "6. 📋 CHECK LOG:"
echo "   tail -20 ~/metrics-tracker/notify_prod.log"
echo ""
echo "7. 🔄 RESTORE:"
echo "   make schedule-restore-after-test"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "💡 HOW IT WORKS:"
echo "   - LaunchAgent checks every minute around scheduled time"
echo "   - Script compares current time vs scheduled time"
echo "   - Only triggers if current time > scheduled time"
echo "   - Won't trigger twice on same day"
echo ""