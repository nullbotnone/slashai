#!/usr/bin/env python3
import json
import datetime
import os

# Current time in milliseconds (from system)
import time
current_time_ms = int(time.time() * 1000)
print(f"Current time: {datetime.datetime.fromtimestamp(current_time_ms/1000, datetime.timezone.utc)} UTC")

# Load the cron jobs current state
with open('projects/slashai/slashai/projects/slashai/cron_jobs_current.json', 'r') as f:
    data = json.load(f)

jobs = data['jobs']

# Analysis results
analysis = {
    'overall_health': 'good',
    'issues': [],
    'recommendations': [],
    'job_details': []
}

# Thresholds
CONSECUTIVE_ERROR_THRESHOLD = 2
LONG_RUN_TIME_MS = 3600000  # 1 hour in milliseconds

for job in jobs:
    job_id = job['id']
    name = job['name']
    enabled = job['enabled']
    state = job['state']
    
    last_run_at_ms = state.get('lastRunAtMs', 0)
    last_run_status = state.get('lastRunStatus', 'unknown')
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_duration_ms = state.get('lastDurationMs', 0)
    
    # Calculate time since last run
    time_since_last_run_ms = current_time_ms - last_run_at_ms if last_run_at_ms > 0 else float('inf')
    time_since_last_run_hours = time_since_last_run_ms / (1000 * 3600) if time_since_last_run_ms != float('inf') else float('inf')
    
    # Get schedule interval to check if haven't run in over 2x interval
    next_run_at_ms = state.get('nextRunAtMs', 0)
    if next_run_at_ms > 0 and last_run_at_ms > 0:
        # Approximate interval as time between last run and next run
        interval_ms = next_run_at_ms - last_run_at_ms
        # If haven't run in over 2x interval
        if time_since_last_run_ms > (2 * interval_ms):
            interval_issue = True
        else:
            interval_issue = False
    else:
        interval_issue = False
    
    # Check for issues
    issues = []
    if not enabled:
        issues.append('Job disabled unexpectedly')
    if consecutive_errors > CONSECUTIVE_ERROR_THRESHOLD:
        issues.append(f'Consecutive errors > {CONSECUTIVE_ERROR_THRESHOLD} ({consecutive_errors})')
    if interval_issue:
        issues.append(f'Has not run in over 2x scheduled interval ({time_since_last_run_hours:.1f} hours since last run)')
    if last_duration_ms > LONG_RUN_TIME_MS:
        issues.append(f'Extremely long run time (>1 hour): {last_duration_ms / (1000*3600):.2f} hours')
    
    # Job detail
    job_detail = {
        'id': job_id,
        'name': name,
        'enabled': enabled,
        'last_run_status': last_run_status,
        'consecutive_errors': consecutive_errors,
        'last_run_duration_ms': last_duration_ms,
        'last_duration_hours': last_duration_ms / (1000 * 3600) if last_duration_ms > 0 else 0,
        'time_since_last_run_hours': time_since_last_run_hours if time_since_last_run_ms != float('inf') else None,
        'issues': issues
    }
    
    analysis['job_details'].append(job_detail)
    
    # Collect issues for overall health
    if issues:
        analysis['issues'].extend([{'job_id': job_id, 'job_name': name, 'issue': issue} for issue in issues])

# Determine overall health
if any(not job['enabled'] for job in jobs):
    analysis['overall_health'] = 'poor'
elif any(job['consecutive_errors'] > CONSECUTIVE_ERROR_THRESHOLD for job in jobs):
    analysis['overall_health'] = 'poor'
elif any(job['last_duration_ms'] > LONG_RUN_TIME_MS for job in jobs):
    analysis['overall_health'] = 'poor'
elif any(issue['issue'].startswith('Has not run in over 2x') for issue in analysis['issues']):
    analysis['overall_health'] = 'degraded'
else:
    analysis['overall_health'] = 'good'

# Generate recommendations
for job in analysis['job_details']:
    if job['issues']:
        for issue in job['issues']:
            if 'disabled' in issue.lower():
                analysis['recommendations'].append(f"Enable job '{job['name']}' (ID: {job['id']})")
            elif 'consecutive errors' in issue.lower():
                analysis['recommendations'].append(f"Investigate recurring failures for job '{job['name']}' (ID: {job['id']}) - {job['consecutive_errors']} consecutive errors")
            elif 'not run in over 2x' in issue.lower():
                analysis['recommendations'].append(f"Check job '{job['name']}' (ID: {job['id']}) - it hasn't run as expected")
            elif 'extremely long run time' in issue.lower():
                analysis['recommendations'].append(f"Investigate performance issue for job '{job['name']}' (ID: {job['id']}) - runs for {job['last_duration_hours']:.2f} hours")

# Special check for SlashAI Daily Tool Check job
daily_tool_check_job = next((job for job in jobs if job['id'] == '7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d'), None)
if daily_tool_check_job:
    state = daily_tool_check_job['state']
    if state.get('consecutiveErrors', 0) > 0:
        analysis['recommendations'].append("SlashAI Daily Tool Check job shows consecutive errors - consider manually triggering to test if underlying issue is resolved")
        # We could trigger it here, but for now just note in recommendations

# Generate report
report = f"""# SlashAI Cron Health Report
**Generated:** {datetime.datetime.fromtimestamp(current_time_ms/1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}
**Overall System Health:** {analysis['overall_health'].upper()}

## Summary
- Total Jobs Monitored: {len(jobs)}
- Jobs with Issues: {len(set(issue['job_id'] for issue in analysis['issues']))}
- Total Issues Found: {len(analysis['issues'])}

## Job Details

"""

for job in analysis['job_details']:
    report += f"""### {job['name']} (ID: {job['id']})
- **Status:** {'ENABLED' if job['enabled'] else 'DISABLED'}
- **Last Run:** {datetime.datetime.fromtimestamp(job.get('last_run_at_ms', 0)/1000, datetime.timezone.utc) if job.get('last_run_at_ms', 0) > 0 else 'Never'} ({job['last_run_status']})
- **Consecutive Errors:** {job['consecutive_errors']}
- **Last Run Duration:** {job['last_duration_hours']:.2f} hours ({job['last_duration_ms']} ms)
- **Time Since Last Run:** {job['time_since_last_run_hours']:.2f} hours ({job['time_since_last_run_hours']*60:.0f} minutes) if job['time_since_last_run_hours'] is not else 'N/A'

"""
    if job['issues']:
        report += f"- **ISSUES:**\n"
        for issue in job['issues']:
            report += f"  - {issue}\n"
    else:
        report += f"- **Status:** No issues detected\n"
    report += "\n"

report += f"""## Issues Requiring Attention
"""

if analysis['issues']:
    for issue in analysis['issues']:
        report += f"- **{issue['job_name']}** (ID: {issue['job_id']}): {issue['issue']}\n"
else:
    report += "No issues detected.\n"

report += f"""
## Recommendations
"""

if analysis['recommendations']:
    # Deduplicate recommendations
    seen = set()
    for rec in analysis['recommendations']:
        if rec not in seen:
            report += f"- {rec}\n"
            seen.add(rec)
else:
    report += "- No specific actions required at this time.\n"

report += f"""
## Next Steps
1. Review any disabled jobs and re-enable if appropriate
2. Investigate jobs with consecutive errors > 2
3. Check jobs that haven't run in over 2x their scheduled interval
4. Monitor jobs with extremely long run times for performance issues
5. Consider setting up alerts for cron job failures

---
*This report was generated automatically by the SlashAI Cron Health Monitor.*
"""

# Save report to the specified location
output_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md'
with open(output_path, 'w') as f:
    f.write(report)

print(f"Health report saved to: {output_path}")

# Also save a JSON version for machine readability
json_output_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.json'
with open(json_output_path, 'w') as f:
    json.dump(analysis, f, indent=2)
print(f"JSON report saved to: {json_output_path}")

# Log completion status (we'll just print for now, but could write to a log file)
print("Cron health check completed successfully.")