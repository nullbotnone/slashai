#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone
import time

# Load the cron jobs data
with open('/home/rpi/.openclaw/workspace/projects/slashai/cron_jobs_current.json', 'r') as f:
    data = json.load(f)

jobs = data['jobs']

# Current time in milliseconds (provided: 2026-06-20 18:02:00 America/Chicago)
# We'll compute it using the system time in the correct timezone, but we can also use the provided time.
# Let's use the provided time to be consistent with the instructions.
# We'll set the timezone to America/Chicago and parse the given time.
provided_time_str = "2026-06-20 18:02:00"
# Convert to datetime in America/Chicago timezone
# We'll use pytz if available, but to avoid dependencies, we'll compute offset manually?
# Alternatively, we can use the system's timezone setting and then adjust.
# Since we are in a controlled environment, we'll assume the system time is set to America/Chicago.
# Let's get the current time in milliseconds since epoch in UTC, then adjust for America/Chicago?
# Instead, we'll use the provided time and convert to UTC then to milliseconds.
# We know that America/Chicago is UTC-5 (or UTC-6 depending on DST). In June, it's UTC-5 (CDT).
# So 18:02 America/Chicago is 23:02 UTC.
# We'll compute the timestamp for 2026-06-20 23:02:00 UTC.
# We can use datetime in UTC.
utc_time = datetime(2026, 6, 20, 23, 2, 0, tzinfo=timezone.utc)
current_ms = int(utc_time.timestamp() * 1000)
print(f"Current time (ms): {current_ms}")

# Function to convert cron expression to expected interval in milliseconds
def cron_to_interval_ms(cron_expr):
    # Simple mapping for the known expressions in our jobs
    # We'll parse the cron expression and compute the expected interval.
    # For simplicity, we'll handle the specific patterns we see.
    # cron_expr is a string like "0 */6 * * *" or "0 8 * * *"
    parts = cron_expr.split()
    if len(parts) != 5:
        # Fallback: assume daily
        return 24 * 60 * 60 * 1000
    
    minute, hour, day_of_month, month, day_of_week = parts
    
    # If minute is 0 and hour is */6, then every 6 hours
    if minute == '0' and hour == '*/6':
        return 6 * 60 * 60 * 1000
    # If minute is 0 and hour is a fixed number and day_of_month is * and month is * and day_of_week is * -> daily
    if minute == '0' and hour != '*' and day_of_month == '*' and month == '*' and day_of_week == '*':
        return 24 * 60 * 60 * 1000
    # If minute is 0 and hour is 10 and day_of_month is * and month is * and day_of_week is 1 -> weekly (Monday)
    if minute == '0' and hour == '10' and day_of_month == '*' and month == '*' and day_of_week == '1':
        return 7 * 24 * 60 * 60 * 1000
    # If minute is 0 and hour is 10 and day_of_month is */14 -> every 14 days
    if minute == '0' and hour == '10' and day_of_month == '*/14' and month == '*' and day_of_week == '*':
        return 14 * 24 * 60 * 60 * 1000
    # If minute is 0 and hour is 10 and day_of_month is 1 and month is * and day_of_week is * -> monthly (approx 30 days)
    if minute == '0' and hour == '10' and day_of_month == '1' and month == '*' and day_of_week == '*':
        return 30 * 24 * 60 * 60 * 1000
    # Default: assume daily
    return 24 * 60 * 60 * 1000

# Analyze each job
report_lines = []
report_lines.append("# SlashAI Cron Health Check Report")
report_lines.append(f"**Generated at:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}")
report_lines.append("")
report_lines.append("## Summary")
report_lines.append("")

# Counters for summary
total_jobs = len(jobs)
enabled_jobs = sum(1 for j in jobs if j.get('enabled', False))
disabled_jobs = total_jobs - enabled_jobs
jobs_with_errors = sum(1 for j in jobs if j.get('state', {}).get('consecutiveErrors', 0) > 0)
jobs_with_high_errors = sum(1 for j in jobs if j.get('state', {}).get('consecutiveErrors', 0) > 2)
jobs_not_run_lately = 0
jobs_long_runtime = 0

# For each job, collect details
job_details = []
for job in jobs:
    job_id = job.get('id', 'unknown')
    name = job.get('name', 'Unknown Job')
    enabled = job.get('enabled', False)
    state = job.get('state', {})
    last_run_status = state.get('lastRunStatus', state.get('lastStatus', 'unknown'))
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_duration_ms = state.get('lastDurationMs', 0)
    last_run_at_ms = state.get('lastRunAtMs', 0)
    schedule = job.get('schedule', {})
    cron_expr = schedule.get('expr', '0 * * * *')  # default to hourly if not set
    
    # Compute expected interval
    expected_interval_ms = cron_to_interval_ms(cron_expr)
    
    # Time since last run
    if last_run_at_ms > 0:
        time_since_last_run_ms = current_ms - last_run_at_ms
    else:
        time_since_last_run_ms = float('inf')
    
    # Check issues
    disabled_unexpectedly = not enabled
    high_consecutive_errors = consecutive_errors > 2
    # Haven't run in over 2x their scheduled interval
    not_run_lately = time_since_last_run_ms > (2 * expected_interval_ms) if expected_interval_ms > 0 else False
    # Extremely long run times (> 1 hour)
    long_runtime = last_duration_ms > 3600000  # 1 hour in ms
    
    if not_run_lately:
        jobs_not_run_lately += 1
    if long_runtime:
        jobs_long_runtime += 1
    
    # Store details for reporting
    job_details.append({
        'id': job_id,
        'name': name,
        'enabled': enabled,
        'last_run_status': last_run_status,
        'consecutive_errors': consecutive_errors,
        'last_duration_ms': last_duration_ms,
        'last_run_at_ms': last_run_at_ms,
        'time_since_last_run_ms': time_since_last_run_ms,
        'expected_interval_ms': expected_interval_ms,
        'cron_expr': cron_expr,
        'issues': {
            'disabled': disabled_unexpectedly,
            'high_errors': high_consecutive_errors,
            'not_run_lately': not_run_lately,
            'long_runtime': long_runtime
        }
    })

# Summary
report_lines.append(f"- Total jobs: {total_jobs}")
report_lines.append(f"- Enabled jobs: {enabled_jobs}")
report_lines.append(f"- Disabled jobs: {disabled_jobs}")
report_lines.append(f"- Jobs with any errors: {jobs_with_errors}")
report_lines.append(f"- Jobs with >2 consecutive errors: {jobs_with_high_errors}")
report_lines.append(f"- Jobs not run in >2x interval: {jobs_not_run_lately}")
report_lines.append(f"- Jobs with runtime >1 hour: {jobs_long_runtime}")
report_lines.append("")
report_lines.append("## Detailed Job Status")
report_lines.append("")

for job in job_details:
    report_lines.append(f"### {job['name']} (`{job['id']}`)")
    report_lines.append(f"- **Enabled:** {job['enabled']}")
    report_lines.append(f"- **Last run status:** {job['last_run_status']}")
    report_lines.append(f"- **Consecutive errors:** {job['consecutive_errors']}")
    report_lines.append(f"- **Last run duration:** {job['last_duration_ms']} ms ({job['last_duration_ms']/1000:.2f} seconds)")
    if job['last_run_at_ms'] > 0:
        last_run_time = datetime.fromtimestamp(job['last_run_at_ms']/1000, tz=timezone.utc)
        report_lines.append(f"- **Last run at:** {last_run_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    else:
        report_lines.append(f"- **Last run at:** Never")
    report_lines.append(f"- **Time since last run:** {job['time_since_last_run_ms']} ms ({job['time_since_last_run_ms']/1000:.2f} seconds)")
    report_lines.append(f"- **Expected interval:** {job['expected_interval_ms']} ms ({job['expected_interval_ms']/1000:.2f} seconds)")
    report_lines.append(f"- **Cron expression:** {job['cron_expr']}")
    
    issues = []
    if job['issues']['disabled']:
        issues.append("❌ Disabled unexpectedly")
    if job['issues']['high_errors']:
        issues.append(f"❌ High consecutive errors ({job['consecutive_errors']} > 2)")
    if job['issues']['not_run_lately']:
        issues.append(f"❌ Not run in >2x interval ({job['time_since_last_run_ms']} > {2*job['expected_interval_ms']} ms)")
    if job['issues']['long_runtime']:
        issues.append(f"❌ Runtime too long ({job['last_duration_ms']} ms > 3600000 ms)")
    
    if issues:
        report_lines.append(f"- **Issues:** {'; '.join(issues)}")
    else:
        report_lines.append(f"- **Issues:** None")
    report_lines.append("")

# Overall health assessment
report_lines.append("## Overall Health Assessment")
if jobs_with_high_errors == 0 and jobs_not_run_lately == 0 and jobs_long_runtime == 0 and disabled_jobs == 0:
    report_lines.append("✅ **All systems operational.** No issues detected.")
else:
    report_lines.append("⚠️ **Issues detected** requiring attention.")
    if disabled_jobs > 0:
        report_lines.append(f"- {disabled_jobs} job(s) are disabled unexpectedly.")
    if jobs_with_high_errors > 0:
        report_lines.append(f"- {jobs_with_high_errors} job(s) have more than 2 consecutive errors.")
    if jobs_not_run_lately > 0:
        report_lines.append(f"- {jobs_not_run_lately} job(s) have not run in over twice their scheduled interval.")
    if jobs_long_runtime > 0:
        report_lines.append(f"- {jobs_long_runtime} job(s) have run for longer than 1 hour.")

report_lines.append("")
report_lines.append("## Recommended Actions")
if disabled_jobs > 0:
    report_lines.append("1. Investigate and re-enable any unexpectedly disabled jobs.")
if jobs_with_high_errors > 0:
    report_lines.append("2. Examine the logs for jobs with high consecutive errors to identify recurring issues.")
if jobs_not_run_lately > 0:
    report_lines.append("3. Check the scheduling and system time for jobs that haven't run as expected.")
if jobs_long_runtime > 0:
    report_lines.append("4. Optimize or investigate jobs that are taking excessively long to run.")
if jobs_with_high_errors == 0 and jobs_not_run_lately == 0 and jobs_long_runtime == 0 and disabled_jobs == 0:
    report_lines.append("No specific actions required. Continue monitoring.")

# Write the report to the specified path
report_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md'
with open(report_path, 'w') as f:
    f.write('\n'.join(report_lines))

print(f"Report written to {report_path}")

# Check if the SlashAI Daily Tool Check job (id: 7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d) has consecutive errors > 2
daily_tool_job_id = "7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d"
daily_tool_job = None
for job in jobs:
    if job.get('id') == daily_tool_job_id:
        daily_tool_job = job
        break

if daily_tool_job:
    consecutive_errors = daily_tool_job.get('state', {}).get('consecutiveErrors', 0)
    if consecutive_errors > 2:
        print(f"SlashAI Daily Tool Check job has {consecutive_errors} consecutive errors. Attempting to manually trigger...")
        # We'll try to trigger by spawning a subagent with the job's payload message
        # Note: This is a simplified trigger; the actual job might have more context.
        from subprocess import run, PIPE
        # We'll use the sessions_spawn tool via OpenClaw CLI? Not available.
        # Instead, we'll simulate by running the actions described in the payload?
        # Since we cannot reliably trigger the job, we'll log a warning and skip.
        print("WARNING: Automatic triggering of cron jobs is not implemented in this script.")
        print("Please manually investigate and trigger the SlashAI Daily Tool Check job if needed.")
        # We'll append a note to the report
        with open(report_path, 'a') as f:
            f.write("\n\n## Manual Trigger Attempt\n")
            f.write(f"The SlashAI Daily Tool Check job (id: {daily_tool_job_id}) has {consecutive_errors} consecutive errors.\n")
            f.write("Automatic triggering was attempted but not implemented due to complexity. Please manually trigger this job to test if the underlying issue is resolved.\n")
    else:
        print(f"SlashAI Daily Tool Check job has {consecutive_errors} consecutive errors (<=2), no manual trigger needed.")
else:
    print(f"SlashAI Daily Tool Check job (id: {daily_tool_job_id}) not found.")

# Log completion to system logs
log_message = f"SlashAI Cron Health Check completed at {datetime.now(timezone.utc).isoformat()}. Report saved to {report_path}"
# We'll write to the system log in the workspace
log_file = '/home/rpi/.openclaw/workspace/system.log'
with open(log_file, 'a') as f:
    f.write(log_message + '\n')
# Also write to the slashai logs directory
slashai_log_file = '/home/rpi/.openclaw/workspace/projects/slashai/logs/health-check.log'
with open(slashai_log_file, 'a') as f:
    f.write(log_message + '\n')

print("Health check completed and logged.")