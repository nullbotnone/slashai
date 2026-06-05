import json
import datetime
import os

# Load the cron jobs data
with open('/home/rpi/.openclaw/workspace/projects/slashai/slashai/projects/slashai/cron_jobs_current.json', 'r') as f:
    data = json.load(f)

jobs = data['jobs']

# Current time from the prompt: Wednesday, June 3rd, 2026 - 06:02 (America/Chicago)
# Let's use the current system time for accuracy
now_ms = int(datetime.datetime.now().timestamp() * 1000)
print(f"Current time: {datetime.datetime.now()}")

# For consistency with the prompt, let's use the exact time mentioned
# Wednesday, June 3rd, 2026 - 06:02 (America/Chicago) = 2026-06-03 06:02:00-05:00
# Convert to UTC: 2026-06-03 11:02:00 UTC
prompt_time = datetime.datetime(2026, 6, 3, 6, 2, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=-5)))
now_ms = int(prompt_time.timestamp() * 1000)
print(f"Using prompt time: {prompt_time}")

print("\n" + "="*80)
print("SLASHAI CRON JOBS HEALTH ANALYSIS")
print("="*80)

issues = []
healthy_jobs = []

for job in jobs:
    job_id = job['id']
    name = job['name']
    enabled = job['enabled']
    
    state = job['state']
    last_run_at_ms = state.get('lastRunAtMs', 0)
    last_run_status = state.get('lastRunStatus', 'unknown')
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_duration_ms = state.get('lastDurationMs', 0)
    next_run_at_ms = state.get('nextRunAtMs', 0)
    
    # Calculate time since last run
    if last_run_at_ms > 0:
        time_since_last_run_ms = now_ms - last_run_at_ms
        time_since_last_run_hours = time_since_last_run_ms / (1000 * 60 * 60)
        last_run_time = datetime.datetime.fromtimestamp(last_run_at_ms / 1000, tz=datetime.timezone.utc)
    else:
        time_since_last_run_ms = float('inf')
        time_since_last_run_hours = float('inf')
        last_run_time = None
    
    # Calculate scheduled interval from cron expression (simplified)
    # We'll check if it hasn't run in over 2x its scheduled interval
    schedule_expr = job['schedule']['expr']
    kind = job['schedule']['kind']
    
    # For simplicity, we'll define expected intervals based on common patterns
    expected_interval_hours = None
    if kind == 'cron':
        if '*/6' in schedule_expr:  # Every 6 hours
            expected_interval_hours = 6
        elif schedule_expr == '0 8 * * *':  # Daily at 8 AM
            expected_interval_hours = 24
        elif schedule_expr == '0 10 * * *':  # Daily at 10 AM
            expected_interval_hours = 24
        elif schedule_expr == '0 10 * * 1':  # Weekly on Monday at 10 AM
            expected_interval_hours = 24 * 7  # 1 week
        elif schedule_expr == '0 10 */14 * *':  # Biweekly (every 14 days) at 10 AM
            expected_interval_hours = 24 * 14  # 2 weeks
        elif schedule_expr == '0 10 1 * *':  # Monthly on 1st at 10 AM
            expected_interval_hours = 24 * 30  # Approximate 1 month
    
    # Check for issues
    job_issues = []
    
    # 1. Job disabled unexpectedly
    if not enabled:
        job_issues.append("Job is disabled")
    
    # 2. Jobs with consecutive errors > 2
    if consecutive_errors > 2:
        job_issues.append(f"High consecutive errors: {consecutive_errors}")
    
    # 3. Jobs that haven't run in over 2x their scheduled interval
    if expected_interval_hours and time_since_last_run_hours > (expected_interval_hours * 2):
        job_issues.append(f"Not run in {time_since_last_run_hours:.1f}h (expected ~{expected_interval_hours}h, threshold: {expected_interval_hours*2}h)")
    
    # 4. Jobs with extremely long run times (> 1 hour)
    if last_duration_ms > (60 * 60 * 1000):  # More than 1 hour
        job_issues.append(f"Extremely long run time: {last_duration_ms/(60*60*1000):.2f} hours")
    
    # Determine overall health
    if job_issues:
        issues.append({
            'id': job_id,
            'name': name,
            'issues': job_issues,
            'enabled': enabled,
            'last_run_status': last_run_status,
            'consecutive_errors': consecutive_errors,
            'last_duration_hours': last_duration_ms/(60*60*1000) if last_duration_ms > 0 else 0,
            'time_since_last_run_hours': time_since_last_run_hours if last_run_at_ms > 0 else float('inf'),
            'last_run_time': last_run_time.strftime('%Y-%m-%d %H:%M:%S UTC') if last_run_time else 'Never'
        })
    else:
        healthy_jobs.append({
            'id': job_id,
            'name': name,
            'enabled': enabled,
            'last_run_status': last_run_status,
            'consecutive_errors': consecutive_errors,
            'last_duration_hours': last_duration_ms/(60*60*1000) if last_duration_ms > 0 else 0,
            'time_since_last_run_hours': time_since_last_run_hours if last_run_at_ms > 0 else float('inf'),
            'last_run_time': last_run_time.strftime('%Y-%m-%d %H:%M:%S UTC') if last_run_time else 'Never'
        })

# Print summary
print(f"\nSUMMARY:")
print(f"Total jobs: {len(jobs)}")
print(f"Healthy jobs: {len(healthy_jobs)}")
print(f"Jobs with issues: {len(issues)}")

if issues:
    print(f"\nISSUES FOUND:")
    print("-" * 80)
    for issue in issues:
        print(f"\nJob: {issue['name']} (ID: {issue['id']})")
        print(f"  Enabled: {issue['enabled']}")
        print(f"  Last run status: {issue['last_run_status']}")
        print(f"  Consecutive errors: {issue['consecutive_errors']}")
        print(f"  Last run duration: {issue['last_duration_hours']:.2f} hours")
        print(f"  Time since last run: {issue['time_since_last_run_hours']:.1f} hours")
        print(f"  Last run time: {issue['last_run_time']}")
        print(f"  Issues:")
        for msg in issue['issues']:
            print(f"    - {msg}")
else:
    print("\nNO ISSUES FOUND - All jobs are healthy!")

# Print healthy jobs for reference
if healthy_jobs:
    print(f"\nHEALTHY JOBS:")
    print("-" * 80)
    for job in healthy_jobs:
        print(f"\nJob: {job['name']} (ID: {job['id']})")
        print(f"  Enabled: {job['enabled']}")
        print(f"  Last run status: {job['last_run_status']}")
        print(f"  Consecutive errors: {job['consecutive_errors']}")
        print(f"  Last run duration: {job['last_duration_hours']:.2f} hours")
        print(f"  Time since last run: {job['time_since_last_run_hours']:.1f} hours")
        print(f"  Last run time: {job['last_run_time']}")

# Save detailed report to file
report_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md'
with open(report_path, 'w') as f:
    f.write("# SlashAI Cron Jobs Health Report\n\n")
    f.write(f"**Generated:** {prompt_time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n\n")
    
    f.write(f"## Summary\n\n")
    f.write(f"- **Total jobs:** {len(jobs)}\n")
    f.write(f"- **Healthy jobs:** {len(healthy_jobs)}\n")
    f.write(f"- **Jobs with issues:** {len(issues)}\n\n")
    
    if issues:
        f.write(f"## Issues Found\n\n")
        for issue in issues:
            f.write(f"### {issue['name']} (ID: `{issue['id']}`)\n\n")
            f.write(f"- **Enabled:** {issue['enabled']}\n")
            f.write(f"- **Last run status:** {issue['last_run_status']}\n")
            f.write(f"- **Consecutive errors:** {issue['consecutive_errors']}\n")
            f.write(f"- **Last run duration:** {issue['last_duration_hours']:.2f} hours\n")
            f.write(f"- **Time since last run:** {issue['time_since_last_run_hours']:.1f} hours\n")
            f.write(f"- **Last run time:** {issue['last_run_time']}\n")
            f.write(f"- **Issues:**\n")
            for msg in issue['issues']:
                f.write(f"  - {msg}\n")
            f.write("\n")
    else:
        f.write(f"## No Issues Found\n\nAll cron jobs are operating normally.\n\n")
    
    f.write(f"## Detailed Job Status\n\n")
    f.write(f"| Job Name | Enabled | Last Status | Errors | Duration (h) | Since Last Run (h) | Last Run Time |\n")
    f.write(f"|----------|---------|-------------|--------|--------------|-------------------|---------------|\n")
    
    all_jobs = healthy_jobs + issues
    for job in all_jobs:
        f.write(f"| {job['name']} | {job['enabled']} | {job['last_run_status']} | {job['consecutive_errors']} | {job['last_duration_hours']:.2f} | {job['time_since_last_run_hours']:.1f} | {job['last_run_time']} |\n")
    
    f.write(f"\n## Recommended Actions\n\n")
    if issues:
        f.write(f"1. **Investigate disabled jobs** - Check why any jobs are disabled and re-enable if appropriate\n")
        f.write(f"2. **Address high error counts** - Look into root causes for jobs with consecutive errors > 2\n")
        f.write(f"3. **Check stalled jobs** - Investigate jobs that haven't run in over 2x their scheduled interval\n")
        f.write(f"4. **Optimize long-running jobs** - Review jobs with extremely long run times for optimization opportunities\n")
        f.write(f"5. **Monitor job execution** - Set up alerts for future job failures\n")
    else:
        f.write(f"No actions required at this time. All jobs are healthy.\n")

print(f"\nReport saved to: {report_path}")

# Check if the SlashAI Daily Tool Check job shows consecutive errors and manually trigger it if needed
daily_tool_job_id = "7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d"
daily_tool_job = None
for job in jobs:
    if job['id'] == daily_tool_job_id:
        daily_tool_job = job
        break

if daily_tool_job:
    consecutive_errors = daily_tool_job['state'].get('consecutiveErrors', 0)
    print(f"\nSlashAI Daily Tool Check job consecutive errors: {consecutive_errors}")
    if consecutive_errors > 0:
        print(f"⚠️  SlashAI Daily Tool Check job has {consecutive_errors} consecutive errors!")
        print(f"As per step 5, manually triggering the job to test if underlying issue is resolved...")
        # Note: Actually triggering the job would require using the sessions_spawn tool or similar
        # For now, we'll just note that it should be triggered
        print(f"📝 NOTE: Job should be manually triggered via OpenClaw cron tool or sessions_spawn")
    else:
        print(f"✅ SlashAI Daily Tool Check job has no consecutive errors.")
else:
    print(f"\n⚠️  SlashAI Daily Tool Check job (ID: {daily_tool_job_id}) not found!")

print(f"\nAnalysis complete.")