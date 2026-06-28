#!/usr/bin/env python3
import json
import datetime
import time

# Load the cron jobs data
with open('/home/rpi/.openclaw/workspace/projects/slashai/cron_jobs_current.json', 'r') as f:
    data = json.load(f)

jobs = data['jobs']

# Current time from user: Monday, June 15th, 2026 - 06:08 (America/Chicago)
# Convert to datetime object
# We'll use the timestamp provided in seconds since epoch: 1781521680
current_timestamp_s = 1781521680  # 2026-06-15 06:08:00 America/Chicago in seconds since epoch
current_time_ms = current_timestamp_s * 1000

print(f"Current time: {datetime.datetime.fromtimestamp(current_timestamp_s, datetime.timezone(datetime.timedelta(hours=-5)))}")

# Scheduled interval parsing helper
def get_interval_seconds(schedule_expr):
    """Convert cron expression to interval in seconds (approximate for common patterns)"""
    # For simplicity, we'll handle common patterns in our data
    if schedule_expr.get('kind') == 'cron':
        expr = schedule_expr['expr']
        # Handle common patterns:
        # "0 */6 * * *" -> every 6 hours
        # "0 8 * * *" -> daily at 8 AM
        # "0 10 * * *" -> daily at 10 AM
        # "0 10 * * 1" -> weekly on Monday at 10 AM
        # "0 10 */14 * *" -> every 14 days at 10 AM
        # "0 10 1 * *" -> monthly on 1st at 10 AM
        
        parts = expr.split()
        if len(parts) == 5:
            minute, hour, day_of_month, month, day_of_week = parts
            
            # Every 6 hours
            if minute == '0' and hour == '*/6' and day_of_month == '*' and month == '*' and day_of_week == '*':
                return 6 * 3600  # 6 hours
            
            # Daily at specific hour
            if minute == '0' and hour != '*' and day_of_month == '*' and month == '*' and day_of_week == '*':
                return 24 * 3600  # 24 hours
            
            # Weekly (Monday = 1)
            if minute == '0' and hour == '10' and day_of_month == '*' and month == '*' and day_of_week == '1':
                return 7 * 24 * 3600  # 7 days
            
            # Every 14 days
            if minute == '0' and hour == '10' and day_of_month == '*/14' and month == '*' and day_of_week == '*':
                return 14 * 24 * 3600  # 14 days
            
            # Monthly (day 1)
            if minute == '0' and hour == '10' and day_of_month == '1' and month == '*' and day_of_week == '*':
                # Approximate month as 30 days
                return 30 * 24 * 3600  # 30 days
    
    # Default fallback
    return 24 * 3600  # 1 day

# Analyze each job
healthy_jobs = []
problematic_jobs = []

for job in jobs:
    job_id = job['id']
    name = job['name']
    enabled = job['enabled']
    
    state = job['state']
    last_run_at_ms = state.get('lastRunAtMs', 0)
    last_run_status = state.get('lastRunStatus', 'unknown')
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_duration_ms = state.get('lastDurationMs', 0)
    
    # Calculate time since last run
    if last_run_at_ms > 0:
        time_since_last_run_ms = current_time_ms - last_run_at_ms
        time_since_last_run_s = time_since_last_run_ms / 1000
    else:
        time_since_last_run_s = float('inf')
    
    # Get scheduled interval
    schedule = job['schedule']
    interval_s = get_interval_seconds(schedule)
    
    # Determine issues
    issues = []
    
    if not enabled:
        issues.append("Job disabled unexpectedly")
    
    if consecutive_errors > 2:
        issues.append(f"Consecutive errors > 2 ({consecutive_errors})")
    
    if time_since_last_run_s > 2 * interval_s:
        issues.append(f"Hasn't run in over 2x scheduled interval ({time_since_last_run_s/3600:.1f}h > {2*interval_s/3600:.1f}h)")
    
    if last_duration_ms > 3600000:  # > 1 hour
        issues.append(f"Extremely long run time ({last_duration_ms/1000:.0f}s > 3600s)")
    
    # Convert timestamps to readable strings
    last_run_str = "Never"
    if last_run_at_ms > 0:
        last_run_dt = datetime.datetime.fromtimestamp(last_run_at_ms/1000, datetime.timezone(datetime.timedelta(hours=-5)))
        last_run_str = last_run_dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    
    job_info = {
        'id': job_id,
        'name': name,
        'enabled': enabled,
        'last_run_status': last_run_status,
        'consecutive_errors': consecutive_errors,
        'last_run_duration_s': last_duration_ms / 1000,
        'time_since_last_run_s': time_since_last_run_s,
        'scheduled_interval_s': interval_s,
        'issues': issues,
        'last_run_str': last_run_str
    }
    
    if issues:
        problematic_jobs.append(job_info)
    else:
        healthy_jobs.append(job_info)

# Generate report
report_lines = []
report_lines.append("# SlashAI Cron Health Report")
report_lines.append(f"**Generated at:** {datetime.datetime.now().strftime('%a %d %b %H:%M:%S %Z %Y')}")
report_lines.append(f"**Current time (ms since epoch):** {current_time_ms}")
report_lines.append("")
report_lines.append("## Summary")
report_lines.append(f"- Total jobs: {len(jobs)}")
report_lines.append(f"- Healthy jobs: {len(healthy_jobs)}")
report_lines.append(f"- Jobs with issues: {len(problematic_jobs)}")
report_lines.append("")

if problematic_jobs:
    report_lines.append("## Issues Found")
    for job in problematic_jobs:
        report_lines.append(f"### {job['name']} (ID: {job['id']})")
        report_lines.append(f"- Status: {'ENABLED' if job['enabled'] else 'DISABLED'}")
        report_lines.append(f"- Last run: {job['last_run_status']}")
        report_lines.append(f"- Consecutive errors: {job['consecutive_errors']}")
        report_lines.append(f"- Last run duration: {job['last_run_duration_s']:.0f} seconds")
        report_lines.append(f"- Time since last run: {job['time_since_last_run_s']:.0f} seconds ({job['time_since_last_run_s']/3600:.1f} hours)")
        report_lines.append(f"- Scheduled interval: {job['scheduled_interval_s']:.0f} seconds ({job['scheduled_interval_s']/3600:.1f} hours)")
        report_lines.append("- Issues:")
        for issue in job['issues']:
            report_lines.append(f"  - {issue}")
        report_lines.append("")
else:
    report_lines.append("## Summary")
    report_lines.append("All jobs are healthy! No issues found.")
    report_lines.append("")

report_lines.append("## Recommendations")
if problematic_jobs:
    report_lines.append("1. Review disabled jobs and enable them if they should be running.")
    report_lines.append("2. Investigate jobs with consecutive errors > 2.")
    report_lines.append("3. Check jobs that haven't run in over 2x their scheduled interval for potential scheduling or execution problems.")
    report_lines.append("4. Look into jobs with extremely long run times (> 1 hour) for optimization or timeout issues.")
else:
    report_lines.append("No actions required. All cron jobs are operating normally.")

report_lines.append("")
report_lines.append("---")
report_lines.append("*This report was generated by the SlashAI Cron Health Monitor job (manual run).*")

# Write report to file
report_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md'
with open(report_path, 'w') as f:
    f.write('\n'.join(report_lines))

print(f"Report written to {report_path}")

# Also print to console for verification
print('\n'.join(report_lines))