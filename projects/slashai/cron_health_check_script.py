#!/usr/bin/env python3
import json
import datetime
import os

# Load the cron jobs data
json_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron_jobs_current.json'
with open(json_path, 'r') as f:
    data = json.load(f)

jobs = data['jobs']

# Current time as given: Sunday, June 14th, 2026 - 00:02 (America/Chicago)
# Convert to milliseconds since epoch
# America/Chicago in June is CDT (UTC-5)
cdt_offset = -5  # hours
naive_dt = datetime.datetime(2026, 6, 14, 0, 2, 0)  # local time without timezone
# Make it timezone-aware for CDT
cdt = datetime.timezone(datetime.timedelta(hours=cdt_offset))
aware_dt = naive_dt.replace(tzinfo=cdt)
# Convert to UTC timestamp
current_time_ms = int(aware_dt.timestamp() * 1000)

# Function to get interval in milliseconds from cron expression
def get_interval_ms(cron_expr):
    # We handle specific expressions we know
    if cron_expr == "0 */6 * * *":
        return 6 * 60 * 60 * 1000  # 6 hours
    elif cron_expr == "0 8 * * *":
        return 24 * 60 * 60 * 1000  # 1 day
    elif cron_expr == "0 10 * * *":
        return 24 * 60 * 60 * 1000  # 1 day
    elif cron_expr == "0 10 * * 1":
        return 7 * 24 * 60 * 60 * 1000  # 1 week
    elif cron_expr == "0 10 */14 * *":
        return 14 * 24 * 60 * 60 * 1000  # 14 days
    elif cron_expr == "0 10 1 * *":
        # Approximate month as 30 days
        return 30 * 24 * 60 * 60 * 1000
    else:
        # Unknown, default to 24 hours
        return 24 * 60 * 60 * 1000

# Analyze each job
report_lines = []
report_lines.append("# SlashAI Cron Health Report")
report_lines.append(f"**Generated at:** {datetime.datetime.now().isoformat()}")
report_lines.append("")
report_lines.append("## Summary")
report_lines.append("")

# Counters
total_jobs = len(jobs)
enabled_count = sum(1 for j in jobs if j.get('enabled', False))
disabled_count = total_jobs - enabled_count
error_jobs = [j for j in jobs if j.get('state', {}).get('lastRunStatus') == 'error']
consecutive_error_jobs = [j for j in jobs if j.get('state', {}).get('consecutiveErrors', 0) > 2]
long_running_jobs = [j for j in jobs if j.get('state', {}).get('lastDurationMs', 0) > 3600000]  # >1 hour
overdue_jobs = []

for job in jobs:
    state = job.get('state', {})
    last_run_at_ms = state.get('lastRunAtMs', 0)
    if last_run_at_ms == 0:
        # Never run, skip overdue check (or treat as overdue?)
        continue
    interval_ms = get_interval_ms(job.get('schedule', {}).get('expr', '0 0 * * *'))
    time_since_last_run = current_time_ms - last_run_at_ms
    if time_since_last_run > 2 * interval_ms:
        overdue_jobs.append(job)

# Overall health
if len(error_jobs) == 0 and len(consecutive_error_jobs) == 0 and len(long_running_jobs) == 0 and len(overdue_jobs) == 0:
    overall_health = "HEALTHY"
elif len(consecutive_error_jobs) == 0 and len(long_running_jobs) == 0 and len(overdue_jobs) == 0:
    overall_health = "MOSTLY HEALTHY (some errors)"
else:
    overall_health = "ISSUES DETECTED"

report_lines.append(f"- **Overall Health:** {overall_health}")
report_lines.append(f"- **Total Jobs:** {total_jobs}")
report_lines.append(f"- **Enabled Jobs:** {enabled_count}")
report_lines.append(f"- **Disabled Jobs:** {disabled_count}")
report_lines.append(f"- **Jobs with Last Run Error:** {len(error_jobs)}")
report_lines.append(f"- **Jobs with Consecutive Errors > 2:** {len(consecutive_error_jobs)}")
report_lines.append(f"- **Jobs with Run Time > 1 Hour:** {len(long_running_jobs)}")
report_lines.append(f"- **Jobs Overdue (last run > 2x interval):** {len(overdue_jobs)}")
report_lines.append("")

# Details of problematic jobs
if error_jobs or consecutive_error_jobs or long_running_jobs or overdue_jobs:
    report_lines.append("## Problematic Jobs")
    report_lines.append("")
    for job in jobs:
        job_id = job.get('id', 'unknown')
        name = job.get('name', 'Unknown')
        state = job.get('state', {})
        enabled = job.get('enabled', False)
        last_run_status = state.get('lastRunStatus', 'unknown')
        last_run_at_ms = state.get('lastRunAtMs', 0)
        last_duration_ms = state.get('lastDurationMs', 0)
        consecutive_errors = state.get('consecutiveErrors', 0)
        next_run_at_ms = state.get('nextRunAtMs', 0)
        
        # Compute time since last run
        if last_run_at_ms > 0:
            time_since_last_run_ms = current_time_ms - last_run_at_ms
            time_since_last_run_str = str(datetime.timedelta(milliseconds=time_since_last_run_ms))
        else:
            time_since_last_run_str = "Never"
        
        # Determine if problematic
        issues = []
        if not enabled:
            issues.append("Disabled")
        if last_run_status == 'error':
            issues.append("Last run error")
        if consecutive_errors > 2:
            issues.append(f"Consecutive errors: {consecutive_errors}")
        if last_duration_ms > 3600000:
            issues.append(f"Run time > 1 hour: {last_duration_ms // 1000}s")
        interval_ms = get_interval_ms(job.get('schedule', {}).get('expr', '0 0 * * *'))
        if last_run_at_ms > 0 and time_since_last_run_ms > 2 * interval_ms:
            issues.append(f"Overdue (>{interval_ms//1000//60//60}h interval)")
        
        if issues:
            report_lines.append(f"### {name} (`{job_id}`)")
            report_lines.append(f"- **Enabled:** {enabled}")
            report_lines.append(f"- **Last Run Status:** {last_run_status}")
            report_lines.append(f"- **Last Run At:** {datetime.datetime.fromtimestamp(last_run_at_ms/1000, datetime.timezone.utc).isoformat() if last_run_at_ms else 'Never'}")
            report_lines.append(f"- **Time Since Last Run:** {time_since_last_run_str}")
            report_lines.append(f"- **Last Run Duration:** {last_duration_ms // 1000} seconds")
            report_lines.append(f"- **Consecutive Errors:** {consecutive_errors}")
            report_lines.append(f"- **Next Run At:** {datetime.datetime.fromtimestamp(next_run_at_ms/1000, datetime.timezone.utc).isoformat() if next_run_at_ms else 'N/A'}")
            report_lines.append(f"- **Issues:** {', '.join(issues)}")
            report_lines.append("")
            
            # Store info for Daily Tool Check
            if job_id == "7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d":
                daily_tool_check_issues = issues
                daily_tool_check_consecutive_errors = consecutive_errors
else:
    report_lines.append("## No problematic jobs found.")
    report_lines.append("")
    daily_tool_check_issues = []
    daily_tool_check_consecutive_errors = 0

# Write the report
report_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md'
with open(report_path, 'w') as f:
    f.write('\n'.join(report_lines))

print(f"Health report written to {report_path}")
print(f"Daily Tool Check consecutive errors: {daily_tool_check_consecutive_errors}")
if daily_tool_check_consecutive_errors > 0:
    print("Daily Tool Check has consecutive errors - trigger flag set")
else:
    print("Daily Tool Check consecutive errors: 0")

# Also output a simple status for logging
print("CRON_HEALTH_CHECK_COMPLETED")