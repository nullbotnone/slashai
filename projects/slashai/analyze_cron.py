import json
import time
import os

# Load the cron jobs data
cron_file = '/home/rpi/.openclaw/workspace/projects/slashai/cron_jobs.json'
with open(cron_file, 'r') as f:
    data = json.load(f)

jobs = data.get('jobs', [])
current_time_ms = int(time.time() * 1000)

report_lines = []
report_lines.append("# SlashAI Cron Health Report")
report_lines.append(f"Generated at: {time.ctime()}")
report_lines.append(f"Current timestamp: {current_time_ms}")
report_lines.append("")

# Overall stats
total_jobs = len(jobs)
enabled_jobs = sum(1 for j in jobs if j.get('enabled', False))
disabled_jobs = total_jobs - enabled_jobs
report_lines.append(f"Total jobs: {total_jobs}")
report_lines.append(f"Enabled jobs: {enabled_jobs}")
report_lines.append(f"Disabled jobs: {disabled_jobs}")
report_lines.append("")

# Analyze each job
issues = []
for job in jobs:
    job_id = job.get('id', 'unknown')
    name = job.get('name', 'Unknown Job')
    enabled = job.get('enabled', False)
    state = job.get('state', {})
    schedule = job.get('schedule', {})
    
    last_run_at = state.get('lastRunAtMs', 0)
    last_run_status = state.get('lastRunStatus', 'unknown')
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_duration_ms = state.get('lastDurationMs', 0)
    last_delivered = state.get('lastDelivered', False)
    next_run_at = state.get('nextRunAtMs', 0)
    
    # Calculate time since last run
    time_since_last_run_ms = current_time_ms - last_run_at if last_run_at > 0 else None
    time_since_last_run_hrs = time_since_last_run_ms / (1000 * 3600) if time_since_last_run_ms is not None else None
    
    # Calculate expected interval from schedule (simplified: using nextRunAtMs - lastRunAtMs)
    expected_interval_ms = None
    if last_run_at > 0 and next_run_at > 0 and next_run_at > last_run_at:
        expected_interval_ms = next_run_at - last_run_at
    
    # Check for issues
    job_issues = []
    
    if not enabled:
        job_issues.append("Job is disabled")
    
    if consecutive_errors > 2:
        job_issues.append(f"High consecutive errors: {consecutive_errors}")
    
    if expected_interval_ms and time_since_last_run_ms is not None:
        if time_since_last_run_ms > 2 * expected_interval_ms:
            job_issues.append(f"Not run in over 2x interval (last run: {time_since_last_run_hrs:.1f} hrs ago, expected interval: {expected_interval_ms/(1000*3600):.1f} hrs)")
    
    if last_duration_ms > 3600000:  # > 1 hour
        job_issues.append(f"Extremely long run time: {last_duration_ms/(1000*3600):.1f} hours")
    
    if last_run_status == 'error':
        job_issues.append(f"Last run status: error")
    
    if job_issues:
        issues.append({
            'id': job_id,
            'name': name,
            'issues': job_issues,
            'details': {
                'enabled': enabled,
                'last_run_status': last_run_status,
                'consecutive_errors': consecutive_errors,
                'last_duration_hrs': last_duration_ms/(1000*3600) if last_duration_ms else 0,
                'time_since_last_run_hrs': time_since_last_run_hrs,
                'next_run_at': time.ctime(next_run_at/1000) if next_run_at else 'None'
            }
        })
    
    # Add job info to report
    report_lines.append(f"## {name} (ID: {job_id})")
    report_lines.append(f"- **Enabled**: {enabled}")
    report_lines.append(f"- **Last Run Status**: {last_run_status}")
    report_lines.append(f"- **Consecutive Errors**: {consecutive_errors}")
    report_lines.append(f"- **Last Run Duration**: {last_duration_ms/(1000*60):.1f} minutes ({last_duration_ms} ms)")
    if time_since_last_run_hrs is not None:
        report_lines.append(f"- **Time Since Last Run**: {time_since_last_run_hrs:.1f} hours")
    else:
        report_lines.append(f"- **Time Since Last Run**: Never run")
    report_lines.append(f"- **Next Run At**: {time.ctime(next_run_at/1000) if next_run_at else 'None'}")
    report_lines.append("")

# Summary of issues
report_lines.append("# Issue Summary")
if not issues:
    report_lines.append("No issues detected. All jobs appear healthy.")
else:
    report_lines.append(f"Found {len(issues)} jobs with issues:")
    for issue in issues:
        report_lines.append(f"### {issue['name']} (ID: {issue['id']})")
        for problem in issue['issues']:
            report_lines.append(f"- {problem}")
        report_lines.append("")

# Recommended actions
report_lines.append("# Recommended Actions")
if not issues:
    report_lines.append("No actions required. System is healthy.")
else:
    report_lines.append("1. Review the issues listed above for each job.")
    report_lines.append("2. For disabled jobs: Determine if they should be re-enabled.")
    report_lines.append("3. For jobs with high consecutive errors: Investigate the cause and consider manual trigger to test.")
    report_lines.append("4. For jobs not running in over 2x interval: Check schedule and system time.")
    report_lines.append("5. For jobs with extremely long run times: Optimize the job or increase timeout.")
    report_lines.append("")
    # Specific action for the Daily Tool Check job if it has errors
    daily_tool_check_id = "7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d"
    daily_tool_check_issue = next((issue for issue in issues if issue['id'] == daily_tool_check_id), None)
    if daily_tool_check_issue and any("consecutive errors" in issue.lower() for issue in daily_tool_check_issue['issues']):
        report_lines.append("6. **SLASHAI DAILY TOOL CHECK JOB**: This job has consecutive errors. Consider manually triggering it to test if the underlying issue is resolved.")
    else:
        report_lines.append("6. SlashAI Daily Tool Check job (id: 7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d) has no consecutive errors - no manual trigger needed.")

# Write the report
report_dir = '/home/rpi/.openclaw/workspace/projects/slashai'
os.makedirs(report_dir, exist_ok=True)
report_file = os.path.join(report_dir, 'cron-health-report.md')
with open(report_file, 'w') as f:
    f.write('\n'.join(report_lines))

print(f"Health report written to {report_file}")

# Also log completion to system logs
log_dir = '/home/rpi/.openclaw/workspace/logs'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'cron-health.log')
with open(log_file, 'a') as f:
    f.write(f"{time.ctime()}: Cron health check completed. Report saved to {report_file}. Issues found: {len(issues)}\n")

print(f"Completion logged to {log_file}")
