#!/bin/bash
# Diagnostic: Check current PROD schedule setup

echo "🔍 PROD SCHEDULE DIAGNOSTIC"
echo "════════════════════════════════════════════════════════════"
echo ""

PLIST_PATH="$HOME/Library/LaunchAgents/com.metricsTracker.prod.plist"

# Check if plist exists
if [ ! -f "$PLIST_PATH" ]; then
    echo "❌ Plist not found at: $PLIST_PATH"
    exit 1
fi

echo "✅ Plist found"
echo ""

# Show the plist content
echo "📄 Current plist content:"
echo "────────────────────────────────────────────────────────────"
cat "$PLIST_PATH"
echo "────────────────────────────────────────────────────────────"
echo ""

# Check key settings
echo "🔑 Key Settings:"
echo ""

# Check ProgramArguments
SCRIPT=$(grep -A 1 "ProgramArguments" "$PLIST_PATH" | grep "<string>" | tail -1 | sed 's/.*<string>\(.*\)<\/string>.*/\1/')
echo "Script called: $SCRIPT"

if [ -f "$SCRIPT" ]; then
    echo "   ✅ Script exists"
    if [ -x "$SCRIPT" ]; then
        echo "   ✅ Script is executable"
    else
        echo "   ❌ Script is NOT executable"
        echo "   Fix: chmod +x $SCRIPT"
    fi
else
    echo "   ❌ Script NOT found!"
fi
echo ""

# Check schedule
echo "Schedule (Weekday/Hour/Minute):"
grep -A 10 "StartCalendarInterval" "$PLIST_PATH" | grep -E "Weekday|Hour|Minute" | while read line; do
    echo "   $line"
done
echo ""

# Check RunAtLoad
if grep -q "<key>RunAtLoad</key>" "$PLIST_PATH"; then
    RUN_AT_LOAD=$(grep -A 1 "RunAtLoad" "$PLIST_PATH" | grep -oE "true|false")
    if [ "$RUN_AT_LOAD" = "true" ]; then
        echo "RunAtLoad: ✅ true (will check on boot/wake)"
    else
        echo "RunAtLoad: ⚠️  false (only runs at exact scheduled time)"
        echo "   This means: if Mac is asleep at scheduled time, notification is LOST"
        echo "   Recommendation: Use enhanced version with RunAtLoad: true"
    fi
else
    echo "RunAtLoad: ❌ NOT SET (defaults to false)"
    echo "   This means: if Mac is asleep at scheduled time, notification is LOST"
fi
echo ""

# Check if loaded
echo "🔧 launchd Status:"
if launchctl list | grep -q com.metricsTracker.prod; then
    echo "   ✅ Plist IS loaded in launchd"
    launchctl list | grep com.metricsTracker.prod
else
    echo "   ❌ Plist is NOT loaded"
    echo "   Run: launchctl load $PLIST_PATH"
fi
echo ""

# Check logs
echo "📋 Recent Log Activity:"
LOG_FILE="$HOME/metrics-tracker/notify_prod.log"
if [ -f "$LOG_FILE" ]; then
    echo "Last 5 entries from $LOG_FILE:"
    tail -5 "$LOG_FILE"
else
    echo "⚠️  No log file found at: $LOG_FILE"
    echo "   This means the job has never run, or logs go elsewhere"
fi
echo ""

# Check last run tracking
LAST_RUN_FILE="$HOME/metrics-tracker/.last_prod_run"
if [ -f "$LAST_RUN_FILE" ]; then
    echo "Last recorded run: $(cat $LAST_RUN_FILE)"
else
    echo "⚠️  No last run tracking file (this is normal for basic version)"
fi
echo ""

echo "════════════════════════════════════════════════════════════"
echo "🎯 RECOMMENDATION"
echo "════════════════════════════════════════════════════════════"
echo ""

if ! grep -q "RunAtLoad.*true" "$PLIST_PATH"; then
    echo "❌ Your plist does NOT have RunAtLoad: true"
    echo ""
    echo "This means if your Mac is asleep at 15:11, the job is LOST."
    echo ""
    echo "Fix options:"
    echo ""
    echo "1️⃣ SIMPLE FIX: Add RunAtLoad manually"
    echo "   Edit: $PLIST_PATH"
    echo "   Add before </dict>:"
    echo "     <key>RunAtLoad</key>"
    echo "     <true/>"
    echo "   Then reload: make schedule-stop-prod && make schedule-prod"
    echo ""
    echo "2️⃣ SMART FIX: Use enhanced version"
    echo "   Uses check_and_notify.sh which:"
    echo "   - Runs at boot/wake"
    echo "   - Checks if it's a scheduled day"
    echo "   - Only runs once per day"
    echo "   Run: Use create_prod_plist_enhanced.sh"
else
    echo "✅ Your plist has RunAtLoad: true"
    echo ""
    echo "But you still need a SMART SCRIPT that checks:"
    echo "- Is it a scheduled day?"
    echo "- Have we already run today?"
    echo ""
    echo "Use check_and_notify.sh instead of notify_metrics.sh"
fi
echo ""