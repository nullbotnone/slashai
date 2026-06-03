import json
import sys
from datetime import datetime, timezone

# Load cron jobs data
with open('/home/rpi/.openclaw/workspace/projects/slashai/cron_jobs_current.json', 'r') as f:
    data = json.load(f)

jobs = data['jobs']

# Current time in milliseconds since epoch (from earlier)
# We'll compute using datetime now UTC
now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
print(f"Current time (UTC): {datetime.now(timezone.utc).isoformat()}")
print(f"Current time ms: {now_ms}")
print()

def parse_cron_interval(expr):
    """Very rough approximation: convert cron expression to seconds.
    Only handles simple cases like '0 */6 * * *' (every 6 hours), '0 8 * * *' (daily at 8), etc.
    We'll compute expected interval in seconds.
    """
    parts = expr.split()
    if len(parts) != 5:
        return None
    minute, hour, day, month, dow = parts
    # We'll compute the smallest interval based on the fields.
    # For simplicity, we'll handle common patterns:
    # If minute is '0' and hour is '*/X' -> every X hours
    # If minute is '0' and hour is fixed and day is '*' -> daily
    # If minute is '0' and hour is fixed and day is '*/X' -> every X days
    # If month is '*' and day is '*' and dow is '*' -> daily or hourly etc.
    # This is a rough approximation; for health check we just need to know if last run > 2x interval.
    # We'll compute expected interval in seconds.
    try:
        if minute == '0' and hour.startswith('*/'):
            # every X hours
            x = int(hour[2:])
            return x * 3600
        if hour == '0' and day.startswith('*/'):
            # every X days at midnight? Actually hour 0 minute 0.
            x = int(day[2:])
            return x * 86400
        if hour == '0' and minute == '0' and day == '*' and month == '*' and dow == '*':
            return 86400  # daily
        if minute == '0' and hour == '0' and day == '*' and month == '*' and dow == '*':
            return 86400
        if minute == '0' and hour == '*' and day == '*' and month == '*' and dow == '*':
            # every hour? Actually minute 0 every hour -> hourly
            return 3600
        # fallback: assume daily
        return 86400
    except:
        return 86400

issues = []
for job in jobs:
    jid = job['id']
    name = job['name']
    enabled = job['enabled']
    state = job['state']
    last_run_status = state.get('lastRunStatus', 'unknown')
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_duration_ms = state.get('lastDurationMs', 0)
    last_run_at_ms = state.get('lastRunAtMs', 0)
    schedule = job['schedule']
    expr = schedule.get('expr', '')
    kind = schedule.get('kind', '')
    
    # Compute time since last run
    time_since_last_run_ms = now_ms - last_run_at_ms if last_run_at_ms > 0 else None
    time_since_last_run_hrs = time_since_last_run_ms / (1000 * 3600) if time_since_last_run_ms is not None else None
    
    # Determine expected interval
    interval_sec = parse_cron_interval(expr) if expr else None
    interval_ms = interval_sec * 1000 if interval_sec else None
    overdue = False
    if interval_ms and time_since_last_run_ms:
        if time_since_last_run_ms > 2 * interval_ms:
            overdue = True
    
    # Check for issues
    if not enabled:
        issues.append((jid, name, "Job disabled unexpectedly"))
    if consecutive_errors > 2:
        issues.append((jid, name, f"Consecutive errors > 2 ({consecutive_errors})"))
    if overdue:
        issues.append((jid, name, f"Hasn't run in over 2x scheduled interval (last run {time_since_last_run_hrs:.1f} hrs ago, interval {interval_sec/3600:.1f} hrs)"))
    if last_duration_ms > 3600000:  # > 1 hour
        issues.append((jid, name, f"Extremely long run time: {last_duration_ms/(1000*3600):.2f} hours"))
    
    # Print job summary
    print(f"Job: {name} ({jid})")
    print(f"  Enabled: {enabled}")
    print(f"  Last run status: {last_run_status}")
    print(f"  Consecutive errors: {consecutive_errors}")
    print(f"  Last duration: {last_duration_ms} ms ({last_duration_ms/1000:.2f} sec)")
    if time_since_last_run_ms is not None:
        print(f"  Time since last run: {time_since_last_run_ms/1000:.0f} sec ({time_since_last_run_ms/(1000*3600):.2f} hrs)")
    if interval_sec:
        print(f"  Schedule interval: {interval_sec/3600:.2f} hrs")
    print()

# Generate report
report_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md'
with open(report_path, 'w') as f:
    f.write('# SlashAI Cron Health Report\\n')
    f.write(f'**Generated at**: {datetime.now(timezone.utc).isoformat()} UTC\\n\\n')
    f.write('## Summary\\n')
    if not issues:
        f.write('All cron jobs are healthy. No issues detected.\\n\\n')
    else:
        f.write(f'Found {len(issues)} issue(s) requiring attention:\\n\\n')
        for jid, name, desc in issues:
            f.write(f'- **{name}** (`{jid}`): {desc}\\n')
        f.write('\\n')
    f.write('## Job Details\\n')
    for job in jobs:
        jid = job['id']
        name = job['name']
        enabled = job['enabled']
        state = job['state']
        last_run_status = state.get('lastRunStatus', 'unknown')
        consecutive_errors = state.get('consecutiveErrors', 0)
        last_duration_ms = state.get('lastDurationMs', 0)
        last_run_at_ms = state.get('lastRunAtMs', 0)
        schedule = job['schedule']
        expr = schedule.get('expr', '')
        time_since_last_run_ms = now_ms - last_run_at_ms if last_run_at_ms > 0 else None
        f.write(f'### {name} (`{jid}`)\\n')
        f.write(f'- Enabled: {enabled}\\n')
        f.write(f'- Last run status: {last_run_status}\\n')
        f.write(f'- Consecutive errors: {consecutive_errors}\\n')
        f.write(f'- Last duration: {last_duration_ms} ms\\n')
        f.write(f'- Last run at: {datetime.fromtimestamp(last_run_at_ms/1000, tz=timezone.utc).isoformat() if last_run_at_ms else \"N/A\"}\\n')
        f.write(f'- Time since last run: {time_since_last_run_ms/1000:.0f} sec ({time_since_last_run_ms/(1000*3600):.2f} hrs) if known\\n')
        f.write(f'- Schedule: {expr}\\n')
        f.write('\\n')
print(f'Report written to {report_path}')

# Step 5: If the SlashAI Daily Tool Check job shows consecutive errors, manually trigger it
daily_tool_job = None
for job in jobs:
    if job['id'] == '7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d':
        daily_tool_job = job
        break
if daily_tool_job:
    consecutive_errors = daily_tool_job['state'].get('consecutiveErrors', 0)
    if consecutive_errors > 0:
        print(f"Daily Tool Check job has consecutive errors: {consecutive_errors}. Manually triggering...")
        # We could trigger via some API, but we don't have a tool. We'll just note.
        # For now, we'll just log that we would trigger.
        print("Note: Manual trigger not implemented in this script; would need to invoke cron tool.")
    else:
        print("Daily Tool Check job has no consecutive errors.")
else:
    print("Daily Tool Check job not found.")

# Step 6: Already saved report.
# Step 7: Log completion status to system logs (channel-independent operation)
# We'll append to a log file.
log_file = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-check.log'
with open(log_file, 'a') as log:
    log.write(f"{datetime.now(timezone.utc).isoformat()} UTC - Cron health check completed. Issues found: {len(issues)}\\n")
print(f"Logged completion to {log_file}")