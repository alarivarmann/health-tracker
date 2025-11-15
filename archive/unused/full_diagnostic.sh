#!/bin/bash
# Comprehensive diagnostics for launchd issues

echo "🔍 METRICS TRACKER DIAGNOSTIC REPORT"
echo "════════════════════════════════════════════════════════════════"
echo ""

# 1. Check if plist exists
echo "1️⃣ CHECKING PLIST FILE"
echo "─────────────────────────────────────────────────────────────"
PLIST_PATH="$HOME/Library/LaunchAgents/com.metricsTracker.test.plist"

if [ -f "$PLIST_PATH" ]; then
    echo "✅ Plist exists at: $PLIST_PATH"
    echo ""
    echo "Contents:"
    cat "$PLIST_PATH"
    echo ""
    
    # Validate XML
    if plutil "$PLIST_PATH" &>/dev/null; then
        echo "✅ Plist is valid XML"
    else
        echo "❌ Plist has XML syntax errors!"
        plutil "$PLIST_PATH"
    fi
else
    echo "❌ Plist NOT found at: $PLIST_PATH"
    echo ""
    echo "Looking for any metrics-related plists..."
    find ~/Library/LaunchAgents -name "*metric*" 2>/dev/null
fi
echo ""

# 2. Check if loaded
echo "2️⃣ CHECKING IF PLIST IS LOADED"
echo "─────────────────────────────────────────────────────────────"
if launchctl list | grep -i "metricsTracker" &>/dev/null; then
    echo "✅ Plist IS loaded in launchd"
    launchctl list | grep -i "metricsTracker"
else
    echo "❌ Plist is NOT loaded in launchd"
    echo ""
    echo "All loaded launch agents:"
    launchctl list | grep -v "com.apple" | head -20
fi
echo ""

# 3. Check notification script
echo "3️⃣ CHECKING NOTIFICATION SCRIPT"
echo "─────────────────────────────────────────────────────────────"
SCRIPT_PATH="$HOME/metrics-tracker/notify_metrics.sh"

if [ -f "$SCRIPT_PATH" ]; then
    echo "✅ Script exists at: $SCRIPT_PATH"
    
    # Check if executable
    if [ -x "$SCRIPT_PATH" ]; then
        echo "✅ Script is executable"
    else
        echo "❌ Script is NOT executable"
        echo "Fix with: chmod +x $SCRIPT_PATH"
    fi
    
    echo ""
    echo "Script contents:"
    echo "─────────────────────"
    cat "$SCRIPT_PATH"
    echo "─────────────────────"
else
    echo "❌ Script NOT found at: $SCRIPT_PATH"
fi
echo ""

# 4. Test script manually
echo "4️⃣ TESTING SCRIPT MANUALLY"
echo "─────────────────────────────────────────────────────────────"
if [ -f "$SCRIPT_PATH" ]; then
    echo "Running: $SCRIPT_PATH"
    echo ""
    $SCRIPT_PATH
    echo ""
    echo "Did you see a notification and browser open? (y/n)"
else
    echo "❌ Cannot test - script doesn't exist"
fi
echo ""

# 5. Check logs
echo "5️⃣ CHECKING LOG FILES"
echo "─────────────────────────────────────────────────────────────"
LOG_PATH="$HOME/metrics-tracker/metrics_reminder.log"
ERR_PATH="$HOME/metrics-tracker/metrics_reminder_error.log"

if [ -f "$LOG_PATH" ]; then
    echo "📄 Standard output log:"
    tail -20 "$LOG_PATH"
else
    echo "⚠️  No log file at: $LOG_PATH"
fi
echo ""

if [ -f "$ERR_PATH" ]; then
    echo "📄 Error log:"
    tail -20 "$ERR_PATH"
else
    echo "⚠️  No error log at: $ERR_PATH"
fi
echo ""

# 6. Check Streamlit
echo "6️⃣ CHECKING IF STREAMLIT IS RUNNING"
echo "─────────────────────────────────────────────────────────────"
if pgrep -f "streamlit" &>/dev/null; then
    echo "✅ Streamlit is running"
    echo ""
    echo "Streamlit processes:"
    ps aux | grep streamlit | grep -v grep
    echo ""
    
    # Test if accessible
    if curl -s "http://localhost:8501" &>/dev/null; then
        echo "✅ Streamlit is accessible at http://localhost:8501"
    else
        echo "❌ Streamlit is running but NOT accessible at http://localhost:8501"
    fi
else
    echo "❌ Streamlit is NOT running"
    echo ""
    echo "Start it with:"
    echo "  cd ~/metrics-tracker"
    echo "  streamlit run metrics_app.py"
fi
echo ""

# 7. Force run the job
echo "7️⃣ FORCE-RUNNING THE JOB NOW"
echo "─────────────────────────────────────────────────────────────"
if launchctl list | grep -i "metricsTracker" &>/dev/null; then
    echo "Forcing execution via launchctl..."
    launchctl start com.metricsTracker.test
    sleep 2
    echo ""
    echo "Check if notification appeared and browser opened."
    echo ""
    
    # Show any new log entries
    if [ -f "$LOG_PATH" ]; then
        echo "Latest log entries:"
        tail -5 "$LOG_PATH"
    fi
else
    echo "❌ Cannot force-run because plist is not loaded"
fi
echo ""

# 8. System log check
echo "8️⃣ CHECKING SYSTEM LOGS FOR ERRORS"
echo "─────────────────────────────────────────────────────────────"
echo "Checking last 5 minutes for launchd errors..."
log show --predicate 'process == "launchd" AND eventMessage CONTAINS "metricsTracker"' --info --last 5m 2>/dev/null | tail -20
echo ""

# 9. Permissions check
echo "9️⃣ CHECKING PERMISSIONS"
echo "─────────────────────────────────────────────────────────────"
ls -la "$PLIST_PATH" 2>/dev/null || echo "Plist not found"
ls -la "$SCRIPT_PATH" 2>/dev/null || echo "Script not found"
echo ""

# Summary and recommendations
echo "═══════════════════════════════════════════════════════════════"
echo "🎯 RECOMMENDATIONS"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Build recommendations based on findings
ISSUES_FOUND=0

if [ ! -f "$PLIST_PATH" ]; then
    echo "❌ Plist missing - copy from artifacts"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Script missing - create it"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
elif [ ! -x "$SCRIPT_PATH" ]; then
    echo "❌ Script not executable - run: chmod +x $SCRIPT_PATH"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

if ! launchctl list | grep -i "metricsTracker" &>/dev/null; then
    echo "❌ Plist not loaded - run: launchctl load $PLIST_PATH"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

if ! pgrep -f "streamlit" &>/dev/null; then
    echo "❌ Streamlit not running - start it first"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

if [ $ISSUES_FOUND -eq 0 ]; then
    echo "✅ Everything looks good!"
    echo ""
    echo "If scheduled run still doesn't work, check:"
    echo "1. Wait until the scheduled time (14:09)"
    echo "2. Check logs after that time"
    echo "3. Verify the time is correct in the plist"
else
    echo ""
    echo "Fix the issues above, then run this diagnostic again."
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"