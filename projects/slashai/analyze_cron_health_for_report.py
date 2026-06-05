#!/usr/bin/env python3
import json
import datetime
import time
import os

# Load cron jobs data
with open('cron_jobs_current.json', 'r') as f:
    data = json.load(f)

jobs = data['jobs']

# Current time in milliseconds
current_time_ms = int(time.time() * 1000)
# Also get human-readable time
current_time = datetime.datetime.fromtimestamp(time.time(), datetime.timezone.utc).astimezone()
print(f"Current time: {current_time}")

# Define thresholds
CONSECUTIVE_ERROR_THRESHOLD = 2
LONG_RUN_TIME_MS = 3600000  # 1 hour

# Helper to parse cron expression to approximate interval (in seconds)
def cron_to_interval_seconds(cron_expr):
    """Very approximate conversion of common cron expressions to interval in seconds."""
    # This is a simplified mapping for common patterns
    if cron_expr == "0 */6 * * *":
        return 6 * 60 * 60  # every 6 hours
    elif cron_expr.startswith("0 ") and cron_expr.endswith(" * * *"):
        # Daily at specific hour:0 8 * * *
        return 24 * 60 * 60  # daily
    elif cron_expr.startswith("0 ") and " * * 1" in cron_expr:
        # Weekly on Monday: 0 10 * * 1
        return 7 * 24 * 60 * 60
    elif cron_expr.startswith("0 ") and " */14 * *" in cron_expr:
        # Biweekly: 0 10 */14 * *
        return 14 * 24 * 60 * 60
    elif cron_expr.startswith("0 ") and " 1 * *" in cron_expr:
        # Monthly: 0 10 1 * *
        return 30 * 24 * 60 * 60  # approximate
    else:
        # fallback: try to compute from nextRunAtMs - lastRunAtMs if available
        return None

def analyze_job(job):
    job_id = job['id']
    name = job['name']
    enabled = job.get('enabled', False)
    state = job.get('state', {})
    last_run_status = state.get('lastRunStatus', state.get('lastStatus', 'unknown'))
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_duration_ms = state.get('lastDurationMs', 0)
    last_run_at_ms = state.get('lastRunAtMs', 0)
    next_run_at_ms = state.get('nextRunAtMs', 0)
    
    # Compute time since last run
    time_since_last_run_ms = current_time_ms - last_run_at_ms if last_run_at_ms > 0 else None
    time_since_last_run_hrs = time_since_last_run_ms / (1000 * 60 * 60) if time_since_last_run_ms else None
    
    # Compute schedule interval from cron expression
    schedule = job.get('schedule', {})
    cron_expr = schedule.get('expr', '')
    interval_seconds = cron_to_interval_seconds(cron_expr)
    interval_ms = interval_seconds * 1000 if interval_seconds else None
    
    # Determine if hasn't run in over 2x interval
    overdue_factor = None
    if time_since_last_run_ms and interval_ms and interval_ms > 0:
        overdue_factor = time_since_last_run_ms / interval_ms
    
    # Issues
    issues = []
    if not enabled:
        issues.append("Job is disabled")
    if last_run_status == 'error':
        issues.append(f"Last run status: error")
    if consecutive_errors > CONSECUTIVE_ERROR_THRESHOLD:
        issues.append(f"Consecutive errors: {consecutive_errors} (> {CONSECUTIVE_ERROR_THRESHOLD})")
    if last_duration_ms > LONG_RUN_TIME_MS:
        issues.append(f"Last run duration: {last_duration_ms}ms (> {LONG_RUN_TIME_MS}ms)")
    if overdue_factor is not None and overdue_factor > 2:
        issues.append(f"Hasn't run in over 2x interval (last run: {time_since_last_run_ms}ms ago, interval: {interval_ms}ms, factor: {overdue_factor:.2f})")
    
    return {
        'id': job_id,
        'name': name,
        'enabled': enabled,
        'last_run_status': last_run_status,
        'consecutive_errors': consecutive_errors,
        'last_duration_ms': last_duration_ms,
        'last_duration_str': f"{last_duration_ms/1000:.2f} seconds" if last_duration_ms else "N/A",
        'last_run_at_ms': last_run_at_ms,
        'last_run_at_str': datetime.datetime.fromtimestamp(last_run_at_ms/1000, datetime.timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S %Z') if last_run_at_ms else "Never",
        'time_since_last_run_ms': time_since_last_run_ms,
        'time_since_last_run_str': f"{time_since_last_run_ms/1000:.0f} seconds" if time_since_last_run_ms else "N/A",
        'time_since_last_run_hrs': time_since_last_run_hrs,
        'next_run_at_ms': next_run_at_ms,
        'next_run_at_str': datetime.datetime.fromtimestamp(next_run_at_ms/1000, datetime.timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S %Z') if next_run_at_ms else "N/A",
        'schedule_expr': cron_expr,
        'interval_seconds': interval_seconds,
        'interval_ms': interval_ms,
        'overdue_factor': overdue_factor,
        'issues': issues
    }

def main():
    print("Analyzing SlashAI cron jobs...")
    results = []
    for job in jobs:
        results.append(analyze_job(job))
    
    # Generate report
    report_lines = []
    report_lines.append("# SlashAI Cron Health Report")
    report_lines.append(f"**Generated at**: {datetime.datetime.now().isoformat()}")
    report_lines.append(f"**Current time (ms since epoch)**: {current_time_ms}")
    report_lines.append("")
    
    # Summary
    total_jobs = len(results)
    enabled_jobs = sum(1 for r in results if r['enabled'])
    disabled_jobs = total_jobs - enabled_jobs
    healthy_jobs = sum(1 for r in results if len(r['issues']) == 0)
    
    report_lines.append(f"- **Healthy jobs**: {healthy_jobs}/{total_jobs} ({healthy_jobs/total_jobs*100:.1f}%)")
    report_lines.append("")
    
    report_lines.append("## Summary")
    report_lines.append(f"- Total jobs: {total_jobs}")
    report_lines.append(f"- Enabled jobs: {enabled_jobs}")
    report_lines.append(f"- Disabled jobs: {disabled_jobs}")
    report_lines.append("")
    
    # Individual job details
    for r in results:
        report_lines.append(f"### {r['name']} (ID: {r['id']})")
        report_lines.append(f"- **Enabled**: {r['enabled']}")
        report_lines.append(f"- **Last run status**: {r['last_run_status']}")
        report_lines.append(f"- **Last status**: {r['last_run_status']}")  # same
        report_lines.append(f"- **Consecutive errors**: {r['consecutive_errors']}")
        report_lines.append(f"- **Last run duration**: {r['last_duration_str']} ({r['last_duration_ms']} ms)")
        report_lines.append(f"- **Last run at**: {r['last_run_at_str']}")
        report_lines.append(f"- **Time since last run**: {r['time_since_last_run_str']} ({r['time_since_last_run_ms']} ms)")
        if r['time_since_last_run_hrs'] is not None:
            report_lines.append(f"- **Time since last run (hours)**: {r['time_since_last_run_hrs']:.2f} hrs")
        report_lines.append(f"- **Next run at**: {r['next_run_at_str']}")
        report_lines.append(f"- **Schedule expression**: {r['schedule_expr']}")
        if r['interval_seconds'] is not None:
            report_lines.append(f"- **Interval**: {r['interval_seconds']} seconds ({r['interval_seconds']/3600:.2f} hours)")
        if r['overdue_factor'] is not None:
            report_lines.append(f"- **Overdue factor**: {r['overdue_factor']:.2f} (time since last run / interval)")
        report_lines.append("")
        
        if r['issues']:
            report_lines.append("**Issues:**")
            for issue in r['issues']:
                report_lines.append(f"- {issue}")
        else:
            report_lines.append("**Issues:** None")
        report_lines.append("")
    
    # Issues Found section
    report_lines.append("## Issues Found")
    any_issues = False
    for r in results:
        if r['issues']:
            any_issues = True
            report_lines.append(f"### {r['name']} (ID: {r['id']})")
            for issue in r['issues']:
                report_lines.append(f"- {issue}")
            report_lines.append("")
    
    if not any_issues:
        report_lines.append("No issues found.")
    report_lines.append("")
    
    # Recommended Actions
    report_lines.append("## Recommended Actions")
    report_lines.append("1. Investigate and fix the issues listed above.")
    report_lines.append("2. For disabled jobs that should be enabled, check why they were disabled and re-enable if appropriate.")
    report_lines.append("3. For jobs with high consecutive errors, check the underlying cause and consider manual intervention.")
    report_lines.append("4. For jobs that haven't run in over 2x their interval, check if the scheduler is working correctly.")
    report_lines.append("5. For jobs with extremely long run times, consider optimizing the job or increasing timeout limits.")
    report_lines.append("")
    
    # Special Note: SlashAI Daily Tool Check
    daily_tool_check = next((r for r in results if r['id'] == '7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d'), None)
    if daily_tool_check:
        report_lines.append("## Special Note: SlashAI Daily Tool Check")
        if daily_tool_check['consecutive_errors'] <= CONSECUTIVE_ERROR_THRESHOLD:
            report_lines.append(f"The SlashAI Daily Tool Check job (ID: 7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d) has {daily_tool_check['consecutive_errors']} consecutive errors, which is within acceptable limits (<= {CONSECUTIVE_ERROR_THRESHOLD}). No manual trigger needed.")
        else:
            report_lines.append(f"The SlashAI Daily Tool Check job (ID: 7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d) has {daily_tool_check['consecutive_errors']} consecutive errors (> {CONSECUTIVE_ERROR_THRESHOLD}). Consider manually triggering it to test if the underlying issue is resolved.")
    
    # Write report
    report_path = 'cron-health-report.md'
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))
    
    print(f"Report written to {report_path}")
    
    # Also print summary to console
    print(f"\nSummary: {healthy_jobs}/{total_jobs} jobs healthy")
    if any_issues:
        print("Issues found - see report for details.")
    else:
        print("No issues found.")

if __name__ == '__main__':
    main()