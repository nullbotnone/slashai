#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone

# Load the cron jobs data from live file (most recent)
jobs_file = '/home/rpi/.openclaw/workspace/projects/slashai/cron_jobs_live.json'
try:
    with open(jobs_file, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    # Fallback to current
    jobs_file = '/home/rpi/.openclaw/workspace/projects/slashai/cron_jobs_current.json'
    with open(jobs_file, 'r') as f:
        data = json.load(f)

jobs = data.get('jobs', [])

# Get current time in milliseconds
dt_utc = datetime.now(timezone.utc)
current_time_ms = int(dt_utc.timestamp() * 1000)

print(f"Current time (ms since epoch): {current_time_ms}")
print(f"Current time (UTC): {dt_utc.isoformat()}")
print(f"Current time (local): {dt_utc.astimezone().isoformat()}")

# Now analyze each job
report_lines = []
report_lines.append("# SlashAI Cron Health Report")
report_lines.append(f"Generated at: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}")
report_lines.append("")
report_lines.append("## Summary")
report_lines.append("")

issues = []
job_details = []

for job in jobs:
    job_id = job['id']
    name = job['name']
    enabled = job.get('enabled', False)
    schedule = job.get('schedule', {})
    expr = schedule.get('expr', 'N/A')
    tz = schedule.get('tz', 'UTC')
    
    state = job.get('state', {})
    last_run_at_ms = state.get('lastRunAtMs')
    last_run_status = state.get('lastRunStatus', 'unknown')
    last_duration_ms = state.get('lastDurationMs', 0)
    consecutive_errors = state.get('consecutiveErrors', 0)
    next_run_at_ms = state.get('nextRunAtMs')
    
    # Calculate time since last run
    if last_run_at_ms:
        time_since_last_run_ms = current_time_ms - last_run_at_ms
        time_since_last_run_str = f"{time_since_last_run_ms // 1000} seconds"
    else:
        time_since_last_run_str = "Never"
    
    # Determine if the job is enabled as expected (we assume it should be enabled unless otherwise)
    # We'll flag if disabled unexpectedly later
    
    # Check for issues
    issue_flags = []
    
    # 1. Jobs disabled unexpectedly
    if not enabled:
        issue_flags.append("Job is disabled")
    
    # 2. Jobs with consecutive errors > 2
    if consecutive_errors > 2:
        issue_flags.append(f"Consecutive errors: {consecutive_errors} (>2)")
    
    # 3. Jobs that haven't run in over 2x their scheduled interval
    # We need to compute the interval from the cron expression
    # For simplicity, we'll skip the exact interval calculation and use the nextRunAtMs and lastRunAtMs
    # If the job has never run, we skip.
    if last_run_at_ms and next_run_at_ms:
        # The expected interval can be approximated as (nextRunAtMs - lastRunAtMs) if the job runs regularly
        expected_interval_ms = next_run_at_ms - last_run_at_ms
        if expected_interval_ms > 0:
            # If the time since last run is greater than 2 * expected_interval_ms, then issue
            if time_since_last_run_ms > 2 * expected_interval_ms:
                issue_flags.append(f"Has not run in over 2x scheduled interval (last run: {time_since_last_run_ms//1000}s ago, expected interval: {expected_interval_ms//1000}s)")
        else:
            # If expected interval is not positive, we skip this check
            pass
    elif not last_run_at_ms:
        # Never run, we can consider it as not run in over 2x interval? We'll flag if it's been a long time since created?
        # We'll skip for now
        pass
    
    # 4. Jobs with extremely long run times (> 1 hour)
    if last_duration_ms > 3600000:  # 1 hour in milliseconds
        issue_flags.append(f"Last run duration: {last_duration_ms // 1000} seconds (>1 hour)")
    
    if issue_flags:
        issues.append({
            'job_id': job_id,
            'name': name,
            'issues': issue_flags
        })
    
    # Collect details for reporting
    job_details.append({
        'id': job_id,
        'name': name,
        'enabled': enabled,
        'schedule': f"{expr} ({tz})",
        'last_run_status': last_run_status,
        'last_run_time': datetime.fromtimestamp(last_run_at_ms/1000, tz=timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S %Z') if last_run_at_ms else 'Never',
        'last_run_duration_sec': last_duration_ms // 1000 if last_duration_ms else 0,
        'consecutive_errors': consecutive_errors,
        'time_since_last_run': time_since_last_run_str,
        'next_run_at': datetime.fromtimestamp(next_run_at_ms/1000, tz=timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S %Z') if next_run_at_ms else 'N/A'
    })

# Write the report
report_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md'
with open(report_path, 'w') as f:
    f.write('\n'.join(report_lines))
    f.write("\n")
    
    # Overall system health
    if not issues:
        f.write("**Overall System Health: GOOD** - No issues detected.\n\n")
    else:
        f.write(f"**Overall System Health: ISSUES DETECTED** - Found {len(issues)} problematic job(s).\n\n")
    
    # Details of each job
    f.write("## Job Details\n\n")
    f.write("| Job ID | Name | Enabled | Schedule | Last Run Status | Last Run Time | Duration (s) | Consecutive Errors | Time Since Last Run | Next Run At |\n")
    f.write("|--------|------|---------|----------|-----------------|---------------|--------------|--------------------|---------------------|-------------|\n")
    for jd in job_details:
        f.write(f"| `{jd['id']}` | {jd['name']} | {jd['enabled']} | {jd['schedule']} | {jd['last_run_status']} | {jd['last_run_time']} | {jd['last_run_duration_sec']} | {jd['consecutive_errors']} | {jd['time_since_last_run']} | {jd['next_run_at']} |\n")
    
    f.write("\n")
    
    # Issues found
    if issues:
        f.write("## Issues Found\n\n")
        for issue in issues:
            f.write(f"### Job: {issue['name']} (`{issue['job_id']}`)\n")
            for flag in issue['issues']:
                f.write(f"- {flag}\n")
            f.write("\n")
        
        f.write("## Recommended Actions\n\n")
        f.write("1. For disabled jobs: Investigate why they were disabled and re-enable if appropriate.\n")
        f.write("2. For jobs with consecutive errors > 2: Check the job logs to understand the error and fix the underlying issue.\n")
        f.write("3. For jobs that haven't run in over 2x their scheduled interval: Check if the job is stuck or if the scheduling is incorrect.\n")
        f.write("4. For jobs with extremely long run times: Investigate why the job is taking so long and optimize if possible.\n")
    else:
        f.write("## Recommended Actions\n\n")
        f.write("No issues detected. Continue regular monitoring.\n")

print(f"Report written to {report_path}")

# Now check the SlashAI Daily Tool Check job for consecutive errors
daily_tool_check_id = "7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d"
daily_tool_check_job = None
for job in jobs:
    if job['id'] == daily_tool_check_id:
        daily_tool_check_job = job
        break

if daily_tool_check_job:
    consecutive_errors = daily_tool_check_job.get('state', {}).get('consecutiveErrors', 0)
    print(f"SlashAI Daily Tool Check job consecutive errors: {consecutive_errors}")
    if consecutive_errors > 0:
        print("Consecutive errors detected. Manually triggering the job...")
        # We will trigger the job by sending a message to the main session? 
        # Since we are in the main session, we can just execute the task described in the job's payload.
        # However, we don't have the payload message here. We can extract it from the job.
        payload = daily_tool_check_job.get('payload', {})
        message = payload.get('message', '')
        if message:
            print(f"Triggering with message: {message[:100]}...")
            # We can use the sessions_send tool to send a message to the main session? 
            # But note: the job is set to run in an isolated session. We can try to spawn a subagent with the task.
            # However, for simplicity, we can just run the command that the job would run.
            # Since we don't know the command, we will skip the actual triggering and just log that we would trigger it.
            # But the instruction requires us to manually trigger it.
            # We can try to use the sessions_spawn tool to run the task.
            # We'll do that after generating the report.
            # For now, we'll set a flag to trigger later.
            trigger_needed = True
            trigger_message = message
        else:
            print("No message found in payload. Cannot trigger.")
            trigger_needed = False
    else:
        print("No consecutive errors. No need to trigger.")
        trigger_needed = False
else:
    print("SlashAI Daily Tool Check job not found.")
    trigger_needed = False

# We'll output the trigger_needed and trigger_message to a file so we can act on it later.
with open('/home/rpi/.openclaw/workspace/tmp/trigger_info.json', 'w') as f:
    json.dump({
        'trigger_needed': trigger_needed,
        'trigger_message': trigger_message if trigger_needed else None,
        'job_id': daily_tool_check_id
    }, f)
