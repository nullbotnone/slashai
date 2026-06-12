import json
import time

# Current time in milliseconds
current_time_ms = 1780981553125

# Load the cron jobs data
with open('/home/rpi/.openclaw/workspace/projects/slashai/slashai/projects/slashai/cron_jobs.json', 'r') as f:
    data = json.load(f)

jobs = data['jobs']

# Analyze each job
report = []
overall_healthy = True

for job in jobs:
    job_id = job['id']
    name = job['name']
    enabled = job['enabled']
    state = job['state']
    last_run_at_ms = state.get('lastRunAtMs', 0)
    last_run_status = state.get('lastRunStatus', state.get('lastStatus', 'unknown'))
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_duration_ms = state.get('lastDurationMs', 0)
    next_run_at_ms = state.get('nextRunAtMs', 0)
    
    # Time since last run in milliseconds
    if last_run_at_ms > 0:
        time_since_last_run_ms = current_time_ms - last_run_at_ms
    else:
        time_since_last_run_ms = float('inf')
    
    # Calculate interval from last run to next run (if both are available)
    interval_ms = 0
    if last_run_at_ms > 0 and next_run_at_ms > 0:
        interval_ms = next_run_at_ms - last_run_at_ms
    
    # Check for issues
    issues = []
    if not enabled:
        issues.append("Job disabled unexpectedly")
        overall_healthy = False
    if consecutive_errors > 2:
        issues.append(f"Consecutive errors > 2 ({consecutive_errors})")
        overall_healthy = False
    if interval_ms > 0 and time_since_last_run_ms > 2 * interval_ms:
        issues.append(f"Haven't run in over 2x scheduled interval ({time_since_last_run_ms/1000:.0f}s > {2*interval_ms/1000:.0f}s)")
        overall_healthy = False
    if last_duration_ms > 3600000:  # 1 hour in milliseconds
        issues.append(f"Extremely long run time (> 1 hour): {last_duration_ms/1000:.0f}s")
        overall_healthy = False
    
    # Job info for report
    job_info = {
        'id': job_id,
        'name': name,
        'enabled': enabled,
        'last_run_status': last_run_status,
        'consecutive_errors': consecutive_errors,
        'last_duration_ms': last_duration_ms,
        'time_since_last_run_ms': time_since_last_run_ms,
        'interval_ms': interval_ms,
        'issues': issues
    }
    report.append(job_info)

# Generate markdown report
markdown = f"""# SlashAI Cron Health Report

**Generated at:** {time.ctime(current_time_ms/1000)} (America/Chicago)

## Overall System Health
**Status:** {'HEALTHY' if overall_healthy else 'ISSUES DETECTED'}

## Job Details

| Job ID | Name | Enabled | Last Run Status | Consecutive Errors | Last Run Duration (s) | Time Since Last Run (s) | Interval (s) | Issues |
|--------|------|---------|-----------------|---------------------|------------------------|--------------------------|--------------|--------|
"""
for job in report:
    issues_str = "<br>".join(job['issues']) if job['issues'] else "None"
    # Format interval
    if job['interval_ms'] > 0:
        interval_str = f"{job['interval_ms']/1000:.2f}"
    else:
        interval_str = "N/A"
    markdown += f"| {job['id']} | {job['name']} | {job['enabled']} | {job['last_run_status']} | {job['consecutive_errors']} | {job['last_duration_ms']/1000:.2f} | {job['time_since_last_run_ms']/1000:.2f} | {interval_str} | {issues_str} |\n"

markdown += "\n## Issues Detected\n"
if overall_healthy:
    markdown += "No issues detected.\n"
else:
    for job in report:
        if job['issues']:
            markdown += f"### {job['name']} (ID: {job['id']})\n"
            for issue in job['issues']:
                markdown += f"- {issue}\n"
            markdown += "\n"

markdown += "## Recommended Actions\n"
if not overall_healthy:
    for job in report:
        if job['issues']:
            markdown += f"### {job['name']}\n"
            for issue in job['issues']:
                markdown += f"- {issue}\n"
            markdown += "\n"
else:
    markdown += "- No actions required. All cron jobs are healthy.\n"

# Check the SlashAI Daily Tool Check job for consecutive errors
daily_tool_job = None
for job in report:
    if job['id'] == '7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d':
        daily_tool_job = job
        break

markdown += "\n## SlashAI Daily Tool Check Job\n"
if daily_tool_job:
    markdown += f"- Consecutive Errors: {daily_tool_job['consecutive_errors']}\n"
    if daily_tool_job['consecutive_errors'] > 0:
        markdown += "- **Action Required:** Manually trigger this job to test if the underlying issue is resolved.\n"
    else:
        markdown += "- No consecutive errors detected.\n"
else:
    markdown += "- Job not found.\n"

# Write the report to the specified path
report_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md'
with open(report_path, 'w') as f:
    f.write(markdown)

print(f"Health report saved to {report_path}")

# Log completion status to system logs
log_path = '/home/rpi/.openclaw/workspace/projects/slashai/logs/cron-health.log'
log_entry = f"{time.ctime(current_time_ms/1000)} - Cron health check completed. Overall health: {'HEALTHY' if overall_healthy else 'ISSUES DETECTED'}. Report saved to {report_path}\n"
with open(log_path, 'a') as f:
    f.write(log_entry)

print(f"Completion status logged to {log_path}")