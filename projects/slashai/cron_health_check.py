#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone

# Load the cron jobs JSON
with open('/tmp/cron_jobs.json', 'r') as f:
    data = json.load(f)

jobs = data['jobs']

# Current time in milliseconds since epoch (we got from earlier date command)
# We'll compute it again to be safe
current_time_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

# Function to parse cron expression and approximate interval in seconds
def cron_to_interval_seconds(expr):
    # Very simple approximation for common patterns
    # We'll handle the specific expressions we know
    if expr == "0 */6 * * *":
        return 6 * 60 * 60  # 6 hours
    elif expr == "0 8 * * *":
        return 24 * 60 * 60  # daily
    elif expr == "0 10 * * *":
        return 24 * 60 * 60  # daily
    elif expr == "0 10 */14 * *":
        return 14 * 24 * 60 * 60  # biweekly
    elif expr == "0 10 1 * *":
        # monthly: approximate as 30 days
        return 30 * 24 * 60 * 60
    else:
        # Fallback: try to compute from nextRunAtMs and lastRunAtMs? We'll use 0 to indicate unknown
        return 0

issues = []
healthy_jobs = []

for job in jobs:
    job_id = job['id']
    name = job['name']
    enabled = job['enabled']
    last_run_status = job['state']['lastRunStatus']
    consecutive_errors = job['state']['consecutiveErrors']
    last_duration_ms = job['state']['lastDurationMs']
    last_run_at_ms = job['state']['lastRunAtMs']
    next_run_at_ms = job['state'].get('nextRunAtMs', 0)
    
    # Compute time since last run in seconds
    time_since_last_run_ms = current_time_ms - last_run_at_ms
    time_since_last_run_hours = time_since_last_run_ms / (1000 * 60 * 60)
    
    # Get cron expression
    expr = job['schedule']['expr']
    interval_seconds = cron_to_interval_seconds(expr)
    interval_hours = interval_seconds / (60 * 60) if interval_seconds > 0 else 0
    
    # Check for issues
    job_issues = []
    
    if not enabled:
        job_issues.append("Job is disabled")
    
    if consecutive_errors > 2:
        job_issues.append(f"Consecutive errors: {consecutive_errors}")
    
    if interval_seconds > 0:
        expected_interval_ms = interval_seconds * 1000
        if time_since_last_run_ms > 2 * expected_interval_ms:
            job_issues.append(f"Hasn't run in over 2x scheduled interval ({time_since_last_run_hours:.1f} hours > {2*interval_hours:.1f} hours)")
    
    if last_duration_ms > 3600000:  # 1 hour in ms
        job_issues.append(f"Extremely long run time: {last_duration_ms / (1000*60):.1f} minutes")
    
    if job_issues:
        issues.append({
            'id': job_id,
            'name': name,
            'issues': job_issues,
            'enabled': enabled,
            'last_run_status': last_run_status,
            'consecutive_errors': consecutive_errors,
            'last_duration_ms': last_duration_ms,
            'time_since_last_run_hours': time_since_last_run_hours
        })
    else:
        healthy_jobs.append({
            'id': job_id,
            'name': name,
            'enabled': enabled,
            'last_run_status': last_run_status,
            'consecutive_errors': consecutive_errors,
            'last_duration_ms': last_duration_ms,
            'time_since_last_run_hours': time_since_last_run_hours
        })

# Overall system health
total_jobs = len(jobs)
healthy_count = len(healthy_jobs)
issue_count = len(issues)
overall_health = "healthy" if issue_count == 0 else "degraded" if issue_count < total_jobs else "unhealthy"

# Recommended actions
recommendations = []
for issue in issues:
    for problem in issue['issues']:
        if "disabled" in problem.lower():
            recommendations.append(f"Enable job '{issue['name']}' (id: {issue['id']})")
        elif "consecutive errors" in problem.lower():
            recommendations.append(f"Investigate recurring failures for job '{issue['name']}' (id: {issue['id']})")
        elif "hasn't run" in problem.lower():
            recommendations.append(f"Check scheduler and system time for job '{issue['name']}' (id: {issue['id']})")
        elif "extremely long run time" in problem.lower():
            recommendations.append(f"Optimize or investigate long-running job '{issue['name']}' (id: {issue['id']})")

# Special check for SlashAI Daily Tool Check job (id: 7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d)
daily_tool_check_job = None
for job in jobs:
    if job['id'] == '7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d':
        daily_tool_check_job = job
        break

if daily_tool_check_job:
    consecutive_errors = daily_tool_check_job['state']['consecutiveErrors']
    if consecutive_errors > 0:
        recommendations.append(f"SlashAI Daily Tool Check job has {consecutive_errors} consecutive errors. Consider manually triggering it to test if the underlying issue is resolved.")

# Generate markdown report
report = f"""# SlashAI Cron Health Check Report

**Generated at:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
**Total Jobs:** {total_jobs}
**Healthy Jobs:** {healthy_count}
**Jobs with Issues:** {issue_count}
**Overall System Health:** {overall_health}

## Healthy Jobs
"""

if healthy_jobs:
    for job in healthy_jobs:
        report += f"- **{job['name']}** (ID: {job['id']})\n"
        report += f"  - Enabled: {job['enabled']}\n"
        report += f"  - Last Run Status: {job['last_run_status']}\n"
        report += f"  - Consecutive Errors: {job['consecutive_errors']}\n"
        report += f"  - Last Run Duration: {job['last_duration_ms'] / 1000:.1f} seconds\n"
        report += f"  - Time Since Last Run: {job['time_since_last_run_hours']:.1f} hours\n"
else:
    report += "None\n"

report += "\n## Jobs with Issues\n"
if issues:
    for job in issues:
        report += f"### {job['name']} (ID: {job['id']})\n"
        report += f"- **Enabled:** {job['enabled']}\n"
        report += f"- **Last Run Status:** {job['last_run_status']}\n"
        report += f"- **Consecutive Errors:** {job['consecutive_errors']}\n"
        report += f"- **Last Run Duration:** {job['last_duration_ms'] / 1000:.1f} seconds\n"
        report += f"- **Time Since Last Run:** {job['time_since_last_run_hours']:.1f} hours\n"
        report += f"- **Issues:**\n"
        for issue in job['issues']:
            report += f"  - {issue}\n"
        report += "\n"
else:
    report += "None\n"

report += "\n## Recommended Actions\n"
if recommendations:
    # Deduplicate recommendations
    seen = set()
    unique_recs = []
    for rec in recommendations:
        if rec not in seen:
            seen.add(rec)
            unique_recs.append(rec)
    for rec in unique_recs:
        report += f"- {rec}\n"
else:
    report += "No specific actions recommended.\n"

# Write the report to the specified file
report_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md'
with open(report_path, 'w') as f:
    f.write(report)

print(f"Health report written to {report_path}")