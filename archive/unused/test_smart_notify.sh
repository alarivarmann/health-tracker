#!/bin/bash
# Test the smart_notify.sh logic

echo "🧪 TESTING SMART NOTIFICATION LOGIC"
echo "════════════════════════════════════════════════════════════"
echo ""

# Show current time/day
echo "Current time: $(date '+%A, %H:%M')"
echo "Current day code: $(date +%u) (1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat, 7=Sun)"
echo ""

# Check if smart_notify.sh exists
if [ ! -f "smart_notify.sh" ]; then
    echo "❌ smart_notify.sh not found in current directory"
    echo "   Make sure you're in ~/metrics-tracker/"
    exit 1
fi

if [ ! -x "smart_notify.sh" ]; then
    echo "⚠️  smart_notify.sh is not executable"
    echo "   Running: chmod +x smart_notify.sh"
    chmod +x smart_notify.sh
fi

echo "✅ smart_notify.sh found and executable"
echo ""

# Show last run if exists
if [ -f ".last_prod_run" ]; then
    echo "Last recorded run: $(cat .last_prod_run)"
else
    echo "No previous run recorded"
fi
echo ""

echo "────────────────────────────────────────────────────────────"
echo "Running smart_notify.sh now..."
echo "────────────────────────────────────────────────────────────"
echo ""

./smart_notify.sh

echo ""
echo "────────────────────────────────────────────────────────────"
echo "📋 Check the log to see what happened:"
echo "────────────────────────────────────────────────────────────"
echo ""

if [ -f "notify_prod.log" ]; then
    tail -15 notify_prod.log
else
    echo "⚠️  No log file generated"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "💡 WHAT TO EXPECT:"
echo "════════════════════════════════════════════════════════════"
echo ""

CURRENT_DAY=$(date +%u)
CURRENT_HOUR=$(date +%H)
CURRENT_MINUTE=$(date +%M)

if [ "$CURRENT_DAY" -eq 2 ] || [ "$CURRENT_DAY" -eq 4 ]; then
    echo "Today IS a scheduled day (Tue/Thu)"
    if [ "$CURRENT_HOUR" -gt 10 ] || ([ "$CURRENT_HOUR" -eq 10 ] && [ "$CURRENT_MINUTE" -ge 30 ]); then
        echo "Time is past 10:30"
        echo "✅ Should have run (notification + browser)"
    else
        echo "Time is before 10:30"
        echo "⏰ Should have skipped (too early)"
    fi
else
    echo "Today is NOT a scheduled day"
    echo "⏭️  Should have skipped (wrong day)"
fi
echo ""