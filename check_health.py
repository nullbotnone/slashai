import json
import time
import math

# Current time in milliseconds from node
current_time_ms = 1781111215588

# Mapping from cron expression to interval in milliseconds
cron_intervals = {
    "0 */6 * * *": 6 * 60 * 60 * 1000,  # 6 hours
    "0 8 * * *": 24 * 60 * 60 * 1000,   # 1 day
    "0 10 * * *": 24 * 60 * 60 * 1000,  # 1 day
    "0 10 * * 1": 7 * 24 * 60 * 60 * 1000,  # 1 week
    "0 10 */14 * *": 14 * 24 * 60 * 60 * 1000,  # 14 days
    "0 10 1 * *": 30 * 24 * 60 * 60 * 1000,    # approximate 1 month
}

# Load the cron jobs data
with open('/home/rpi/.openclaw/workspace/projects/slashai/cron_jobs_current.json', 'r') as f:
    data = json.load(f)

jobs = data['jobs']

# Prepare report lines
report_lines = []
report_lines.append("# SlashAI Cron Health Report")
report_lines.append(f"Generated at: {time.ctime(current_time_ms / 1000.0)}")
report_lines.append("")

# Overall counters
total_jobs = len(jobs)
enabled_jobs = sum(1 for j in jobs if j.get('enabled', False))
disabled_jobs = total_jobs - enabled_jobs
jobs_with_errors = sum(1 for j in jobs if j.get('state', {}).get('consecutiveErrors', 0) > 0)
jobs_with_consecutive_errors_gt2 = sum(1 for j in jobs if j.get('state', {}).get('consecutiveErrors', 0) > 2)
# For long run times: > 1 hour (3600000 ms)
jobs_with_long_runtime = sum(1 for j in jobs if j.get('state', {}).get('lastDurationMs', 0) > 3600000)
# For overdue jobs: we'll compute per job
overdue_jobs = []

report_lines.append(f"## Summary")
report_lines.append(f"- Total jobs: {total_jobs}")
report_lines.append(f"- Enabled jobs: {enabled_jobs}")
report_lines.append(f"- Disabled jobs: {disabled_jobs}")
report_lines.append(f"- Jobs with any errors: {jobs_with_errors}")
report_lines.append(f"- Jobs with consecutive errors > 2: {jobs_with_consecutive_errors_gt2}")
report_lines.append(f"- Jobs with last run > 1 hour: {jobs_with_long_runtime}")
report_lines.append("")

# Detailed job analysis
report_lines.append("## Job Details")
for job in jobs:
    job_id = job.get('id', 'unknown')
    name = job.get('name', 'Unnamed')
    enabled = job.get('enabled', False)
    state = job.get('state', {})
    last_run_status = state.get('lastRunStatus', 'unknown')
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_duration_ms = state.get('lastDurationMs', 0)
    last_run_at_ms = state.get('lastRunAtMs', 0)
    schedule = job.get('schedule', {})
    cron_expr = schedule.get('expr', '') if schedule else ''
    
    # Compute time since last run
    time_since_last_run_ms = current_time_ms - last_run_at_ms if last_run_at_ms > 0 else None
    
    # Determine if overdue (more than 2x interval)
    overdue = False
    if cron_expr in cron_intervals and last_run_at_ms > 0:
        interval_ms = cron_intervals[cron_expr]
        if time_since_last_run_ms > 2 * interval_ms:
            overdue = True
            overdue_jobs.append(job_id)
    
    # Build job report
    report_lines.append(f"### {name} (`{job_id}`)")
    report_lines.append(f"- Enabled: {enabled}")
    report_lines.append(f"- Last run status: {last_run_status}")
    report_lines.append(f"- Consecutive errors: {consecutive_errors}")
    report_lines.append(f"- Last run duration: {last_duration_ms} ms ({last_duration_ms / 1000:.2f} seconds)")
    if time_since_last_run_ms is not None:
        hours_since = time_since_last_run_ms / (1000 * 60 * 60)
        report_lines.append(f"- Time since last run: {time_since_last_run_ms} ms ({hours_since:.2f} hours)")
    else:
        report_lines.append(f"- Time since last run: never run")
    report_lines.append(f"- Schedule: {cron_expr}")
    report_lines.append(f"- Overdue (>2x interval): {overdue}")
    report_lines.append("")

# Issues needing attention
report_lines.append("## Issues Needing Attention")
issues = []

# Disabled jobs
disabled_list = [j['name'] for j in jobs if not j.get('enabled', False)]
if disabled_list:
    issues.append(f"**Disabled jobs**: {', '.join(disabled_list)}")

# Jobs with consecutive errors > 2
consecutive_errors_list = [j['name'] for j in jobs if j.get('state', {}).get('consecutiveErrors', 0) > 2]
if consecutive_errors_list:
    issues.append(f"**Jobs with consecutive errors > 2**: {', '.join(consecutive_errors_list)}")

# Overdue jobs
overdue_list = [j['name'] for j in jobs if j['id'] in overdue_jobs]
if overdue_list:
    issues.append(f"**Overdue jobs (haven't run in >2x interval)**: {', '.join(overdue_list)}")

# Jobs with long run times (>1 hour)
long_runtime_list = [j['name'] for j in jobs if j.get('state', {}).get('lastDurationMs', 0) > 3600000]
if long_runtime_list:
    issues.append(f"**Jobs with last run > 1 hour**: {', '.join(long_runtime_list)}")

if issues:
    for issue in issues:
        report_lines.append(f"- {issue}")
else:
    report_lines.append("No issues found.")

# Recommended actions
report_lines.append("")
report_lines.append("## Recommended Actions")
if disabled_list:
    report_lines.append("1. Investigate why jobs are disabled and re-enable if appropriate.")
if consecutive_errors_list:
    report_lines.append("2. Check the logs for jobs with repeated errors and fix underlying issues.")
if overdue_list:
    report_lines.append("3. Investigate why overdue jobs are not running as scheduled.")
if long_runtime_list:
    report_lines.append("4. Review jobs with long run times for optimization or timeout issues.")
if not (disabled_list or consecutive_errors_list or overdue_list or long_runtime_list):
    report_lines.append("No actions required. All jobs are healthy.")

# Special check for SlashAI Daily Tool Check job
daily_tool_job_id = "7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d"
daily_tool_job = None
for job in jobs:
    if job.get('id') == daily_tool_job_id:
        daily_tool_job = job
        break

if daily_tool_job:
    consecutive_errors = daily_tool_job.get('state', {}).get('consecutiveErrors', 0)
    report_lines.append("")
    report_lines.append("## SlashAI Daily Tool Check (Special Check)")
    report_lines.append(f"- Job ID: {daily_tool_job_id}")
    report_lines.append(f"- Consecutive errors: {consecutive_errors}")
    if consecutive_errors > 0:
        report_lines.append("**Note**: This job has consecutive errors. As per instructions, we would manually trigger it to test if the underlying issue is resolved.")
        # We don't actually trigger it in this script, but we note that action is needed.
        report_lines.append("- Recommended action: Manually trigger this job to see if the issue is resolved.")
    else:
        report_lines.append("No consecutive errors. Job is healthy.")
else:
    report_lines.append("")
    report_lines.append("## SlashAI Daily Tool Check (Special Check)")
    report_lines.append("Job not found!")

# Write the report to file
report_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md'
with open(report_path, 'w') as f:
    f.write('\n'.join(report_lines))

print(f"Health report written to {report_path}")
