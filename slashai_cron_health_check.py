#!/usr/bin/env python3
import json
import subprocess
import sys
import re
import time
import datetime
import os

# Current time in milliseconds
def get_current_time_ms():
    return int(time.time() * 1000)

def get_cron_jobs():
    """Run openclaw cron list --json and return parsed JSON."""
    result = subprocess.run(['openclaw', 'cron', 'list', '--json'],
                            capture_output=True, text=True, check=True)
    return json.loads(result.stdout)

def cron_expr_to_interval_seconds(expr):
    """
    Convert a cron expression to an interval in seconds.
    Supports common patterns used in SlashAI jobs.
    Returns 0 if cannot determine.
    """
    # Split into 5 fields
    parts = expr.strip().split()
    if len(parts) != 5:
        return 0
    minute, hour, day_of_month, month, day_of_week = parts

    # Helper to check if a field is a fixed number (single integer)
    def is_fixed(field):
        return re.match(r'^\d+$', field) is not None

    # Helper to check if a field is a step expression like */6
    def is_step(field):
        return re.match(r'^\*/\d+$', field) is not None

    # Every 6 hours: minute=0, hour=*/6, day_of_month=*, month=*, day_of_week=*
    if (minute == '0' and is_step(hour) and hour.startswith('*/6') and
        day_of_month == '*' and month == '*' and day_of_week == '*'):
        step = int(hour[2:])
        return step * 3600  # hours to seconds

    # Daily: fixed minute and hour, day_of_month=*, month=*, day_of_week=*
    if (re.match(r'^\d+$', minute) is not None and
        re.match(r'^\d+$', hour) is not None and
        day_of_month == '*' and month == '*' and day_of_week == '*'):
        return 24 * 3600

    # Weekly: fixed minute and hour, day_of_month=*, month=*, day_of_week fixed (0-6 or 1-7)
    if (re.match(r'^\d+$', minute) is not None and
        re.match(r'^\d+$', hour) is not None and
        day_of_month == '*' and month == '*' and
        re.match(r'^\d+$', day_of_week) is not None):
        # Assuming day_of_week is a single number (0-6 or 0-7 where 0 and 7 are Sunday)
        # We'll treat as weekly
        return 7 * 24 * 3600

    # Monthly: fixed minute and hour, day_of_month fixed (1-31), month=*, day_of_week=*
    if (re.match(r'^\d+$', minute) is not None and
        re.match(r'^\d+$', hour) is not None and
        re.match(r'^\d+$', day_of_month) is not None and
        1 <= int(day_of_month) <= 31 and
        month == '*' and day_of_week == '*'):
        # Approximate a month as 30 days
        return 30 * 24 * 3600

    # Every 14 days: minute fixed, hour fixed, day_of_month=*/14, month=*, day_of_week=*
    if (re.match(r'^\d+$', minute) is not None and
        re.match(r'^\d+$', hour) is not None and
        is_step(day_of_month) and day_of_month.startswith('*/14') and
        month == '*' and day_of_week == '*'):
        step = int(day_of_month[2:])
        return step * 24 * 3600

    # If we cannot determine, return 0
    return 0

def trigger_cron_job(job_id):
    """Manually trigger a cron job using openclaw cron trigger."""
    try:
        result = subprocess.run(['openclaw', 'cron', 'trigger', job_id],
                                capture_output=True, text=True, check=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def main():
    current_time_ms = get_current_time_ms()
    current_time_str = datetime.datetime.fromtimestamp(current_time_ms / 1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    try:
        jobs_data = get_cron_jobs()
    except Exception as e:
        print(f"Error fetching cron jobs: {e}", file=sys.stderr)
        sys.exit(1)
    
    jobs = jobs_data.get('jobs', [])

    # Prepare report lines
    report_lines = []
    report_lines.append("# SlashAI Cron Health Report")
    report_lines.append(f"Generated: {current_time_str}")
    report_lines.append(f"Total Jobs: {len(jobs)}")
    report_lines.append("")

    # Summary counters
    total_jobs = len(jobs)
    enabled_count = 0
    disabled_unexpected = []
    excessive_errors = []
    interval_issues = []
    long_runtime = []
    
    # For manual trigger tracking
    daily_tool_check_job = None
    manual_trigger_performed = False
    manual_trigger_result = None

    for job in jobs:
        job_id = job.get('id')
        name = job.get('name')
        enabled = job.get('enabled', False)
        state = job.get('state', {})
        schedule = job.get('schedule', {})
        expr = schedule.get('expr', '') if isinstance(schedule, dict) else ''

        if enabled:
            enabled_count += 1
        else:
            disabled_unexpected.append((job_id, name))
            # Still check other issues for disabled jobs? Usually we'd skip, but let's check errors and runtime at least
            # We'll continue to check errors and runtime but skip interval check for disabled jobs
        
        # Store reference to Daily Tool Check job for potential manual trigger
        if job_id == "7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d":
            daily_tool_check_job = job

        last_run_status = state.get('lastRunStatus', 'unknown')
        consecutive_errors = state.get('consecutiveErrors', 0)
        last_duration_ms = state.get('lastDurationMs', 0)
        last_run_at_ms = state.get('lastRunAtMs', 0)

        # Check consecutive errors > 2
        if consecutive_errors > 2:
            excessive_errors.append((job_id, name, consecutive_errors, last_run_status))

        # Check extremely long run time (> 1 hour)
        if last_duration_ms > 3600000:  # 1 hour in ms
            long_runtime.append((job_id, name, last_duration_ms))

        # Check if hasn't run in over 2x scheduled interval (only for enabled jobs)
        if enabled:  # Only check interval for enabled jobs
            interval_seconds = cron_expr_to_interval_seconds(expr)
            if interval_seconds > 0:
                time_since_ms = current_time_ms - last_run_at_ms
                threshold_ms = 2 * interval_seconds * 1000
                if time_since_ms > threshold_ms:
                    interval_issues.append((job_id, name, time_since_ms // 1000, interval_seconds, last_run_at_ms))
            # If we cannot determine interval, we skip this check
        # For disabled jobs, we skip interval check

    # Check if Daily Tool Check job has consecutive errors and needs manual trigger
    if daily_tool_check_job:
        state = daily_tool_check_job.get('state', {})
        consecutive_errors = state.get('consecutiveErrors', 0)
        if consecutive_errors > 0:
            print(f"SlashAI Daily Tool Check job has {consecutive_errors} consecutive error(s). Attempting manual trigger...")
            success, output = trigger_cron_job("7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d")
            manual_trigger_performed = success
            manual_trigger_result = output
            if success:
                print("Manual trigger successful.")
            else:
                print(f"Manual trigger failed: {output}", file=sys.stderr)

    # Build report
    report_lines.append(f"Total jobs: {total_jobs}")
    report_lines.append(f"Enabled jobs: {enabled_count}")
    report_lines.append(f"Disabled jobs: {total_jobs - enabled_count}")
    report_lines.append("")

    # Job details table
    report_lines.append("## Job Details")
    report_lines.append("")
    report_lines.append("| Job Name | ID | Enabled | Last Run Status | Consecutive Errors | Last Run Duration | Time Since Last Run | Schedule |")
    report_lines.append("|----------|----|---------|-----------------|--------------------|-------------------|---------------------|----------|")
    
    for job in jobs:
        job_id = job.get('id')
        name = job.get('name')
        enabled = job.get('enabled', False)
        state = job.get('state', {})
        schedule = job.get('schedule', {})
        expr = schedule.get('expr', '') if isinstance(schedule, dict) else ''
        
        last_run_status = state.get('lastRunStatus', 'unknown')
        consecutive_errors = state.get('consecutiveErrors', 0)
        last_duration_ms = state.get('lastDurationMs', 0)
        last_run_at_ms = state.get('lastRunAtMs', 0)
        
        # Format duration
        if last_duration_ms >= 3600000:
            duration_str = f"{last_duration_ms / 3600000:.2f} hours"
        elif last_duration_ms >= 60000:
            duration_str = f"{last_duration_ms / 60000:.1f} minutes"
        else:
            duration_str = f"{last_duration_ms} ms"
            
        # Format time since last run
        if last_run_at_ms > 0:
            time_since_ms = current_time_ms - last_run_at_ms
            if time_since_ms >= 86400000:
                time_since_str = f"{time_since_ms / 86400000:.1f} days"
            elif time_since_ms >= 3600000:
                time_since_str = f"{time_since_ms / 3600000:.1f} hours"
            elif time_since_ms >= 60000:
                time_since_str = f"{time_since_ms / 60000:.1f} minutes"
            else:
                time_since_str = f"{time_since_ms / 1000:.1f} seconds"
        else:
            time_since_str = "Never"
            
        report_lines.append(f"| {name} | {job_id} | {enabled} | {last_run_status} | {consecutive_errors} | {duration_str} | {time_since_str} | {expr} |")
    
    report_lines.append("")

    if disabled_unexpected:
        report_lines.append("## Jobs Disabled Unexpectedly")
        for job_id, name in disabled_unexpected:
            report_lines.append(f"- {name} (ID: {job_id})")
        report_lines.append("")

    if excessive_errors:
        report_lines.append("## Jobs with Consecutive Errors > 2")
        for job_id, name, count, status in excessive_errors:
            report_lines.append(f"- {name} (ID: {job_id}): {count} consecutive errors, last status: {status}")
        report_lines.append("")

    if long_runtime:
        report_lines.append("## Jobs with Extremely Long Run Time (> 1 hour)")
        for job_id, name, duration_ms in long_runtime:
            duration_hr = duration_ms / 3600000
            report_lines.append(f"- {name} (ID: {job_id}): {duration_hr:.2f} hours")
        report_lines.append("")

    if interval_issues:
        report_lines.append("## Jobs That Haven't Run in Over 2x Their Scheduled Interval")
        for job_id, name, time_since_sec, interval_sec, last_run_at_ms in interval_issues:
            time_since_hr = time_since_sec / 3600
            interval_hr = interval_sec / 3600
            report_lines.append(f"- {name} (ID: {job_id}): last run {time_since_hr:.2f} hours ago, interval {interval_hr:.2f} hours")
        report_lines.append("")

    # Overall system health
    report_lines.append("## Overall System Health")
    if not (disabled_unexpected or excessive_errors or long_runtime or interval_issues):
        report_lines.append("**Status:** ✅ HEALTHY - No issues detected.")
    else:
        report_lines.append("**Status:** ⚠️ ISSUES DETECTED - See above for details.")
    report_lines.append("")

    # Recommended actions
    report_lines.append("## Recommended Actions")
    if disabled_unexpected:
        report_lines.append("1. Investigate why jobs were disabled and re-enable if appropriate.")
    if excessive_errors:
        report_lines.append("2. Investigate the root cause of repeated failures for jobs with consecutive errors > 2.")
    if long_runtime:
        report_lines.append("3. Optimize or investigate jobs with extremely long run times to reduce execution duration.")
    if interval_issues:
        report_lines.append("4. Check the cron scheduler and system time for jobs that are not running on schedule.")
    if not (disabled_unexpected or excessive_errors or long_runtime or interval_issues):
        report_lines.append("No specific actions required. Continue monitoring.")

    # SlashAI Daily Tool Check Manual Trigger section
    report_lines.append("")
    report_lines.append("## SlashAI Daily Tool Check Manual Trigger")
    if daily_tool_check_job:
        state = daily_tool_check_job.get('state', {})
        consecutive_errors = state.get('consecutiveErrors', 0)
        if consecutive_errors > 0:
            if manual_trigger_performed:
                trigger_time = datetime.datetime.fromtimestamp(current_time_ms / 1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
                report_lines.append(f"The SlashAI Daily Tool Check job (ID: 7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d) had {consecutive_errors} consecutive error(s).")
                report_lines.append(f"As per instructions, this job was manually triggered to test if the underlying issue is resolved.")
                report_lines.append(f"**Manual trigger completed at**: {trigger_time}")
                if manual_trigger_result:
                    report_lines.append(f"**Trigger output**: {manual_trigger_result}")
            else:
                report_lines.append(f"The SlashAI Daily Tool Check job (ID: 7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d) had {consecutive_errors} consecutive error(s).")
                report_lines.append(f"Manual trigger was attempted but failed.")
                if manual_trigger_result:
                    report_lines.append(f"**Error**: {manual_trigger_result}")
        else:
            report_lines.append(f"The SlashAI Daily Tool Check job (ID: 7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d) has 0 consecutive errors.")
            report_lines.append(f"No manual trigger was needed as per instructions.")
    else:
        report_lines.append("SlashAI Daily Tool Check job not found.")

    # Write the report to the specified file
    report_path = "/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md"
    # Ensure directory exists
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))

    print(f"Health report written to {report_path}")
    
    # Log completion status to system logs
    log_path = "/home/rpi/.openclaw/workspace/projects/slashai/slashai/system.log"
    try:
        with open(log_path, 'a') as log_file:
            log_file.write(f"[{datetime.datetime.now().isoformat()}] Cron health check completed. Report saved to {report_path}\n")
            if manual_trigger_performed:
                log_file.write(f"[{datetime.datetime.now().isoformat()}] SlashAI Daily Tool Check job manually triggered.\n")
    except Exception as e:
        print(f"Warning: Could not write to system log: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()