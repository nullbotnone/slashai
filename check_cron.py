#!/usr/bin/env python3
import json
import subprocess
import sys
import re

# Current time in milliseconds from the prompt (UTC: 2026-06-04 11:02:00)
# We got this from the date command: 1780570920000
current_time_ms = 1780570920000

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

def main():
    jobs_data = get_cron_jobs()
    jobs = jobs_data.get('jobs', [])

    # Prepare report lines
    report_lines = []
    report_lines.append("# SlashAI Cron Health Check Report")
    report_lines.append(f"Generated at: {current_time_ms} ms since epoch (UTC)")
    report_lines.append("")

    # Summary counters
    total_jobs = len(jobs)
    enabled_count = 0
    disabled_unexpected = []
    excessive_errors = []
    interval_issues = []
    long_runtime = []

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
            continue  # Skip further checks for disabled jobs? We still might want to check other things? Let's still check.

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

        # Check if hasn't run in over 2x scheduled interval
        interval_seconds = cron_expr_to_interval_seconds(expr)
        if interval_seconds > 0:
            time_since_ms = current_time_ms - last_run_at_ms
            threshold_ms = 2 * interval_seconds * 1000
            if time_since_ms > threshold_ms:
                interval_issues.append((job_id, name, time_since_ms // 1000, interval_seconds, last_run_at_ms))
        else:
            # If we cannot determine interval, we skip this check
            pass

    # Build report
    report_lines.append(f"Total jobs: {total_jobs}")
    report_lines.append(f"Enabled jobs: {enabled_count}")
    report_lines.append(f"Disabled jobs: {total_jobs - enabled_count}")
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

    # Write the report to the specified file
    report_path = "/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md"
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))

    print(f"Health report written to {report_path}")

if __name__ == '__main__':
    main()
