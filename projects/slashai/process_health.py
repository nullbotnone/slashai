#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime, timezone

# Change to the slashai directory
os.chdir('/home/rpi/.openclaw/workspace/projects/slashai')

# Load the cron jobs data
with open('cron_jobs_current.json', 'r') as f:
    data = json.load(f)

jobs = data['jobs']

# Current time in milliseconds (we'll get from the environment or we can pass as argument)
# We'll get the current time from the system
current_time_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

# For each job, compute health
report_lines = []
report_lines.append("# SlashAI Cron Health Report")
report_lines.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
report_lines.append("")
report_lines.append("## Summary")
report_lines.append("")

# Counters for summary
total_jobs = len(jobs)
enabled_jobs = sum(1 for j in jobs if j['enabled'])
disabled_jobs = total_jobs - enabled_jobs
jobs_with_errors = sum(1 for j in jobs if j['state']['consecutiveErrors'] > 0)
jobs_with_consecutive_errors_gt_2 = sum(1 for j in jobs if j['state']['consecutiveErrors'] > 2)
jobs_with_long_runtime = sum(1 for j in jobs if j['state']['lastDurationMs'] > 3600000)  # > 1 hour
jobs_missed_schedule = 0

# We'll collect issues per job
issues_by_job = {}

for job in jobs:
    job_id = job['id']
    job_name = job['name']
    enabled = job['enabled']
    last_run_status = job['state'].get('lastRunStatus', job['state'].get('lastStatus', 'unknown'))
    consecutive_errors = job['state']['consecutiveErrors']
    last_duration_ms = job['state']['lastDurationMs']
    last_run_at_ms = job['state']['lastRunAtMs']
    next_run_at_ms = job['state']['nextRunAtMs']
    
    # Compute time since last run and interval
    time_since_last_run_ms = current_time_ms - last_run_at_ms
    interval_ms = next_run_at_ms - last_run_at_ms  # expected interval between runs
    
    # Check if the job has missed more than 2x its interval
    missed_schedule = time_since_last_run_ms > 2 * interval_ms
    if missed_schedule:
        jobs_missed_schedule += 1
    
    # Collect issues for this job
    issues = []
    if not enabled:
        issues.append("Job is disabled")
    if consecutive_errors > 2:
        issues.append(f"Consecutive errors > 2 ({consecutive_errors})")
    if missed_schedule:
        issues.append(f"Hasn't run in over 2x scheduled interval (last run: {datetime.fromtimestamp(last_run_at_ms/1000).strftime('%Y-%m-%d %H:%M:%S')}, interval: {interval_ms/1000/60:.1f} minutes)")
    if last_duration_ms > 3600000:
        issues.append(f"Extremely long run time (>1 hour): {last_duration_ms/1000/60:.1f} minutes")
    
    if issues:
        issues_by_job[job_id] = {
            'name': job_name,
            'issues': issues,
            'enabled': enabled,
            'last_run_status': last_run_status,
            'consecutive_errors': consecutive_errors,
            'last_duration_ms': last_duration_ms,
            'last_run_at_ms': last_run_at_ms,
            'interval_ms': interval_ms,
            'time_since_last_run_ms': time_since_last_run_ms
        }

# Summary
report_lines.append(f"- Total jobs: {total_jobs}")
report_lines.append(f"- Enabled jobs: {enabled_jobs}")
report_lines.append(f"- Disabled jobs: {disabled_jobs}")
report_lines.append(f"- Jobs with any errors: {jobs_with_errors}")
report_lines.append(f"- Jobs with consecutive errors > 2: {jobs_with_consecutive_errors_gt_2}")
report_lines.append(f"- Jobs with extremely long run times (>1 hour): {jobs_with_long_runtime}")
report_lines.append(f"- Jobs that haven't run in over 2x their scheduled interval: {jobs_missed_schedule}")
report_lines.append("")
report_lines.append("## Overall System Health")
if jobs_with_consecutive_errors_gt_2 == 0 and jobs_with_long_runtime == 0 and jobs_missed_schedule == 0 and disabled_jobs == 0:
    report_lines.append("✅ All systems healthy")
else:
    report_lines.append("⚠️ Issues detected")
report_lines.append("")
report_lines.append("## Detailed Job Status")

for job in jobs:
    job_id = job['id']
    job_name = job['name']
    enabled = job['enabled']
    last_run_status = job['state'].get('lastRunStatus', job['state'].get('lastStatus', 'unknown'))
    consecutive_errors = job['state']['consecutiveErrors']
    last_duration_ms = job['state']['lastDurationMs']
    last_run_at_ms = job['state']['lastRunAtMs']
    next_run_at_ms = job['state']['nextRunAtMs']
    
    time_since_last_run_ms = current_time_ms - last_run_at_ms
    interval_ms = next_run_at_ms - last_run_at_ms
    
    status_emoji = "✅" if last_run_status == "ok" else "❌"
    enabled_emoji = "🟢" if enabled else "🔴"
    
    report_lines.append(f"### {job_name} (`{job_id}`)")
    report_lines.append(f"- Status: {enabled_emoji} {'Enabled' if enabled else 'Disabled'} | Last Run: {status_emoji} {last_run_status}")
    report_lines.append(f"- Consecutive Errors: {consecutive_errors}")
    report_lines.append(f"- Last Run Duration: {last_duration_ms/1000:.1f} seconds ({last_duration_ms/1000/60:.1f} minutes)")
    report_lines.append(f"- Last Run At: {datetime.fromtimestamp(last_run_at_ms/1000).strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"- Time Since Last Run: {time_since_last_run_ms/1000:.1f} seconds ({time_since_last_run_ms/1000/60:.1f} minutes)")
    report_lines.append(f"- Expected Interval: {interval_ms/1000/60:.1f} minutes")
    report_lines.append("")
    
    if job_id in issues_by_job:
        report_lines.append("**Issues:**")
        for issue in issues_by_job[job_id]['issues']:
            report_lines.append(f"- {issue}")
        report_lines.append("")

# If there are issues, list them
if issues_by_job:
    report_lines.append("## Issues Requiring Attention")
    for job_id, info in issues_by_job.items():
        report_lines.append(f"### {info['name']} (`{job_id}`)")
        for issue in info['issues']:
            report_lines.append(f"- {issue}")
        report_lines.append("")
else:
    report_lines.append("## Issues Requiring Attention")
    report_lines.append("No issues found.")
    report_lines.append("")

# Check if the Daily Tool Check job has consecutive errors and trigger if needed
daily_tool_check_id = "7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d"
daily_tool_check_job = None
for job in jobs:
    if job['id'] == daily_tool_check_id:
        daily_tool_check_job = job
        break

if daily_tool_check_job:
    consecutive_errors = daily_tool_check_job['state']['consecutiveErrors']
    if consecutive_errors > 0:
        report_lines.append("## Daily Tool Check Job Trigger")
        report_lines.append(f"The SlashAI Daily Tool Check job (id: {daily_tool_check_id}) has {consecutive_errors} consecutive error(s).")
        report_lines.append("Attempting to manually trigger the job to test if the underlying issue is resolved...")
        report_lines.append("")
        # We'll attempt to trigger the job by running a script if we find one
        # Let's look for a script that might perform the daily tool check
        # We'll search for files containing "Daily Tool Check" or "tools.json" in the slashai directory
        # We'll do this in the script by running a shell command
        import subprocess
        try:
            # Search for scripts that might be related
            result = subprocess.run(['grep', '-r', 'Daily Tool Check', '.', '--include=*.py', '--include=*.sh'], capture_output=True, text=True, timeout=10)
            if result.stdout:
                report_lines.append("Found related scripts:")
                for line in result.stdout.split('\\n'):
                    if line.strip():
                        report_lines.append(f"- {line}")
            else:
                report_lines.append("No specific scripts found for Daily Tool Check via grep.")
        except Exception as e:
            report_lines.append(f"Error searching for scripts: {e}")
        
        # We can also try to run the perform_health_check_now.py or similar? But that's for health check.
        # Instead, we can try to run the job by executing the agent turn? We don't have that capability.
        # We'll just note that we cannot automatically trigger the job without knowing the exact mechanism.
        report_lines.append("")
        report_lines.append("Note: Automatic triggering of the job is not implemented in this health check script. Manual intervention may be required.")
    else:
        report_lines.append("")
        report_lines.append("## Daily Tool Check Job")
        report_lines.append(f"The SlashAI Daily Tool Check job (id: {daily_tool_check_id}) has no consecutive errors. No action needed.")
else:
    report_lines.append("")
    report_lines.append("## Daily Tool Check Job")
    report_lines.append(f"Warning: SlashAI Daily Tool Check job (id: {daily_tool_check_id}) not found.")

# Write the report to the specified file
report_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md'
with open(report_path, 'w') as f:
    f.write('\\n'.join(report_lines))

print(f"Health report written to {report_path}")

# Also log completion to system logs (we'll write to a log file in the logs directory)
log_dir = '/home/rpi/.openclaw/workspace/projects/slashai/logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file = os.path.join(log_dir, 'cron_health_check.log')
with open(log_file, 'a') as f:
    f.write(f"{datetime.now().isoformat()} - Cron health check completed. Report written to {report_path}\\n")

print("Completion logged to system logs.")