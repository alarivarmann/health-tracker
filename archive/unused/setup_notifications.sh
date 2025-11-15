#!/bin/bash
# Setup script to fix your plist and create the notification script

echo "🔧 FIXING METRICS TRACKER SETUP"
echo "════════════════════════════════════════════════════════════"
echo ""

cd ~/metrics-tracker

# Step 1: Create the notification script
echo "1️⃣ Creating notification script..."
cat > notify_metrics.sh << 'SCRIPT_EOF'
#!/bin/bash
# Metrics Tracker Notification Script

echo "[$(date)] Script started" >> "$HOME/metrics-tracker/notify.log"

# Send notification
osascript -e 'display notification "⏰ Time to fill in your metrics!" with title "📊 Metrics Tracker" sound name "Glass"'

sleep 1

# Check if Streamlit is running
if curl -s http://localhost:8501 > /dev/null; then
    echo "[$(date)] Streamlit is running, opening browser" >> "$HOME/metrics-tracker/notify.log"
    open "http://localhost:8501"
    echo "[$(date)] Browser opened successfully" >> "$HOME/metrics-tracker/notify.log"
else
    echo "[$(date)] ERROR: Streamlit is not running" >> "$HOME/metrics-tracker/notify.log"
    osascript -e 'display notification "Streamlit is not running! Start it first." with title "❌ Metrics Tracker Error" sound name "Basso"'
fi

echo "[$(date)] Script finished" >> "$HOME/metrics-tracker/notify.log"
SCRIPT_EOF

chmod +x notify_metrics.sh
echo "✅ Created and made executable: notify_metrics.sh"
echo ""

# Step 2: Test the script
echo "2️⃣ Testing notification script..."
./notify_metrics.sh
echo ""
echo "Did you see a notification and browser open? (yes/no)"
read -r RESPONSE
echo ""

if [[ "$RESPONSE" != "yes" ]]; then
    echo "⚠️  Script test failed. Check if Streamlit is running:"
    echo "   ps aux | grep streamlit"
    echo ""
    echo "If not running, start it:"
    echo "   cd ~/metrics-tracker"
    echo "   streamlit run metrics_app.py"
    echo ""
    exit 1
fi

# Step 3: Unload old plist
echo "3️⃣ Unloading old plist..."
launchctl unload ~/Library/LaunchAgents/com.metricsTracker.test.plist 2>/dev/null
echo "✅ Unloaded"
echo ""

# Step 4: Backup old plist
echo "4️⃣ Backing up old plist..."
if [ -f ~/Library/LaunchAgents/com.metricsTracker.test.plist ]; then
    cp ~/Library/LaunchAgents/com.metricsTracker.test.plist ~/Library/LaunchAgents/com.metricsTracker.test.plist.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Backed up old plist"
else
    echo "⚠️  No existing plist found (this is fine for first setup)"
fi
echo ""

# Step 5: Create new plist
echo "5️⃣ Creating corrected plist..."
cat > ~/Library/LaunchAgents/com.metricsTracker.test.plist << 'PLIST_EOF'
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
    <dict>
        <key>Hour</key>
        <integer>17</integer>
        <key>Minute</key>
        <integer>59</integer>
    </dict>
    
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
PLIST_EOF

echo "✅ Created new plist"
echo ""

# Step 6: Validate plist
echo "6️⃣ Validating plist XML..."
if plutil ~/Library/LaunchAgents/com.metricsTracker.test.plist; then
    echo "✅ Plist is valid"
else
    echo "❌ Plist has errors!"
    exit 1
fi
echo ""

# Step 7: Load new plist
echo "7️⃣ Loading new plist..."
launchctl load ~/Library/LaunchAgents/com.metricsTracker.test.plist
echo "✅ Loaded"
echo ""

# Step 8: Verify
echo "8️⃣ Verifying setup..."
if launchctl list | grep com.metricsTracker.test > /dev/null; then
    echo "✅ Plist is loaded and active"
else
    echo "❌ Plist failed to load"
    echo ""
    echo "Try manually:"
    echo "  launchctl load -w ~/Library/LaunchAgents/com.metricsTracker.test.plist"
    exit 1
fi
echo ""

# Step 9: Force test
echo "9️⃣ Force-testing the job now..."
launchctl start com.metricsTracker.test
sleep 2
echo ""
echo "Did you see another notification and browser open?"
echo ""

# Show logs
echo "📋 Log output:"
if [ -f notify.log ]; then
    tail -10 notify.log
else
    echo "No log file yet"
fi
echo ""

# Summary
echo "════════════════════════════════════════════════════════════"
echo "✅ SETUP COMPLETE!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "⏰ Scheduled to run daily at 17:59 (5:59 PM)"
echo ""
echo "📝 Logs:"
echo "   ~/metrics-tracker/notify.log"
echo "   ~/metrics-tracker/notify.error.log"
echo ""
echo "🧪 To test immediately:"
echo "   ~/metrics-tracker/notify_metrics.sh"
echo ""
echo "🔧 To change time, edit:"
echo "   ~/Library/LaunchAgents/com.metricsTracker.test.plist"
echo "   Then: launchctl unload <plist> && launchctl load <plist>"
echo ""
echo "🗑️  To remove:"
echo "   launchctl unload ~/Library/LaunchAgents/com.metricsTracker.test.plist"
echo "   rm ~/Library/LaunchAgents/com.metricsTracker.test.plist"
echo ""