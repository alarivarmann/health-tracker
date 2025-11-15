#!/bin/bash#!/bin/bash

# Generate PROD schedule plist - Structure-aware version# Generate CORRECT PROD schedule plist

# Dynamically detects project paths instead of hard-coding them# Handles: scheduled times + wake from sleep

# Handles: scheduled times + wake from sleep

cat > ~/Library/LaunchAgents/com.metricsTracker.prod.plist << 'EOF'

# Detect project structure dynamically<?xml version="1.0" encoding="UTF-8"?>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">

PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"<plist version="1.0">

<dict>

# Find the metrics_app.py location    <key>Label</key>

if [ -f "$PROJECT_ROOT/src/metrics_app.py" ]; then    <string>com.metricsTracker.prod</string>

    APP_PATH="src/metrics_app.py"    

elif [ -f "$PROJECT_ROOT/metrics_app.py" ]; then    <key>ProgramArguments</key>

    APP_PATH="metrics_app.py"    <array>

else        <string>/bin/bash</string>

    echo "❌ ERROR: Cannot find metrics_app.py in expected locations"        <string>/Users/alavar/metrics-tracker/scripts/smart_notify.sh</string>

    echo "   Looked in:"    </array>

    echo "   - $PROJECT_ROOT/src/metrics_app.py"    

    echo "   - $PROJECT_ROOT/metrics_app.py"    <!-- Run on schedule: Tuesdays & Thursdays at 10:30 -->

    exit 1    <key>StartCalendarInterval</key>

fi    <array>

        <dict>

# Determine script location            <key>Weekday</key>

if [ -f "$PROJECT_ROOT/scripts/smart_notify.sh" ]; then            <integer>2</integer>

    NOTIFY_SCRIPT="$PROJECT_ROOT/scripts/smart_notify.sh"            <key>Hour</key>

elif [ -f "$PROJECT_ROOT/smart_notify.sh" ]; then            <integer>10</integer>

    NOTIFY_SCRIPT="$PROJECT_ROOT/smart_notify.sh"            <key>Minute</key>

else            <integer>30</integer>

    echo "❌ ERROR: Cannot find smart_notify.sh"        </dict>

    echo "   Looked in:"        <dict>

    echo "   - $PROJECT_ROOT/scripts/smart_notify.sh"            <key>Weekday</key>

    echo "   - $PROJECT_ROOT/smart_notify.sh"            <integer>4</integer>

    exit 1            <key>Hour</key>

fi            <integer>10</integer>

            <key>Minute</key>

# Determine log directory            <integer>30</integer>

if [ -d "$PROJECT_ROOT/logs" ]; then        </dict>

    LOG_DIR="$PROJECT_ROOT/logs"    </array>

else    

    LOG_DIR="$PROJECT_ROOT"    <!-- CRITICAL: Run on boot/wake to catch missed schedules -->

fi    <key>RunAtLoad</key>

    <true/>

echo "📋 Detected project structure:"    

echo "   Project root: $PROJECT_ROOT"    <key>WorkingDirectory</key>

echo "   App path: $APP_PATH"    <string>/Users/alavar/metrics-tracker</string>

echo "   Notify script: $NOTIFY_SCRIPT"    

echo "   Log directory: $LOG_DIR"    <key>StandardOutPath</key>

echo ""    <string>/Users/alavar/metrics-tracker/logs/notify_prod.log</string>

    

# Read schedule from stdin or use default    <key>StandardErrorPath</key>

if [ -z "$1" ]; then    <string>/Users/alavar/metrics-tracker/logs/notify_prod.error.log</string>

    echo "⚠️  No schedule provided, using default: Tuesday & Thursday at 10:30"</dict>

    SCHEDULE_ENTRIES='</plist>

        <dict>EOF

            <key>Weekday</key>

            <integer>2</integer>echo "✅ Created PROD plist (with wake-from-sleep support)"
            <key>Hour</key>
            <integer>10</integer>
            <key>Minute</key>
            <integer>30</integer>
        </dict>
        <dict>
            <key>Weekday</key>
            <integer>4</integer>
            <key>Hour</key>
            <integer>10</integer>
            <key>Minute</key>
            <integer>30</integer>
        </dict>'
else
    SCHEDULE_ENTRIES="$1"
fi

# Generate plist with detected paths
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
        <string>$NOTIFY_SCRIPT</string>
    </array>
    
    <!-- Run on schedule -->
    <key>StartCalendarInterval</key>
    <array>$SCHEDULE_ENTRIES
    </array>
    
    <!-- CRITICAL: Run on boot/wake to catch missed schedules -->
    <key>RunAtLoad</key>
    <true/>
    
    <key>WorkingDirectory</key>
    <string>$PROJECT_ROOT</string>
    
    <key>StandardOutPath</key>
    <string>$LOG_DIR/notify_prod.log</string>
    
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/notify_prod.error.log</string>
</dict>
</plist>
EOF

echo "✅ Created PROD plist at ~/Library/LaunchAgents/com.metricsTracker.prod.plist"
echo ""
echo "📄 Generated plist uses:"
echo "   Notify script: $NOTIFY_SCRIPT"
echo "   Working dir: $PROJECT_ROOT"
echo "   Prod logs: $LOG_DIR/notify_prod.{log,error.log}"
echo "   Wake-from-sleep: Enabled (RunAtLoad=true)"
