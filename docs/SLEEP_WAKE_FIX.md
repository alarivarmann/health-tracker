# Sleep/Wake Schedule Fix - Documentation

## Problem Summary
The metrics tracker had two main issues:

1. **Sleep/Wake Issue**: When the Mac went to sleep during the scheduled reminder time, the notification would not trigger when the Mac woke up.
2. **Status Display Issue**: `make schedule-status` showed hardcoded "Tue/Thu 10:30" instead of the actual configured schedule.

## Root Causes

### 1. Test Mode Script Still Active
The `smart_notify.sh` script was still in **SLEEP TEST mode** instead of production mode. It was checking for a test file (`.sleep_test_time`) instead of reading the actual schedule from the plist.

### 2. No Catch-Up Mechanism
LaunchD's `StartCalendarInterval` only triggers at the exact scheduled time. If the Mac is asleep, it doesn't "catch up" when it wakes up.

### 3. Hardcoded Status Display
The Makefile had hardcoded schedule display text instead of dynamically reading from the plist file.

## Solutions Implemented

### 1. Restored Production Mode Logic in `smart_notify.sh`
- ✅ Reads schedule directly from the plist file (`com.metricsTracker.prod.plist`)
- ✅ Checks current weekday against all scheduled weekdays in the plist
- ✅ Implements a **60-minute grace period** for missed schedules
- ✅ Tracks last run date AND time to prevent duplicate runs

### 2. Grace Period Catch-Up Mechanism
When the script runs (triggered by LaunchD's `RunAtLoad` or any wake event):
- Checks if today is a scheduled weekday
- Checks if current time is AFTER the scheduled time
- If within 60 minutes of the scheduled time AND hasn't run today yet → **triggers notification**
- This ensures notifications happen even if the Mac was asleep during the exact scheduled time

### 3. Dynamic Status Display
The `make schedule-status` command now:
- ✅ Reads the actual plist file
- ✅ Parses all `StartCalendarInterval` entries
- ✅ Displays each scheduled day and time dynamically
- ✅ Shows the last run date and time

## How It Works Now

### Schedule Configuration Flow
1. Run `make schedule-prod` and enter your desired times
2. Script creates `com.metricsTracker.prod.plist` with `StartCalendarInterval` entries
3. LaunchD loads the schedule

### Notification Trigger Flow
1. **At Scheduled Time**: LaunchD triggers `smart_notify.sh` at exact scheduled time
2. **On Wake**: LaunchD's `RunAtLoad` triggers `smart_notify.sh` when Mac wakes
3. **Smart Check**: Script checks:
   - Is today a scheduled weekday?
   - Has it already run today?
   - If scheduled time has passed, is it within the 60-minute grace period?
4. **Action**: If all checks pass, notification triggers and Streamlit opens

### Current Configuration (as of Nov 14, 2025)
```
Schedule: Friday at 16:36
Status: Active
Last Run: 2025-11-14
Grace Period: 60 minutes
```

## Testing Recommendations

### Test 1: Normal Schedule
1. Set a schedule for tomorrow at a specific time
2. Keep Mac awake
3. Verify notification triggers at exact time

### Test 2: Sleep During Schedule
1. Set a schedule for 5 minutes from now
2. Put Mac to sleep immediately
3. Wake Mac 10 minutes later (within 60-min grace period)
4. Verify notification triggers immediately upon wake

### Test 3: Wake After Grace Period
1. Set a schedule for a specific time
2. Put Mac to sleep before that time
3. Wake Mac 90 minutes after scheduled time (beyond grace period)
4. Verify notification does NOT trigger (too late)

### Test 4: Already Ran Today
1. Schedule triggers successfully in the morning
2. Put Mac to sleep, then wake it later the same day
3. Verify notification does NOT trigger again (already ran today)

## Files Modified
- ✅ `/Users/alavar/metrics-tracker/smart_notify.sh` - Restored production logic with grace period
- ✅ `/Users/alavar/metrics-tracker/Makefile` - Fixed schedule-status to show dynamic schedule
- ✅ Schedule reloaded with `launchctl`

## Key Features
- **Grace Period**: 60 minutes (configurable in `smart_notify.sh` via `GRACE_PERIOD_MINS`)
- **Once-Per-Day**: Uses `.last_prod_run` file to prevent duplicate runs
- **Multi-Schedule**: Supports multiple days/times in one plist
- **Auto-Start**: Starts Streamlit automatically if not running
- **Robust Logging**: Detailed logs in `~/metrics-tracker/notify_prod.log`

## Adjusting Grace Period
To change the grace period, edit `smart_notify.sh`:
```bash
GRACE_PERIOD_MINS=60  # Change this value (in minutes)
```
Then reload: `make schedule-stop-prod && make schedule-prod`

## Commands Reference
```bash
make schedule-prod          # Configure production schedule
make schedule-status        # View current schedule (dynamic)
make schedule-stop-prod     # Stop production schedule
make schedule-stop-all      # Stop all schedules
```
