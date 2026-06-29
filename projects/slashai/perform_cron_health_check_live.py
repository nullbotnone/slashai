#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone

# Load the cron jobs data from live file
json_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron_jobs_live.json'
with open(json_path, 'r') as f:
    data = json.load(f)

jobs = data.get('jobs', [])

# Current time in milliseconds since epoch
now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

# For logging
log_path = '/home/rpi/.openclaw/workspace/system.log'

def log_message(msg):
    with open(log_path, 'a') as f:
        f.write(f'{datetime.now().isoformat()} {msg}\n')
    print(msg)

# Analyze each job
issues = []
for job in jobs:
    job_id = job.get('id')
    name = job.get('name')
    enabled = job.get('enabled', False)
    state = job.get('state', {})
    last_run_status = state.get('lastRunStatus', 'unknown')
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_duration_ms = state.get('lastDurationMs', 0)
    last_run_at_ms = state.get('lastRunAtMs', 0)
    next_run_at_ms = state.get('nextRunAtMs', 0)
    
    # Time since last run
    if last_run_at_ms > 0:
        time_since_last_run_ms = now_ms - last_run_at_ms
        time_since_last_run_hours = time_since_last_run_ms / (1000 * 60 * 60)
    else:
        time_since_last_run_ms = None
        time_since_last_run_hours = None
    
    # Expected interval from schedule (approx)
    if next_run_at_ms > 0 and last_run_at_ms > 0:
        expected_interval_ms = next_run_at_ms - last_run_at_ms
        expected_interval_hours = expected_interval_ms / (1000 * 60 * 60)
    else:
        expected_interval_ms = None
        expected_interval_hours = None
    
    # Check for issues
    if not enabled:
        issues.append({
            'job': name,
            'issue': 'Job is disabled',
            'details': f'Enabled: {enabled}'
        })
    
    if consecutive_errors > 2:
        issues.append({
            'job': name,
            'issue': f'High consecutive errors: {consecutive_errors}',
            'details': f'Consecutive errors: {consecutive_errors}'
        })
    
    if expected_interval_ms is not None and time_since_last_run_ms is not None:
        if time_since_last_run_ms > 2 * expected_interval_ms:
            issues.append({
                'job': name,
                'issue': f'Has not run in over 2x scheduled interval',
                'details': f'Time since last run: {time_since_last_run_hours:.2f} hours, expected interval: {expected_interval_hours:.2f} hours'
            })
    
    if last_duration_ms > 3600000:  # 1 hour in ms
        issues.append({
            'job': name,
            'issue': f'Extremely long run time: {last_duration_ms / (1000*60):.2f} minutes',
            'details': f'Last duration: {last_duration_ms} ms ({last_duration_ms / (1000*60):.2f} minutes)'
        })

# Overall health: if no issues, healthy
overall_healthy = len(issues) == 0

# Prepare report
report_lines = []
report_lines.append('# SlashAI Cron Health Report')
report_lines.append(f'**Generated at:** {datetime.now(timezone.utc).isoformat()}')
report_lines.append(f'**Current time (America/Chicago):** {datetime.now().astimezone().isoformat()}')
report_lines.append('')
report_lines.append('## Overall System Health')
if overall_healthy:
    report_lines.append('✅ **Healthy** - No issues detected.')
else:
    report_lines.append('⚠️ **Issues Detected** - See details below.')
report_lines.append('')
report_lines.append('## Job Details')
for job in jobs:
    job_id = job.get('id')
    name = job.get('name')
    enabled = job.get('enabled', False)
    state = job.get('state', {})
    last_run_status = state.get('lastRunStatus', 'unknown')
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_duration_ms = state.get('lastDurationMs', 0)
    last_run_at_ms = state.get('lastRunAtMs', 0)
    next_run_at_ms = state.get('nextRunAtMs', 0)
    
    # Format times
    def format_ts(ts):
        if ts == 0:
            return 'Never'
        dt = datetime.fromtimestamp(ts/1000, tz=timezone.utc)
        return dt.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
    
    last_run_str = format_ts(last_run_at_ms)
    next_run_str = format_ts(next_run_at_ms)
    
    report_lines.append(f'### {name} (`{job_id}`)')
    report_lines.append(f'- **Enabled:** {enabled}')
    report_lines.append(f'- **Last Run Status:** {last_run_status}')
    report_lines.append(f'- **Consecutive Errors:** {consecutive_errors}')
    report_lines.append(f'- **Last Run Duration:** {last_duration_ms} ms ({last_duration_ms/1000:.2f} s)')
    report_lines.append(f'- **Last Run At:** {last_run_str}')
    report_lines.append(f'- **Next Run At:** {next_run_str}')
    if last_run_at_ms > 0 and next_run_at_ms > 0:
        interval_ms = next_run_at_ms - last_run_at_ms
        report_lines.append(f'- **Scheduled Interval:** {interval_ms/3600000:.2f} hours')
    report_lines.append('')

report_lines.append('## Issues Needing Attention')
if issues:
    for issue in issues:
        report_lines.append(f'- **{issue["job"]}:** {issue["issue"]}')
        report_lines.append(f'  - Details: {issue["details"]}')
else:
    report_lines.append('None')

report_lines.append('')
report_lines.append('## Recommended Actions')
if issues:
    report_lines.append('1. Investigate disabled jobs and re-enable if appropriate.')
    report_lines.append('2. For jobs with high consecutive errors, check the underlying cause and consider manual trigger to test.')
    report_lines.append('3. For jobs not running on schedule, check if the agent is operational and if there are any blockers.')
    report_lines.append('4. For jobs with long run times, consider optimizing or increasing timeout limits.')
else:
    report_lines.append('No actions required. System is healthy.')

# Special check for SlashAI Daily Tool Check job
daily_tool_job = None
for job in jobs:
    if job.get('id') == '7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d':
        daily_tool_job = job
        break

if daily_tool_job:
    consecutive_errors = daily_tool_job.get('state', {}).get('consecutiveErrors', 0)
    last_run_status = daily_tool_job.get('state', {}).get('lastRunStatus', 'unknown')
    if consecutive_errors > 0:
        report_lines.append('')
        report_lines.append('## SlashAI Daily Tool Check Manual Trigger')
        report_lines.append(f'The SlashAI Daily Tool Check job has {consecutive_errors} consecutive errors (last status: {last_run_status}). According to the health check procedure, we should manually trigger it to test if the underlying issue is resolved.')
        report_lines.append('**Note:** Manual trigger not performed in this automated script; you may need to trigger it via the OpenClaw interface.')
        report_lines.append(f'Last error: {daily_tool_job.get("state", {}).get("lastError", "Unknown")}')
    else:
        report_lines.append('')
        report_lines.append('## SlashAI Daily Tool Check')
        report_lines.append('The SlashAI Daily Tool Check job has no consecutive errors. No manual trigger needed.')

# Write report
report_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md'
with open(report_path, 'w') as f:
    f.write('\n'.join(report_lines))

log_message(f'Cron health check completed. Report saved to {report_path}')
log_message(f'Overall health: {"Healthy" if overall_healthy else "Issues detected"}')

# Also output to console
print('\\n'.join(report_lines))