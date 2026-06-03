#!/usr/bin/env python3
import json
import datetime
import os

# Load the cron jobs data
json_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron_jobs_current.json'
with open(json_path, 'r') as f:
    data = json.load(f)

jobs = data['jobs']

# Current time in milliseconds (we got from earlier, but we can compute again)
# We'll compute current time to be sure
import time
current_time_ms = int(time.time() * 1000)

# Define thresholds
MAX_CONSECUTIVE_ERRORS = 2
MAX_DURATION_MS = 3600000  # 1 hour

# Prepare report lines
report_lines = []
report_lines.append("# SlashAI Cron Health Report")
report_lines.append(f"**Generated at**: {datetime.datetime.now().isoformat()}")
report_lines.append(f"**Current time (ms since epoch)**: {current_time_ms}")
report_lines.append("")

# Overall stats
total_jobs = len(jobs)
enabled_jobs = sum(1 for j in jobs if j['enabled'])
disabled_jobs = total_jobs - enabled_jobs

report_lines.append("## Summary")
report_lines.append(f"- Total jobs: {total_jobs}")
report_lines.append(f"- Enabled jobs: {enabled_jobs}")
report_lines.append(f"- Disabled jobs: {disabled_jobs}")
report_lines.append("")

# Analyze each job
issues = []
healthy_jobs = 0

for job in jobs:
    job_id = job['id']
    name = job['name']
    enabled = job['enabled']
    state = job['state']
    
    # Extract state fields with defaults
    last_run_at_ms = state.get('lastRunAtMs', 0)
    last_run_status = state.get('lastRunStatus', 'unknown')
    last_status = state.get('lastStatus', 'unknown')
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_duration_ms = state.get('lastDurationMs', 0)
    next_run_at_ms = state.get('nextRunAtMs', 0)
    
    # Compute time since last run
    time_since_last_run_ms = current_time_ms - last_run_at_ms if last_run_at_ms > 0 else float('inf')
    
    # Compute interval from last run to next run (if available)
    interval_ms = None
    if last_run_at_ms > 0 and next_run_at_ms > 0 and next_run_at_ms > last_run_at_ms:
        interval_ms = next_run_at_ms - last_run_at_ms
    
    # Check for issues
    job_issues = []
    
    if not enabled:
        job_issues.append("Job is disabled")
    
    if last_run_status != 'ok' and last_status != 'ok':
        job_issues.append(f"Last run status: {last_run_status}")
    
    if consecutive_errors > MAX_CONSECUTIVE_ERRORS:
        job_issues.append(f"Consecutive errors: {consecutive_errors} (>{MAX_CONSECUTIVE_ERRORS})")
    
    if interval_ms is not None:
        if time_since_last_run_ms > 2 * interval_ms:
            job_issues.append(f"Hasn't run in over 2x interval (last run: {time_since_last_run_ms}ms ago, interval: {interval_ms}ms)")
    else:
        # If we can't compute interval, we can't check this condition
        pass
    
    if last_duration_ms > MAX_DURATION_MS:
        job_issues.append(f"Last run duration: {last_duration_ms}ms (>{MAX_DURATION_MS}ms)")
    
    if job_issues:
        issues.append((job_id, name, job_issues))
    else:
        healthy_jobs += 1
    
    # Job details for report
    report_lines.append(f"### {name} (ID: {job_id})")
    report_lines.append(f"- **Enabled**: {enabled}")
    report_lines.append(f"- **Last run status**: {last_run_status}")
    report_lines.append(f"- **Last status**: {last_status}")
    report_lines.append(f"- **Consecutive errors**: {consecutive_errors}")
    report_lines.append(f"- **Last run duration**: {last_duration_ms} ms ({last_duration_ms/1000:.2f} seconds)")
    report_lines.append(f"- **Last run at**: {datetime.datetime.fromtimestamp(last_run_at_ms/1000).isoformat() if last_run_at_ms > 0 else 'Never'}")
    report_lines.append(f"- **Time since last run**: {time_since_last_run_ms} ms ({time_since_last_run_ms/1000:.2f} seconds)")
    if interval_ms is not None:
        report_lines.append(f"- **Interval (last to next)**: {interval_ms} ms ({interval_ms/1000:.2f} seconds)")
        report_lines.append(f"- **Next run at**: {datetime.datetime.fromtimestamp(next_run_at_ms/1000).isoformat() if next_run_at_ms > 0 else 'N/A'}")
    else:
        report_lines.append(f"- **Interval**: Could not be computed (invalid next/last run times)")
    report_lines.append("")
    
    if job_issues:
        report_lines.append("**Issues:**")
        for issue in job_issues:
            report_lines.append(f"- {issue}")
        report_lines.append("")

report_lines.insert(3, f"- **Healthy jobs**: {healthy_jobs}/{total_jobs} ({healthy_jobs/total_jobs*100:.1f}%)")
report_lines.insert(4, "")

# Issues summary
if issues:
    report_lines.append("## Issues Found")
    for job_id, name, job_issues in issues:
        report_lines.append(f"### {name} (ID: {job_id})")
        for issue in job_issues:
            report_lines.append(f"- {issue}")
        report_lines.append("")
else:
    report_lines.append("## Issues Found")
    report_lines.append("No issues found. All jobs are healthy.")
    report_lines.append("")

# Recommended actions
report_lines.append("## Recommended Actions")
if issues:
    report_lines.append("1. Investigate and fix the issues listed above.")
    report_lines.append("2. For disabled jobs that should be enabled, check why they were disabled and re-enable if appropriate.")
    report_lines.append("3. For jobs with high consecutive errors, check the underlying cause and consider manual intervention.")
    report_lines.append("4. For jobs that haven't run in over 2x their interval, check if the scheduler is working correctly.")
    report_lines.append("5. For jobs with extremely long run times, consider optimizing the job or increasing timeout limits.")
else:
    report_lines.append("No actions required. All cron jobs are operating normally.")

# Check for the specific job: SlashAI Daily Tool Check (id: 7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d)
daily_tool_check_job = None
for job in jobs:
    if job['id'] == '7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d':
        daily_tool_check_job = job
        break

if daily_tool_check_job:
    consecutive_errors = daily_tool_check_job['state']['consecutiveErrors']
    if consecutive_errors > MAX_CONSECUTIVE_ERRORS:
        report_lines.append("")
        report_lines.append("## Special Note: SlashAI Daily Tool Check")
        report_lines.append(f"The SlashAI Daily Tool Check job (ID: 7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d) has {consecutive_errors} consecutive errors, which exceeds the threshold of {MAX_CONSECUTIVE_ERRORS}.")
        report_lines.append("As per instructions, this job should be manually triggered to test if the underlying issue is resolved.")
        report_lines.append("However, automatic triggering is not implemented in this script. Consider manually triggering the job via the OpenClaw interface or by running the associated task.")
    else:
        report_lines.append("")
        report_lines.append("## Special Note: SlashAI Daily Tool Check")
        report_lines.append(f"The SlashAI Daily Tool Check job (ID: 7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d) has {consecutive_errors} consecutive errors, which is within acceptable limits (<={MAX_CONSECUTIVE_ERRORS}). No manual trigger needed.")
else:
    report_lines.append("")
    report_lines.append("## Special Note: SlashAI Daily Tool Check")
    report_lines.append("WARNING: SlashAI Daily Tool Check job (ID: 7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d) not found in cron jobs list.")

# Write the report
report_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md'
with open(report_path, 'w') as f:
    f.write('\n'.join(report_lines))

print(f"Health report written to {report_path}")

# Log completion to system logs
log_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-check.log'
log_message = f"{datetime.datetime.now().isoformat()} - Cron health check completed. Report saved to {report_path}\n"
with open(log_path, 'a') as f:
    f.write(log_message)

print(f"Completion logged to {log_path}")