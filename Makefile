.PHONY: start start-fg start-bg stop restart clean flush-data status test
.PHONY: schedule-prod schedule-test schedule-stop-prod schedule-stop-test schedule-status schedule-stop-all
.PHONY: schedule-sleep-test schedule-restore-after-test

# ════════════════════════════════════════════════════════════════
# CONFIGURATION VARIABLES
# ════════════════════════════════════════════════════════════════
PROJECT_ROOT := $(shell pwd)
SRC_DIR := $(PROJECT_ROOT)/src
DATA_DIR := $(PROJECT_ROOT)/data
LOGS_DIR := $(PROJECT_ROOT)/logs
SCRIPTS_DIR := $(PROJECT_ROOT)/scripts
ARCHIVE_DIR := $(PROJECT_ROOT)/archive/backups

MAIN_APP := $(SRC_DIR)/metrics_app.py
PREFLIGHT := $(SRC_DIR)/preflight_check.py

METRICS_DATA := $(DATA_DIR)/metrics_data.json
METRICS_LOG := $(DATA_DIR)/metrics_log.csv
LAST_RUN_FILE := $(DATA_DIR)/.last_prod_run

PROD_LOG := $(LOGS_DIR)/notify_prod.log
TEST_LOG := $(LOGS_DIR)/notify_test.log

LAUNCH_AGENTS := $(HOME)/Library/LaunchAgents
PROD_PLIST := $(LAUNCH_AGENTS)/com.metricsTracker.prod.plist
TEST_PLIST := $(LAUNCH_AGENTS)/com.metricsTracker.test.plist

STREAMLIT_LOG := /tmp/metrics_streamlit.log
STREAMLIT_URL := http://localhost:8501

# ════════════════════════════════════════════════════════════════
# APP CONTROL COMMANDS
# ════════════════════════════════════════════════════════════════

# Pre-flight sanity check
test:
	@echo "Running pre-flight checks..."
	@export PATH=$$HOME/.local/bin:$$PATH && uv run python3 $(PREFLIGHT) || (echo "❌ Tests failed! Fix issues before starting app." && exit 1)

# Start the app in background and show status (DEFAULT)
start:
	@make start-bg
	@echo ""
	@make schedule-status

# Start the app in foreground (with pre-flight check)
start-fg: test
	@echo ""
	@echo "🚀 Starting Metrics Tracker..."
	@export PATH=$$HOME/.local/bin:$$PATH && uv run streamlit run $(MAIN_APP)

# Start in background (daemon mode)
start-bg:
	@make test || (echo "❌ Tests failed! Fix issues before starting app." && exit 1)
	@echo "🚀 Starting Metrics Tracker in background..."
	@export PATH=$$HOME/.local/bin:$$PATH && nohup uv run streamlit run $(MAIN_APP) > $(STREAMLIT_LOG) 2>&1 &
	@sleep 3
	@echo "✅ Running on $(STREAMLIT_URL)"
	@echo "   Logs: tail -f $(STREAMLIT_LOG)"

# Stop the app
stop:
	@echo "🛑 Stopping Metrics Tracker..."
	@pkill -f "streamlit run $(MAIN_APP)" || echo "No process found"
	@sleep 1
	@echo "✅ Stopped"

# Restart the app  
restart: stop
	@sleep 2
	@echo "🔄 Restarting..."
	@make start

# Clean cache and restart
clean: stop
	@echo "🧹 Cleaning cache..."
	@rm -rf ~/.streamlit/cache
	@rm -rf .streamlit
	@pkill -9 -f streamlit || true
	@sleep 2
	@echo "✅ Cache cleared"
	@make start

# Flush/reset all data (CSV and narratives)
flush-data:
	@echo "⚠️  WARNING: This will delete ALL metrics data!"
	@echo ""
	@echo "Files that will be deleted:"
	@if [ -f $(METRICS_DATA) ]; then echo "  • $(METRICS_DATA)"; fi
	@if [ -f $(METRICS_LOG) ]; then echo "  • $(METRICS_LOG) ($$(wc -l < $(METRICS_LOG)) entries)"; fi
	@if [ -f $(LAST_RUN_FILE) ]; then echo "  • $(LAST_RUN_FILE) (schedule tracking)"; fi
	@echo ""
	@read -p "Are you sure? Type 'yes' to confirm: " confirm && [ "$$confirm" = "yes" ] || (echo "Cancelled." && exit 1)
	@echo ""
	@echo "🗑️  Flushing data..."
	@mkdir -p $(ARCHIVE_DIR)
	@if [ -f $(METRICS_DATA) ]; then \
		cp $(METRICS_DATA) $(ARCHIVE_DIR)/metrics_data.json.backup.$$(date +%Y%m%d_%H%M%S) && \
		echo "✅ Backed up to: $(ARCHIVE_DIR)/metrics_data.json.backup.$$(date +%Y%m%d_%H%M%S)"; \
	fi
	@if [ -f $(METRICS_LOG) ]; then \
		cp $(METRICS_LOG) $(ARCHIVE_DIR)/metrics_log.csv.backup.$$(date +%Y%m%d_%H%M%S) && \
		echo "✅ Backed up to: $(ARCHIVE_DIR)/metrics_log.csv.backup.$$(date +%Y%m%d_%H%M%S)"; \
	fi
	@rm -f $(METRICS_DATA)
	@rm -f $(METRICS_LOG)
	@rm -f $(LAST_RUN_FILE)
	@rm -f $(LAST_RUN_FILE).time
	@echo ""
	@echo "✅ All data flushed! Fresh start ready."
	@echo ""
	@echo "💡 Backups saved in $(ARCHIVE_DIR)/ with timestamp in case you need them."

# ════════════════════════════════════════════════════════════════
# SCHEDULING COMMANDS
# ════════════════════════════════════════════════════════════════

# Interactive sleep test
schedule-sleep-test:
	@echo "🧪 SLEEP/WAKE TEST SETUP"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	@echo "This test will prompt you to enter a future time."
	@echo "You'll then put your Mac to sleep, and when you wake it"
	@echo "after that time, the notification will trigger."
	@echo ""
	@echo "Current time: $$(date '+%H:%M')"
	@echo ""
	@chmod +x $(SCRIPTS_DIR)/setup_sleep_test_helper.sh 2>/dev/null || true; \
	$(SCRIPTS_DIR)/setup_sleep_test_helper.sh

# Restore after sleep test
schedule-restore-after-test:
	@echo "🔄 Restoring after sleep test..."
	@echo "Note: Restore script may need to be created in scripts/ directory"

# Schedule PROD: Interactive schedule setup
schedule-prod:
	@echo "🚀 PRODUCTION SCHEDULE SETUP"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	@echo "This will interactively configure your metrics reminder schedule."
	@echo ""
	@echo "Example: For Tuesday & Thursday at 10:30 AM, you would enter:"
	@echo "  Entry #1: Weekday 2, Hour 10, Minute 30"
	@echo "  Entry #2: Weekday 4, Hour 10, Minute 30"
	@echo ""
	@chmod +x $(SCRIPTS_DIR)/setup_prod_schedule.sh 2>/dev/null || true; \
	$(SCRIPTS_DIR)/setup_prod_schedule.sh

# Schedule TEST: Every 3 minutes (continuous)
schedule-test:
	@echo "🧪 Setting up TEST schedule..."
	@echo "   Every 3 minutes (starts immediately)"
	@chmod +x $(SCRIPTS_DIR)/create_test_plist.sh 2>/dev/null || true
	@chmod +x $(SCRIPTS_DIR)/smart_notify.sh 2>/dev/null || true
	@$(SCRIPTS_DIR)/create_test_plist.sh
	@launchctl unload $(TEST_PLIST) 2>/dev/null || true
	@launchctl load $(TEST_PLIST)
	@echo "✅ TEST schedule activated!"
	@echo "   First run: NOW (then every 3 minutes)"
	@echo "   Logs: tail -f $(TEST_LOG)"
	@echo ""
	@echo "⚠️  Remember to stop TEST mode when done:"
	@echo "   make schedule-stop-test"

# Stop PROD schedule
schedule-stop-prod:
	@echo "🛑 Stopping PROD schedule..."
	@launchctl unload $(PROD_PLIST) 2>/dev/null && echo "✅ PROD schedule stopped" || echo "⚠️  PROD schedule was not running"

# Stop TEST schedule
schedule-stop-test:
	@echo "🛑 Stopping TEST schedule..."
	@launchctl unload $(TEST_PLIST) 2>/dev/null && echo "✅ TEST schedule stopped" || echo "⚠️  TEST schedule was not running"

# Stop all schedules
schedule-stop-all: schedule-stop-prod schedule-stop-test
	@echo ""
	@echo "✅ All schedules stopped"

# Check schedule status
schedule-status:
	@echo "════════════════════════════════════════════════════════════"
	@echo "📅 SCHEDULE STATUS"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	@echo "🚀 PROD Schedule:"
	@if launchctl list | grep -q com.metricsTracker.prod; then \
		echo "   ✅ ACTIVE"; \
		if [ -f $(PROD_PLIST) ]; then \
			echo "   Configured times:"; \
			plutil -convert json -o /tmp/metrics_schedule.json $(PROD_PLIST) 2>/dev/null; \
			python3 -c "import json; data = json.load(open('/tmp/metrics_schedule.json')); intervals = data.get('StartCalendarInterval', []); days = {1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat', 7:'Sun'}; [print(f\"     • {days.get(i.get('Weekday', 0), 'Daily')} at {i.get('Hour', 0):02d}:{i.get('Minute', 0):02d}\") if 'Weekday' in i else print(f\"     • Daily at {i.get('Hour', 0):02d}:{i.get('Minute', 0):02d}\") for i in intervals]" 2>/dev/null || echo "     • $$(plutil -extract StartCalendarInterval json -o - $(PROD_PLIST) 2>/dev/null | grep -E 'Hour|Minute' | tr -d ' ' | paste -sd ' ' - || echo 'Schedule configured')"; \
			rm -f /tmp/metrics_schedule.json; \
		fi; \
		if [ -f $(LAST_RUN_FILE) ]; then \
			echo "   Last run: $$(cat $(LAST_RUN_FILE)) at $$(cat $(LAST_RUN_FILE).time 2>/dev/null || echo 'unknown')"; \
		else \
			echo "   Last run: Never"; \
		fi; \
		echo "   Logs: $(PROD_LOG)"; \
	else \
		echo "   ⚪ INACTIVE"; \
		echo "   Run: make schedule-prod"; \
	fi
	@echo ""
	@echo "🧪 TEST Schedule (Every 3 min):"
	@if launchctl list | grep -q com.metricsTracker.test; then \
		echo "   ✅ ACTIVE"; \
		echo "   Logs: $(TEST_LOG)"; \
		if [ -f $(TEST_LOG) ]; then \
			echo "   Last run: $$(tail -1 $(TEST_LOG) 2>/dev/null | grep -oE '\[.*\]' | head -1)"; \
		fi; \
	else \
		echo "   ⚪ INACTIVE"; \
		echo "   Run: make schedule-test"; \
	fi
	@echo ""
	@echo "📊 Streamlit App:"
	@if ps aux | grep -q "[s]treamlit run.*metrics_app"; then \
		echo "   ✅ RUNNING on $(STREAMLIT_URL)"; \
	else \
		echo "   ⚪ NOT RUNNING"; \
		echo "   Start: make start-bg"; \
	fi
	@echo ""
	@echo "════════════════════════════════════════════════════════════"
	@echo "💡 Quick Commands:"
	@echo "   make schedule-prod          # Enable production schedule"
	@echo "   make schedule-test          # Enable test schedule (3 min)"
	@echo "   make schedule-stop-prod     # Disable production"
	@echo "   make schedule-stop-test     # Disable test"
	@echo "   make schedule-stop-all      # Disable all schedules"
	@echo "   make schedule-status        # Show this status"
	@echo "════════════════════════════════════════════════════════════"

# Check overall status (legacy command - now includes schedules)
status: schedule-status
	@echo ""
	@echo "📋 Recent Activity (All Logs):"
	@echo "────────────────────────────────────────────────────────────"
	@if [ -f $(PROD_LOG) ]; then \
		echo "PROD:"; \
		tail -3 $(PROD_LOG) 2>/dev/null | sed 's/^/  /'; \
	fi
	@if [ -f $(TEST_LOG) ]; then \
		echo "TEST:"; \
		tail -3 $(TEST_LOG) 2>/dev/null | sed 's/^/  /'; \
	fi

# Help command
help:
	@echo "════════════════════════════════════════════════════════════"
	@echo "📊 METRICS TRACKER - Available Commands"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	@echo "🚀 APP CONTROL:"
	@echo "   make start              # Start app (background) + show status"
	@echo "   make start-fg           # Start app (foreground)"
	@echo "   make start-bg           # Start app (background only)"
	@echo "   make stop               # Stop app"
	@echo "   make restart            # Restart app"
	@echo "   make clean              # Clean cache & restart"
	@echo "   make test               # Run pre-flight checks"
	@echo ""
	@echo "💾 DATA MANAGEMENT:"
	@echo "   make flush-data         # Delete all data (creates backups)"
	@echo ""
	@echo "⏰ SCHEDULING:"
	@echo "   make schedule-prod      # Enable PROD (Tue/Thu 10:30)"
	@echo "   make schedule-test      # Enable TEST (every 3 min)"
	@echo "   make schedule-stop-prod # Disable PROD"
	@echo "   make schedule-stop-test # Disable TEST"
	@echo "   make schedule-stop-all  # Disable all schedules"
	@echo "   make schedule-status    # Show schedule status"
	@echo ""
	@echo "🧪 TESTING:"
	@echo "   make schedule-sleep-test         # Test sleep/wake behavior"
	@echo "   make schedule-restore-after-test # Restore after sleep test"
	@echo ""
	@echo "📊 STATUS:"
	@echo "   make status             # Show full status"
	@echo "   make schedule-status    # Show schedule status only"
	@echo "   make help               # Show this help"
	@echo ""
	@echo "════════════════════════════════════════════════════════════"