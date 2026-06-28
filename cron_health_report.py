#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone

# Current time in milliseconds since epoch (UTC) as provided: 2026-06-26 23:02:00 UTC
# We computed: 1782514920000
current_time_ms = 1782514920000

# Mapping of cron expressions to interval in seconds (approximate)
cron_to_interval = {
    "0 */6 * * *": 6 * 3600,  # 6 hours
    "0 8 * * *": 24 * 3600,   # 1 day
    "0 10 * * *": 24 * 3600,  # 1 day
    "0 10 * * 1": 7 * 24 * 3600,  # 1 week
    "0 10 */14 * *": 14 * 24 * 3600,  # 2 weeks
    "0 10 1 * *": 30 * 24 * 3600,     # 1 month (approx)
}

# Path to the cron jobs JSON file
cron_jobs_file = "/home/rpi/.openclaw/workspace/projects/slashai/slashai/projects/slashai/cron_jobs.json"

# Output report file
report_file = "/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md"

def load_cron_jobs():
    with open(cron_jobs_file, 'r') as f:
        data = json.load(f)
    return data['jobs']

def analyze_job(job):
    issues = []
    # Enabled
    if not job.get('enabled', True):
        issues.append("Job is disabled")
    
    # Last run status
    state = job.get('state', {})
    last_run_status = state.get('lastRunStatus', state.get('lastStatus', 'unknown'))
    if last_run_status == 'error':
        issues.append(f"Last run status: {last_run_status}")
    
    # Consecutive errors
    consecutive_errors = state.get('consecutiveErrors', 0)
    if consecutive_errors > 2:
        issues.append(f"Consecutive errors: {consecutive_errors}")
    
    # Last run duration
    last_duration_ms = state.get('lastDurationMs', 0)
    if last_duration_ms > 3600000:  # > 1 hour
        issues.append(f"Last run duration: {last_duration_ms / 1000:.2f} seconds (>1 hour)")
    
    # Time since last run
    last_run_at_ms = state.get('lastRunAtMs', 0)
    if last_run_at_ms > 0:
        time_since_last_run_ms = current_time_ms - last_run_at_ms
        # Get interval from cron expression
        cron_expr = job.get('schedule', {}).get('expr')
        interval_sec = cron_to_interval.get(cron_expr)
        if interval_sec is not None:
            interval_ms = interval_sec * 1000
            if time_since_last_run_ms > 2 * interval_ms:
                issues.append(f"Time since last run: {time_since_last_run_ms / 1000:.0f}s > 2x interval ({interval_sec}s)")
        else:
            # If we don't know the interval, skip this check
            pass
    else:
        issues.append("Never run")
    
    return issues

def main():
    jobs = load_cron_jobs()
    
    report_lines = []
    report_lines.append("# SlashAI Cron Health Report")
    report_lines.append(f"Generated at: {datetime.fromtimestamp(current_time_ms/1000, tz=timezone.utc).isoformat()}")
    report_lines.append("")
    
    # Overall health
    total_jobs = len(jobs)
    healthy_jobs = 0
    problematic_jobs = []
    
    for job in jobs:
        issues = analyze_job(job)
        if not issues:
            healthy_jobs += 1
        else:
            problematic_jobs.append((job, issues))
    
    report_lines.append(f"## Summary")
    report_lines.append(f"- Total jobs: {total_jobs}")
    report_lines.append(f"- Healthy jobs: {healthy_jobs}")
    report_lines.append(f"- Jobs with issues: {len(problematic_jobs)}")
    report_lines.append("")
    
    if problematic_jobs:
        report_lines.append("## Issues Found")
        for job, issues in problematic_jobs:
            report_lines.append(f"### {job['name']} (ID: {job['id']})")
            for issue in issues:
                report_lines.append(f"- {issue}")
            report_lines.append("")
    else:
        report_lines.append("## No issues found")
        report_lines.append("")
    
    # Specific check for SlashAI Daily Tool Check job
    daily_tool_check_id = "7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d"
    daily_job = None
    for job in jobs:
        if job['id'] == daily_tool_check_id:
            daily_job = job
            break
    
    if daily_job:
        state = daily_job.get('state', {})
        consecutive_errors = state.get('consecutiveErrors', 0)
        report_lines.append("## SlashAI Daily Tool Check (ID: 7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d)")
        report_lines.append(f"- Consecutive errors: {consecutive_errors}")
        if consecutive_errors > 0:
            report_lines.append("- **ACTION REQUIRED**: Manually trigger this job to test if the underlying issue is resolved.")
        else:
            report_lines.append("- No consecutive errors.")
        report_lines.append("")
    
    # Write report
    with open(report_file, 'w') as f:
        f.write("\n".join(report_lines))
    
    print(f"Report written to {report_file}")

if __name__ == "__main__":
    main()