#!/usr/bin/env python3
import json
import datetime
import time
import os

# Current time from user: Friday, July 3rd, 2026 - 12:02 (America/Chicago) / 2026-07-03 17:02 UTC
# We'll use the current system time for consistency
now_ms = int(time.time() * 1000)
now_dt = datetime.datetime.fromtimestamp(time.time(), datetime.timezone.utc)
print(f"Current time (UTC): {now_dt.isoformat()}")

# Load cron jobs from the slashai directory (inner)
cron_jobs_path = 'cron_jobs.json'
if not os.path.exists(cron_jobs_path):
    # Try alternative paths
    alt_paths = [
        '../cron_jobs.json',
        './slashai/cron_jobs.json',
        '../slashai/cron_jobs.json'
    ]
    for path in alt_paths:
        if os.path.exists(path):
            cron_jobs_path = path
            break

print(f"Loading cron jobs from: {cron_jobs_path}")
with open(cron_jobs_path, 'r') as f:
    data = json.load(f)

jobs = data.get('jobs', [])
print(f"Found {len(jobs)} cron jobs\n")

# Analyze each job
issues = []
job_details = []

for job in jobs:
    job_id = job['id']
    name = job['name']
    enabled = job.get('enabled', False)
    state = job.get('state', {})
    last_run_status = state.get('lastRunStatus', 'unknown')
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_run_at_ms = state.get('lastRunAtMs', 0)
    last_duration_ms = state.get('lastDurationMs', 0)
    schedule_expr = job.get('schedule', {}).get('expr', '')
    schedule_kind = job.get('schedule', {}).get('kind', '')
    tz = job.get('schedule', {}).get('tz', '')
    
    # Calculate time since last run
    time_since_last_run_ms = now_ms - last_run_at_ms if last_run_at_ms > 0 else float('inf')
    time_since_last_run_hours = time_since_last_run_ms / (1000 * 60 * 60) if last_run_at_ms > 0 else float('inf')
    time_since_last_run_days = time_since_last_run_hours / 24
    
    # Determine expected interval from cron expression (simplified)
    expected_interval_hours = None
    if schedule_expr == '0 */6 * * *':  # every 6 hours
        expected_interval_hours = 6
    elif schedule_expr == '0 8 * * *':  # daily at 8 AM
        expected_interval_hours = 24
    elif schedule_expr == '0 10 * * *':  # daily at 10 AM
        expected_interval_hours = 24
    elif schedule_expr == '0 10 * * 1':  # weekly on Monday at 10 AM
        expected_interval_hours = 24 * 7
    elif schedule_expr == '0 10 */14 * *':  # every 14 days at 10 AM
        expected_interval_hours = 24 * 14
    elif schedule_expr == '0 10 1 * *':  # monthly on 1st at 10 AM
        expected_interval_hours = 24 * 30  # approximate
    else:
        # Default to 24 hours if unknown
        expected_interval_hours = 24
    
    # Check for issues
    job_issues = []
    
    if not enabled:
        job_issues.append('Job is disabled unexpectedly')
    
    if last_run_status == 'error':
        job_issues.append(f'Last run status: error')
    
    if consecutive_errors > 2:
        job_issues.append(f'Consecutive errors: {consecutive_errors} (>2 threshold)')
    
    if expected_interval_hours and time_since_last_run_hours > (2 * expected_interval_hours):
        job_issues.append(
            f'Has not run for {time_since_last_run_hours:.1f} hours '
            f'(>2x expected interval of {expected_interval_hours} hours)'
        )
    
    if last_duration_ms > (60 * 60 * 1000):  # > 1 hour
        job_issues.append(
            f'Last run duration: {last_duration_ms / (1000*60):.1f} minutes (>1 hour threshold)'
        )
    
    job_details.append({
        'id': job_id,
        'name': name,
        'enabled': enabled,
        'last_run_status': last_run_status,
        'consecutive_errors': consecutive_errors,
        'last_run_at_ms': last_run_at_ms,
        'last_duration_ms': last_duration_ms,
        'time_since_last_run_hours': time_since_last_run_hours,
        'time_since_last_run_days': time_since_last_run_days,
        'schedule_expr': schedule_expr,
        'timezone': tz,
        'issues': job_issues
    })
    
    if job_issues:
        issues.append({
            'id': job_id,
            'name': name,
            'issues': job_issues,
            'details': {
                'enabled': enabled,
                'lastRunStatus': last_run_status,
                'consecutiveErrors': consecutive_errors,
                'lastRunAtMs': last_run_at_ms,
                'lastDurationMs': last_duration_ms,
                'timeSinceLastRunHours': time_since_last_run_hours,
                'schedule': schedule_expr,
                'timezone': tz
            }
        })

# Generate Markdown Report
report_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md'

with open(report_path, 'w') as f:
    f.write('# SlashAI Cron Health Report\n\n')
    f.write(f'**Generated:** {now_dt.strftime("%Y-%m-%d %H:%M:%S UTC")}  \n')
    f.write(f'**Generated (America/Chicago):** {now_dt.astimezone(datetime.timezone(datetime.timedelta(hours=-5))).strftime("%Y-%m-%d %H:%M:%S")}  \n\n')
    
    f.write('---\n\n')
    
    f.write('## Executive Summary\n\n')
    f.write(f'- **Total Cron Jobs Monitored:** {len(jobs)}\n')
    f.write(f'- **Jobs with Issues:** {len(issues)}\n')
    f.write(f'- **Healthy Jobs:** {len(jobs) - len(issues)}\n')
    f.write(f'- **Overall System Health:** {"⚠️ Attention Required" if issues else "✅ Healthy"}\n\n')
    
    if issues:
        f.write('## ⚠️ Issues Requiring Attention\n\n')
        for issue in issues:
            f.write(f'### {issue["name"]} (`{issue["id"]}`)\n\n')
            for problem in issue['issues']:
                f.write(f'- {problem}\n')
            f.write('\n')
            
            # Details
            details = issue['details']
            f.write('<details>\n<summary>Show Details</summary>\n\n')
            f.write(f'- **Enabled:** {details["enabled"]}\n')
            f.write(f'- **Last Run Status:** {details["lastRunStatus"]}\n')
            f.write(f'- **Consecutive Errors:** {details["consecutiveErrors"]}\n')
            f.write(f'- **Last Run:** {datetime.datetime.fromtimestamp(details["lastRunAtMs"]/1000, datetime.timezone.utc).isoformat() if details["lastRunAtMs"] > 0 else "Never"}  \n')
            f.write(f'  ({datetime.datetime.fromtimestamp(details["lastRunAtMs"]/1000, datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=-5))).strftime("%Y-%m-%d %H:%M:%S CST")})\n')
            f.write(f'- **Last Run Duration:** {details["lastDurationMs"] / (1000*60):.2f} minutes\n')
            f.write(f'- **Time Since Last Run:** {details["timeSinceLastRunHours"]:.2f} hours ({details["timeSinceLastRunHours"]/24:.2f} days)\n')
            f.write(f'- **Schedule:** `{details["schedule"]}` ({details["timezone"]})\n')
            f.write('</details>\n\n')
    else:
        f.write('## ✅ All Systems Healthy\n\n')
        f.write('No issues detected with any cron jobs.\n\n')
    
    f.write('---\n\n')
    
    f.write('## Detailed Job Status\n\n')
    f.write('| Job Name | Status | Enabled | Last Run | Duration | Time Since | Issues |\n')
    f.write('|----------|--------|---------|----------|----------|------------|--------|\n')
    for job in job_details:
        status_emoji = '✅' if job['last_run_status'] == 'ok' and job['consecutive_errors'] == 0 and not job['issues'] else '⚠️'
        last_run_str = 'Never'
        if job['last_run_at_ms'] > 0:
            dt = datetime.datetime.fromtimestamp(job['last_run_at_ms']/1000, datetime.timezone.utc)
            last_run_str = dt.strftime('%Y-%m-%d %H:%M')
        duration_str = f"{job['last_duration_ms'] / (1000*60):.1f} min" if job['last_duration_ms'] > 0 else 'N/A'
        since_str = f"{job['time_since_last_run_hours']:.1f}h" if job['time_since_last_run_hours'] < 24 else f"{job['time_since_last_run_days']:.1f}d"
        issues_count = len(job['issues'])
        issues_str = f"{issues_count}" if issues_count > 0 else "None"
        
        f.write(f"| {job['name']} | {status_emoji} | {'Yes' if job['enabled'] else 'No'} | {last_run_str} | {duration_str} | {since_str} | {issues_str} |\n")
    
    f.write('\n---\n\n')
    
    f.write('## Special Check: SlashAI Daily Tool Check\n\n')
    daily_tool_id = '7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d'
    daily_tool_job = None
    for job in jobs:
        if job['id'] == daily_tool_id:
            daily_tool_job = job
            break
    
    if daily_tool_job:
        state = daily_tool_job.get('state', {})
        consecutive_errors = state.get('consecutiveErrors', 0)
        last_run_status = state.get('lastRunStatus', 'unknown')
        
        f.write(f'- **Job Name:** SlashAI Daily Tool Check\n')
        f.write(f'- **Job ID:** `{daily_tool_id}`\n')
        f.write(f'- **Consecutive Errors:** {consecutive_errors}\n')
        f.write(f'- **Last Run Status:** {last_run_status}\n')
        f.write(f'- **Enabled:** {daily_tool_job.get("enabled", False)}\n')
        f.write(f'- **Last Run:** {datetime.datetime.fromtimestamp(state.get("lastRunAtMs", 0)/1000, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC") if state.get("lastRunAtMs", 0) > 0 else "Never"}  \n')
        f.write(f'  ({datetime.datetime.fromtimestamp(state.get("lastRunAtMs", 0)/1000, datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=-5))).strftime("%Y-%m-%d %H:%M:%S CST")})\n\n')
        
        if consecutive_errors > 0:
            f.write('### ⚠️ Action Required\n\n')
            f.write('The SlashAI Daily Tool Job has consecutive errors. As per instructions, ')
            f.write('it should be manually triggered to test if the underlying issue is resolved.\n\n')
            f.write('**Note:** Since this check is being performed automatically, manual triggering ')
            f.write('would need to be done by a system administrator or via the appropriate ')
            f.write('OpenClaw command.\n')
        else:
            f.write('### ✅ Status Healthy\n\n')
            f.write('The SlashAI Daily Tool Job has no consecutive errors and is operating normally.\n')
    else:
        f.write('Could not find SlashAI Daily Tool Job with ID: ' + daily_tool_id + '\n')
    
    f.write('\n---\n\n')
    
    f.write('## Recommendations\n\n')
    if issues:
        f.write('1. **Investigate Disabled Jobs:** Check why any jobs show as disabled unexpectedly.\n')
        f.write('2. **Address Repeated Failures:** Investigate jobs with consecutive errors > 2.\n')
        f.write('3. **Check Scheduling System:** Investigate why jobs have not run for extended periods.\n')
        f.write('4. **Review Long-Running Jobs:** Optimize jobs that consistently run longer than 1 hour.\n')
        f.write('5. **Verify Cron System:** Ensure the underlying cron/scheduling system is operational.\n')
    else:
        f.write('1. **Continue Monitoring:** Regular health checks should continue to ensure system stability.\n')
        f.write('2. **Review Logs:** Periodically check job logs for any emerging issues.\n')
        f.write('3. **Update Documentation:** Ensure runbooks are up-to-date for any manual interventions.\n')
    
    f.write('\n---\n\n')
    f.write('*This report was generated automatically by the SlashAI Cron Health Monitor.*\n')

print(f"Report generated successfully at: {report_path}")

# Also, let's output a summary to console
print("\n" + "="*60)
print("CRON HEALTH CHECK SUMMARY")
print("="*60)
print(f"Total Jobs: {len(jobs)}")
print(f"Jobs with Issues: {len(issues)}")
print(f"Healthy Jobs: {len(jobs) - len(issues)}")
if issues:
    print("\nIssues Found:")
    for issue in issues:
        print(f"  - {issue['name']}: {', '.join(issue['issues'][:2])}{'...' if len(issue['issues']) > 2 else ''}")
else:
    print("\n✅ All jobs are healthy!")

# Special check for daily tool
if daily_tool_job:
    state = daily_tool_job.get('state', {})
    consecutive_errors = state.get('consecutiveErrors', 0)
    print(f"\nSlashAI Daily Tool Check:")
    print(f"  Consecutive Errors: {consecutive_errors}")
    if consecutive_errors > 0:
        print("  ⚠️  ACTION NEEDED: Manual trigger recommended")
    else:
        print("  ✅ Status: Healthy")