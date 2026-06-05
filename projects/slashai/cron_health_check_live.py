#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, timezone

# Load the live cron jobs state
jobs_file = '/home/rpi/.openclaw/cron/jobs.json'
try:
    with open(jobs_file, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: {jobs_file} not found.", file=sys.stderr)
    sys.exit(1)

jobs = data.get('jobs', [])
if not jobs:
    print("No jobs found in the cron jobs file.", file=sys.stderr)
    sys.exit(1)

# Current time in milliseconds since epoch
now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

# Helper to convert cron expression to interval in seconds (approximate)
def cron_to_interval_seconds(cron_expr):
    # Mapping of known cron expressions to intervals in seconds
    # We handle the specific expressions found in the jobs
    if cron_expr == "0 */6 * * *":
        return 6 * 3600  # 6 hours
    elif cron_expr == "0 8 * * *":
        return 24 * 3600  # daily
    elif cron_expr == "0 10 * * *":
        return 24 * 3600  # daily
    elif cron_expr == "0 10 * * 1":
        return 7 * 24 * 3600  # weekly
    elif cron_expr == "0 10 */14 * *":
        return 14 * 24 * 3600  # biweekly
    elif cron_expr == "0 10 1 * *":
        # Monthly: approximate as 30 days
        return 30 * 24 * 3600
    else:
        # Unknown expression, default to 24 hours
        return 24 * 3600

# Analyze each job
report_lines = []
report_lines.append("# SlashAI Cron Health Report")
report_lines.append(f"**Generated at:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
report_lines.append("")

# Overall health counters
total_jobs = len(jobs)
enabled_jobs = sum(1 for j in jobs if j.get('enabled', False))
disabled_jobs = total_jobs - enabled_jobs
jobs_with_errors = sum(1 for j in jobs if j.get('state', {}).get('consecutiveErrors', 0) > 0)
jobs_consecutive_errors_gt2 = sum(1 for j in jobs if j.get('state', {}).get('consecutiveErrors', 0) > 2)
jobs_long_runtime = sum(1 for j in jobs if j.get('state', {}).get('lastDurationMs', 0) > 3600000)  # >1 hour
jobs_not_run_in_2x_interval = 0

for job in jobs:
    state = job.get('state', {})
    last_run_at_ms = state.get('lastRunAtMs')
    if last_run_at_ms is None:
        # Never run? Consider as not run in over 2x interval
        jobs_not_run_in_2x_interval += 1
        continue
    interval_sec = cron_to_interval_seconds(job.get('schedule', {}).get('expr', '0 0 * * *'))
    time_since_last_run_ms = now_ms - last_run_at_ms
    if time_since_last_run_ms > (2 * interval_sec * 1000):
        jobs_not_run_in_2x_interval += 1

# Determine overall health
if disabled_jobs > 0 or jobs_consecutive_errors_gt2 > 0 or jobs_not_run_in_2x_interval > 0 or jobs_long_runtime > 0:
    overall_health = "🔴 **Unhealthy** - Issues detected"
else:
    overall_health = "🟢 **Healthy** - No issues detected"

report_lines.append(f"## Overall System Health: {overall_health}")
report_lines.append("")
report_lines.append("### Summary Statistics")
report_lines.append(f"- Total Jobs: {total_jobs}")
report_lines.append(f"- Enabled Jobs: {enabled_jobs}")
report_lines.append(f"- Disabled Jobs: {disabled_jobs}")
report_lines.append(f"- Jobs with Any Errors: {jobs_with_errors}")
report_lines.append(f"- Jobs with Consecutive Errors > 2: {jobs_consecutive_errors_gt2}")
report_lines.append(f"- Jobs with Last Run > 1 Hour: {jobs_long_runtime}")
report_lines.append(f"- Jobs Not Run in Over 2x Interval: {jobs_not_run_in_2x_interval}")
report_lines.append("")

# Detailed job status
report_lines.append("## Job Details")
for job in jobs:
    job_id = job.get('id', 'unknown')
    name = job.get('name', 'Unknown')
    enabled = job.get('enabled', False)
    state = job.get('state', {})
    last_run_status = state.get('lastRunStatus', state.get('lastStatus', 'unknown'))
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_duration_ms = state.get('lastDurationMs', 0)
    last_run_at_ms = state.get('lastRunAtMs')
    
    # Format last run time
    if last_run_at_ms:
        last_run_dt = datetime.fromtimestamp(last_run_at_ms / 1000, tz=timezone.utc)
        last_run_str = last_run_dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        time_since_ms = now_ms - last_run_at_ms
        time_since_str = f"{time_since_ms // 1000} seconds ago"
    else:
        last_run_str = "Never"
        time_since_str = "N/A"
    
    # Format last duration
    if last_duration_ms:
        duration_str = f"{last_duration_ms / 1000:.2f} seconds"
    else:
        duration_str = "N/A"
    
    # Determine status emoji
    if not enabled:
        status_emoji = "⚪"
    elif last_run_status == "ok" and consecutive_errors == 0:
        status_emoji = "🟢"
    elif last_run_status == "error" or consecutive_errors > 0:
        status_emoji = "🔴"
    else:
        status_emoji = "⚪"
    
    report_lines.append(f"### {status_emoji} {name} (`{job_id}`)")
    report_lines.append(f"- **Enabled:** {enabled}")
    report_lines.append(f"- **Last Run Status:** {last_run_status}")
    report_lines.append(f"- **Consecutive Errors:** {consecutive_errors}")
    report_lines.append(f"- **Last Run Duration:** {duration_str}")
    report_lines.append(f"- **Last Run At:** {last_run_str}")
    report_lines.append(f"- **Time Since Last Run:** {time_since_str}")
    report_lines.append("")

# Identify problematic jobs
problematic = []
for job in jobs:
    job_id = job.get('id')
    name = job.get('name')
    enabled = job.get('enabled', False)
    state = job.get('state', {})
    last_run_status = state.get('lastRunStatus', state.get('lastStatus', 'unknown'))
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_duration_ms = state.get('lastDurationMs', 0)
    last_run_at_ms = state.get('lastRunAtMs')
    
    issues = []
    if not enabled:
        issues.append("Disabled unexpectedly")
    if consecutive_errors > 2:
        issues.append(f"Consecutive errors > 2 ({consecutive_errors})")
    if last_duration_ms > 3600000:
        issues.append(f"Extremely long run time ({last_duration_ms / 3600000:.2f} hours)")
    if last_run_at_ms is not None:
        interval_sec = cron_to_interval_seconds(job.get('schedule', {}).get('expr', '0 0 * * *'))
        time_since_last_run_ms = now_ms - last_run_at_ms
        if time_since_last_run_ms > (2 * interval_sec * 1000):
            issues.append(f"Hasn't run in over 2x scheduled interval ({time_since_last_run_ms / 1000:.0f}s > {2 * interval_sec}s)")
    elif last_run_at_ms is None:
        issues.append("Never run")
    
    if issues:
        problematic.append((job_id, name, issues))

if problematic:
    report_lines.append("## 🚨 Problematic Jobs Needing Attention")
    for job_id, name, issues in problematic:
        report_lines.append(f"### {name} (`{job_id}`)")
        for issue in issues:
            report_lines.append(f"- {issue}")
        report_lines.append("")
else:
    report_lines.append("## ✅ No Problematic Jobs Found")
    report_lines.append("")

# Recommended actions
report_lines.append("## Recommended Actions")
if problematic:
    report_lines.append("1. Investigate the problematic jobs listed above.")
    report_lines.append("2. For disabled jobs, check if they should be re-enabled.")
    report_lines.append("3. For jobs with consecutive errors, examine the error logs and fix underlying issues.")
    report_lines.append("4. For jobs with long run times, consider optimizing or increasing timeout limits.")
    report_lines.append("5. For jobs not running on schedule, check the scheduler and system time.")
else:
    report_lines.append("1. No immediate actions required. Continue monitoring.")
    report_lines.append("2. Consider setting up alerts for future issues.")

# Check if we need to manually trigger the SlashAI Daily Tool Check job
daily_tool_check_id = "7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d"
daily_tool_check_job = None
for job in jobs:
    if job.get('id') == daily_tool_check_id:
        daily_tool_check_job = job
        break

if daily_tool_check_job:
    consecutive_errors = daily_tool_check_job.get('state', {}).get('consecutiveErrors', 0)
    if consecutive_errors > 0:
        report_lines.append("")
        report_lines.append("## ⚠️ Manual Trigger Advised")
        report_lines.append(f"The SlashAI Daily Tool Check job (`{daily_tool_check_id}`) has {consecutive_errors} consecutive error(s).")
        report_lines.append("Consider manually triggering it to test if the underlying issue is resolved.")
        # Actually trigger the job
        print(f"SlashAI Daily Tool Check job has {consecutive_errors} consecutive errors. Triggering manually...")
        result = subprocess.run(["openclaw", "cron", "run", "--id", daily_tool_check_id], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully triggered job {daily_tool_check_id}")
            print(f"Output: {result.stdout}")
            report_lines.append(f"✅ Successfully triggered job {daily_tool_check_id} at {datetime.now(timezone.utc).isoformat()}")
        else:
            print(f"Failed to trigger job {daily_tool_check_id}")
            print(f"Error: {result.stderr}")
            report_lines.append(f"❌ Failed to trigger job {daily_tool_check_id}: {result.stderr}")
    else:
        report_lines.append("")
        report_lines.append("## ℹ️ SlashAI Daily Tool Check")
        report_lines.append(f"The SlashAI Daily Tool Check job (`{daily_tool_check_id}`) has no consecutive errors. No manual trigger needed.")
else:
    report_lines.append("")
    report_lines.append(f"## ⚠️ SlashAI Daily Tool Check job not found!")

# Write the report to the specified file
report_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md'
with open(report_path, 'w') as f:
    f.write('\n'.join(report_lines))

print(f"Health report written to {report_path}")

# Log completion status to system logs (append to existing log file)
log_file = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-check.log'
try:
    with open(log_file, 'a') as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] Cron health check completed. Report saved to {report_path}\n")
        f.write(f"Overall health: {overall_health}\n")
except Exception as e:
    print(f"Warning: Could not write to log file {log_file}: {e}", file=sys.stderr)

# Also log to syslog using logger command
try:
    subprocess.run(["logger", "SlashAI Cron Health Check completed. Report saved to " + report_path], check=False)
except Exception as e:
    print(f"Warning: Could not log to syslog: {e}", file=sys.stderr)