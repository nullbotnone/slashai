import json
import time
import sys
from datetime import datetime, timezone

# Load the live jobs data
with open('/home/rpi/.openclaw/workspace/projects/slashai/cron_jobs_live.json', 'r') as f:
    data = json.load(f)

jobs = data['jobs']

# Current time in milliseconds
now_ms = int(time.time() * 1000)

# Helper to parse cron expression and approximate interval in seconds
def cron_to_interval_seconds(expr):
    # Very simple parser for our specific expressions
    # We only handle the ones we know
    if expr == '0 */6 * * *':
        return 6 * 3600  # every 6 hours
    if expr == '0 8 * * *':
        return 24 * 3600  # daily
    if expr == '0 10 * * *':
        return 24 * 3600  # daily
    if expr == '0 10 * * 1':
        return 7 * 24 * 3600  # weekly
    if expr == '0 10 */14 * *':
        return 14 * 24 * 3600  # every 14 days
    if expr == '0 10 1 * *':
        return 30 * 24 * 3600  # approximate monthly
    # Default to 1 hour if unknown
    return 3600

# Analysis results
results = []
overall_status = 'HEALTHY'
issues = []
recommended_actions = []

for job in jobs:
    job_id = job['id']
    name = job['name']
    enabled = job['enabled']
    schedule_expr = job['schedule']['expr']
    state = job['state']
    
    last_run_at_ms = state.get('lastRunAtMs', 0)
    last_run_status = state.get('lastRunStatus', 'unknown')
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_duration_ms = state.get('lastDurationMs', 0)
    next_run_at_ms = state.get('nextRunAtMs', 0)
    
    # Compute time since last run
    time_since_last_run_ms = now_ms - last_run_at_ms if last_run_at_ms > 0 else float('inf')
    time_since_last_run_h = time_since_last_run_ms / (3600 * 1000) if last_run_at_ms > 0 else float('inf')
    
    # Compute interval in seconds
    interval_seconds = cron_to_interval_seconds(schedule_expr)
    interval_ms = interval_seconds * 1000
    
    # Check if the job has run at least once
    has_run = last_run_at_ms > 0
    
    # Determine if the job is overdue (past next run time)
    overdue = now_ms > next_run_at_ms if next_run_at_ms > 0 else False
    
    # Check if hasn't run in over 2x interval
    interval_exceeded = False
    if has_run and interval_ms > 0:
        interval_exceeded = time_since_last_run_ms > (2 * interval_ms)
    
    # Check for extremely long run time (> 1 hour)
    long_running = last_duration_ms > (3600 * 1000)
    
    # Determine issue status for this job
    job_issues = []
    if not enabled:
        job_issues.append('DISABLED UNEXPECTEDLY')
    if last_run_status == 'error':
        job_issues.append('LAST RUN ERROR')
    if consecutive_errors > 2:
        job_issues.append(f'HIGH CONSECUTIVE ERRORS ({consecutive_errors})')
    if not has_run:
        job_issues.append('NEVER RUN')
    elif interval_exceeded:
        job_issues.append(f'HAS NOT RUN IN OVER 2x INTERVAL ({time_since_last_run_h:.1f}h > {2*interval_seconds/3600:.1f}h)')
    if overdue:
        job_issues.append('OVERDUE (past next run time)')
    if long_running:
        job_issues.append(f'LONG RUNNING ({last_duration_ms/3600000:.1f}h > 1h)')
    
    if job_issues:
        overall_status = 'UNHEALTHY'
        issues.append({
            'id': job_id,
            'name': name,
            'issues': job_issues
        })
        # Add recommended actions
        if not enabled:
            recommended_actions.append(f"Enable job '{name}' (ID: {job_id})")
        if last_run_status == 'error':
            recommended_actions.append(f"Investigate error for job '{name}': {state.get('lastError', 'Unknown error')}")
        if consecutive_errors > 2:
            recommended_actions.append(f"Investigate recurring failures for job '{name}' (consecutive errors: {consecutive_errors})")
        if not has_run:
            recommended_actions.append(f"Check why job '{name}' has never run")
        elif interval_exceeded:
            recommended_actions.append(f"Check schedule and system time for job '{name}' (last run {time_since_last_run_h:.1f}h ago)")
        if overdue:
            recommended_actions.append(f"Job '{name}' is overdue; consider triggering manually")
        if long_running:
            recommended_actions.append(f"Investigate why job '{name}' runs longer than 1 hour")
    
    results.append({
        'id': job_id,
        'name': name,
        'enabled': enabled,
        'last_run_status': last_run_status,
        'consecutive_errors': consecutive_errors,
        'last_run_duration_ms': last_duration_ms,
        'time_since_last_run_h': time_since_last_run_h if has_run else None,
        'next_run_at_ms': next_run_at_ms,
        'issues': job_issues
    })

# Special handling for the Daily Tool Check job if it has consecutive errors
daily_tool_job_id = '7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d'
daily_tool_job = None
for job in jobs:
    if job['id'] == daily_tool_job_id:
        daily_tool_job = job
        break

if daily_tool_job:
    state = daily_tool_job['state']
    if state.get('consecutiveErrors', 0) > 0:
        # We already captured this in issues, but we can add a specific recommendation
        recommended_actions.append(f"Manually trigger the SlashAI Daily Tool Check job (ID: {daily_tool_job_id}) to test if the underlying issue is resolved (current error: {state.get('lastError', 'Unknown')})")

# Generate report
report_lines = []
report_lines.append('# SlashAI Cron Health Check Report')
report_lines.append(f'Generated at: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")}')
report_lines.append('')
report_lines.append(f'Total jobs: {len(jobs)}')
enabled_count = sum(1 for j in jobs if j['enabled'])
report_lines.append(f'Enabled jobs: {enabled_count}')
disabled_count = len(jobs) - enabled_count
report_lines.append(f'Disabled jobs: {disabled_count}')
report_lines.append('')
report_lines.append('## Overall System Health')
if overall_status == 'HEALTHY':
    report_lines.append('**Status:** ✅ HEALTHY - No issues detected.')
else:
    report_lines.append('**Status:** ❌ UNHEALTHY - Issues detected.')
report_lines.append('')
if issues:
    report_lines.append('## Issues Found')
    for issue in issues:
        report_lines.append(f"- **{issue['name']} (ID: {issue['id']})**: {', '.join(issue['issues'])}")
    report_lines.append('')
else:
    report_lines.append('## Issues Found')
    report_lines.append('None')
    report_lines.append('')
if recommended_actions:
    report_lines.append('## Recommended Actions')
    for action in set(recommended_actions):  # deduplicate
        report_lines.append(f'- {action}')
    report_lines.append('')
else:
    report_lines.append('## Recommended Actions')
    report_lines.append('No specific actions required. Continue monitoring.')
    report_lines.append('')

# Add a summary table
report_lines.append('## Job Details')
report_lines.append('| Job Name | Enabled | Last Run Status | Consecutive Errors | Last Duration (h) | Time Since Last Run (h) | Next Run | Issues |')
report_lines.append('|----------|---------|-----------------|--------------------|-------------------|-------------------------|----------|--------|')
for r in results:
    name = r['name']
    enabled_str = 'Yes' if r['enabled'] else 'No'
    last_status = r['last_run_status']
    consec = r['consecutive_errors']
    last_dur_h = f"{r['last_run_duration_ms'] / 3600000:.2f}" if r['last_run_duration_ms'] > 0 else '0'
    time_since_h = f"{r['time_since_last_run_h']:.2f}" if r['time_since_last_run_h'] is not None else 'N/A'
    next_run = datetime.fromtimestamp(r['next_run_at_ms']/1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M') if r['next_run_at_ms'] > 0 else 'N/A'
    issues_str = ', '.join(r['issues']) if r['issues'] else 'None'
    report_lines.append(f'| {name} | {enabled_str} | {last_status} | {consec} | {last_dur_h} | {time_since_h} | {next_run} | {issues_str} |')

# Write to file
report_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md'
with open(report_path, 'w') as f:
    f.write('\n'.join(report_lines))

print(f'Report written to {report_path}')
print(f'Overall status: {overall_status}')
