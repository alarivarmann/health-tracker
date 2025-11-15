#!/bin/bash
# Helper script to restore after sleep test

echo "🔄 Restoring original schedule..."
echo ""

# Restore smart_notify.sh
if [ -f smart_notify.sh.backup ]; then
    mv smart_notify.sh.backup smart_notify.sh
    chmod +x smart_notify.sh
    echo "✅ Restored smart_notify.sh"
else
    echo "⚠️  No backup found for smart_notify.sh"
fi

# Restore plist
if [ -f ~/Library/LaunchAgents/com.metricsTracker.prod.plist.backup ]; then
    mv ~/Library/LaunchAgents/com.metricsTracker.prod.plist.backup ~/Library/LaunchAgents/com.metricsTracker.prod.plist
    echo "✅ Restored plist"
else
    echo "⚠️  No backup found for plist"
fi

# Reload
launchctl unload ~/Library/LaunchAgents/com.metricsTracker.prod.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.metricsTracker.prod.plist 2>/dev/null || true

echo ""
echo "✅ Original schedule restored!"
echo ""
echo "Check status: make schedule-status"