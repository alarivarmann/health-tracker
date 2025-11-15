#!/bin/bash
# Generate TEST schedule plist - Structure-aware version

# Detect project structure dynamically
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Determine script location
if [ -f "$PROJECT_ROOT/scripts/smart_notify.sh" ]; then
    NOTIFY_SCRIPT="$PROJECT_ROOT/scripts/smart_notify.sh"
elif [ -f "$PROJECT_ROOT/smart_notify.sh" ]; then
    NOTIFY_SCRIPT="$PROJECT_ROOT/smart_notify.sh"
else
    echo "❌ ERROR: Cannot find smart_notify.sh"
    exit 1
fi

# Determine log directory
if [ -d "$PROJECT_ROOT/logs" ]; then
    LOG_DIR="$PROJECT_ROOT/logs"
else
    LOG_DIR="$PROJECT_ROOT"
fi

echo "📋 Detected: notify=$NOTIFY_SCRIPT, logs=$LOG_DIR"

cat > ~/Library/LaunchAgents/com.metricsTracker.test.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.metricsTracker.test</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$NOTIFY_SCRIPT</string>
    </array>
    
    <key>StartInterval</key>
    <integer>180</integer>
    
    <key>WorkingDirectory</key>
    <string>$PROJECT_ROOT</string>
    
    <key>StandardOutPath</key>
    <string>$LOG_DIR/notify_test.log</string>
    
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/notify_test.error.log</string>
    
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

echo "✅ Created TEST plist"