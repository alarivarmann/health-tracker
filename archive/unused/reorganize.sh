#!/bin/bash
# Reorganize metrics-tracker folder structure

echo "🧹 METRICS TRACKER - FOLDER REORGANIZATION"
echo "══════════════════════════════════════════"
echo ""
echo "This will reorganize your project into a clean structure:"
echo "  src/       - Source code"
echo "  data/      - Data files"
echo "  logs/      - Log files"
echo "  docs/      - Documentation"
echo "  scripts/   - Utility scripts"
echo "  archive/   - Old/backup files"
echo ""
read -p "Continue? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "📦 Creating new folder structure..."

# Create new directories
mkdir -p src/modules
mkdir -p src/tests
mkdir -p data
mkdir -p logs
mkdir -p docs
mkdir -p scripts
mkdir -p archive/backups
mkdir -p archive/unused
mkdir -p archive/debug

echo "✅ Folders created"
echo ""
echo "📝 Moving files..."

# Move source code
echo "  → Moving source code to src/"
[ -f metrics_app.py ] && mv metrics_app.py src/
[ -f preflight_check.py ] && mv preflight_check.py src/

# Move modules
echo "  → Moving modules to src/modules/"
if [ -d modules ]; then
    mv modules/* src/modules/ 2>/dev/null
    rmdir modules 2>/dev/null
fi

# Move test files
echo "  → Moving tests to src/tests/"
[ -f test_alerting.py ] && mv test_alerting.py src/tests/
[ -f test_narrative_consistency.py ] && mv test_narrative_consistency.py src/tests/
[ -f test_user_scenario.py ] && mv test_user_scenario.py src/tests/

# Move scripts
echo "  → Moving scripts to scripts/"
[ -f smart_notify.sh ] && mv smart_notify.sh scripts/
[ -f setup_prod_schedule.sh ] && mv setup_prod_schedule.sh scripts/
[ -f create_prod_plist.sh ] && mv create_prod_plist.sh scripts/
[ -f create_test_plist.sh ] && mv create_test_plist.sh scripts/
[ -f setup_sleep_test_helper.sh ] && mv setup_sleep_test_helper.sh scripts/

# Move data files
echo "  → Moving data files to data/"
[ -f metrics_data.csv ] && mv metrics_data.csv data/
[ -f metrics_data.json ] && mv metrics_data.json data/
[ -f metrics_log.csv ] && mv metrics_log.csv data/
[ -f narratives.json ] && mv narratives.json data/
[ -f work_individual_metrics_tracker.yaml ] && mv work_individual_metrics_tracker.yaml data/
[ -f config.json ] && mv config.json data/

# Move log files
echo "  → Moving logs to logs/"
mv *.log logs/ 2>/dev/null
mv *.error.log logs/ 2>/dev/null

# Move documentation
echo "  → Moving documentation to docs/"
mv *.md docs/ 2>/dev/null

# Move backup files
echo "  → Moving backups to archive/backups/"
mv *.backup archive/backups/ 2>/dev/null
mv *.bak archive/backups/ 2>/dev/null
mv *.corrupted archive/backups/ 2>/dev/null
mv *.csv.backup.* archive/backups/ 2>/dev/null
mv *.json.backup.* archive/backups/ 2>/dev/null

# Move unused/old files
echo "  → Moving unused files to archive/unused/"
[ -f metrics_app_simple.py ] && mv metrics_app_simple.py archive/unused/
[ -f visualizer.py ] && mv visualizer.py archive/unused/
[ -f package.json ] && mv package.json archive/unused/
[ -f test_app.py ] && mv test_app.py archive/unused/
[ -f launch_streamlit.sh ] && mv launch_streamlit.sh archive/unused/
[ -f schedule_metrics.sh ] && mv schedule_metrics.sh archive/unused/
[ -f setup_notifications.sh ] && mv setup_notifications.sh archive/unused/
[ -f setup_final.sh ] && mv setup_final.sh archive/unused/
[ -f diagnose_prod_schedule.sh ] && mv diagnose_prod_schedule.sh archive/unused/
[ -f fix_plist.sh ] && mv fix_plist.sh archive/unused/
[ -f full_diagnostic.sh ] && mv full_diagnostic.sh archive/unused/
[ -f notify_metrics.sh ] && mv notify_metrics.sh archive/unused/
[ -f open_metrics_reminder.sh ] && mv open_metrics_reminder.sh archive/unused/
[ -f check_and_notify.sh ] && mv check_and_notify.sh archive/unused/
[ -f restore_after_sleep_test.sh ] && mv restore_after_sleep_test.sh archive/unused/
[ -f test_alerting.sh ] && mv test_alerting.sh archive/unused/
[ -f test_ports.sh ] && mv test_ports.sh archive/unused/
[ -f test_smart_notify.sh ] && mv test_smart_notify.sh archive/unused/
[ -f create_modules.sh ] && mv create_modules.sh archive/unused/
mv analysis_2025-*.txt archive/unused/ 2>/dev/null

# Move debug folders
echo "  → Moving debug files to archive/debug/"
[ -d debug ] && mv debug archive/debug/
[ -d cleanup ] && mv cleanup archive/debug/

# Delete temporary files
echo "  → Removing temporary files..."
rm -f .sleep_test_time
rm -f .last_prod_run.time

echo ""
echo "✅ Files moved"
echo ""
echo "🔧 Now updating file paths in scripts..."

# This will be done in the next step with actual path updates

echo ""
echo "══════════════════════════════════════════"
echo "✅ REORGANIZATION COMPLETE"
echo "══════════════════════════════════════════"
echo ""
echo "⚠️  IMPORTANT: Paths need to be updated in:"
echo "   - Makefile"
echo "   - scripts/smart_notify.sh"
echo "   - scripts/setup_prod_schedule.sh"
echo "   - src/modules/config.py"
echo "   - src/modules/data.py"
echo "   - src/modules/narratives.py"
echo ""
echo "Next step: Run the path update script"
