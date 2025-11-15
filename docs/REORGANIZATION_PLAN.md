# Folder Reorganization Plan

## Current Issues
- Root folder cluttered with 70+ files
- Logs, data, code, docs all mixed together
- Multiple backup and test files
- Hard to find what you need

## New Structure

```
metrics-tracker/
├── src/                          # Source code
│   ├── metrics_app.py           # Main app
│   ├── preflight_check.py       # Pre-flight checks
│   ├── modules/                 # Core modules
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── data.py
│   │   ├── narratives.py
│   │   ├── analysis.py
│   │   ├── insights.py
│   │   └── severity.py
│   └── tests/                   # Test files
│       ├── test_alerting.py
│       ├── test_narrative_consistency.py
│       └── test_user_scenario.py
├── data/                         # Data files
│   ├── metrics_data.csv
│   ├── metrics_data.json
│   ├── metrics_log.csv
│   ├── narratives.json
│   └── work_individual_metrics_tracker.yaml
├── logs/                         # Log files
│   ├── metrics-tracker.log
│   ├── notify_prod.log
│   ├── notify_test.log
│   └── streamlit_test.log
├── docs/                         # Documentation
│   ├── README.md
│   ├── QUICK_REFERENCE.md
│   ├── SCHEDULE_FIX_SUMMARY.md
│   ├── SLEEP_WAKE_FIX.md
│   └── (all other .md files)
├── scripts/                      # Setup and utility scripts
│   ├── smart_notify.sh          # Production notification script
│   ├── setup_prod_schedule.sh   # Schedule setup
│   ├── create_prod_plist.sh
│   └── setup_sleep_test_helper.sh
├── archive/                      # Old/backup files
│   ├── metrics_app.py.backup
│   ├── smart_notify.sh.backup
│   ├── cleanup/
│   └── debug/
├── .streamlit/                   # Streamlit config
├── .venv/                        # Virtual environment
├── Makefile                      # Keep at root
├── pyproject.toml                # Keep at root
├── uv.lock                       # Keep at root
├── .env                          # Keep at root
└── .python-version               # Keep at root
```

## Files to Keep (Essential)

### Root (Configuration)
- Makefile
- pyproject.toml, uv.lock
- .env, .python-version
- config.json

### Source Code → src/
- metrics_app.py (main app)
- preflight_check.py
- modules/* → src/modules/

### Scripts → scripts/
- smart_notify.sh
- setup_prod_schedule.sh
- create_prod_plist.sh
- create_test_plist.sh
- setup_sleep_test_helper.sh

### Data → data/
- metrics_data.csv (if exists)
- metrics_data.json
- metrics_log.csv
- narratives.json (if exists)
- work_individual_metrics_tracker.yaml

### Logs → logs/
- All *.log files
- All *.error.log files

### Documentation → docs/
- All *.md files

## Files to Archive

### Backups → archive/backups/
- *.backup files
- *.bak files
- *.corrupted files

### Old/Unused → archive/unused/
- metrics_app_simple.py
- visualizer.py
- package.json
- test_app.py
- launch_streamlit.sh
- schedule_metrics.sh
- setup_notifications.sh
- setup_final.sh
- diagnose_prod_schedule.sh
- fix_plist.sh
- full_diagnostic.sh
- notify_metrics.sh
- open_metrics_reminder.sh
- check_and_notify.sh
- restore_after_sleep_test.sh
- test_alerting.sh
- test_ports.sh
- test_smart_notify.sh
- create_modules.sh
- analysis_2025-*.txt

### Debug → archive/debug/
- debug/ folder
- cleanup/ folder

## Files to Delete
- .sleep_test_time (temp file)
- .last_prod_run.time (will be recreated)
- reminder.log (empty or old)
- Various backup CSV files from Nov 14

## Path Updates Needed

### Makefile
- Update paths to src/metrics_app.py
- Update paths to logs/
- Update paths to src/preflight_check.py

### smart_notify.sh
- LOG_FILE="$HOME/metrics-tracker/logs/notify_prod.log"
- Update Streamlit path

### setup_prod_schedule.sh
- Update script paths
- Update log paths

### src/modules/config.py
- DATA_FILE = Path("data/metrics_data.csv")
- Update all data paths

### src/modules/data.py
- Update DATA_FILE path

### src/modules/narratives.py
- Update narratives.json path
