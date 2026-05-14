#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timezone

def get_current_time_ms():
    return int(datetime.now(timezone.utc).timestamp() * 1000)

def main():
    # Read the cron jobs data
    with open('/home/rpi/.openclaw/workspace/projects/slashai/cron_jobs_current.json', 'r') as f:
        data = json.load(f)
    
    jobs = data['jobs']
    current_time_ms = get_current_time_ms()
    
    # Initialize report
    report_lines = []
    report_lines.append('# SlashAI Cron Health Report')
    report_lines.append(f'Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")}')
    report_lines.append('')
    
    # Summary
    total_jobs = len(jobs)
    enabled_jobs = sum(1 for j in jobs if j.get('enabled', False))
    disabled_jobs = total_jobs - enabled_jobs
    report_lines.append('## Summary')
    report_lines.append(f'- Total jobs: {total_jobs}')
    report_lines.append(f'- Enabled jobs: {enabled_jobs}')
    report_lines.append(f'- Disabled jobs: {disabled_jobs}')
    report_lines.append('')
    
    # Job details
    report_lines.append('## Job Details')
    problematic_jobs = []
    
    for job in jobs:
        jid = job['id']
        name = job['name']
        enabled = job.get('enabled', False)
        state = job.get('state', {})
        last_run_at = state.get('lastRunAtMs')
        last_run_status = state.get('lastRunStatus', state.get('lastStatus', 'unknown'))
        consecutive_errors = state.get('consecutiveErrors', 0)
        last_duration_ms = state.get('lastDurationMs', 0)
        
        # Time since last run
        if last_run_at:
            time_since_ms = current_time_ms - last_run_at
            time_since_hours = time_since_ms / (1000 * 60 * 60)
            time_since_str = f'{time_since_hours:.2f} hours'
        else:
            time_since_str = 'Never'
        
        # Issues detection
        issues = []
        if not enabled:
            issues.append('DISABLED')
        if consecutive_errors > 2:
            issues.append(f'High consecutive errors ({consecutive_errors})')
        if last_duration_ms > 3600000:  # > 1 hour
            issues.append(f'Long run time ({last_duration_ms/3600000:.2f} hours)')
        if last_run_at is None:
            issues.append('Never run')
        elif time_since_ms > 24 * 60 * 60 * 1000:  # > 1 day
            issues.append(f'Not run for {time_since_str}')
        
        # Add to problematic jobs if any issues
        if issues:
            problematic_jobs.append((jid, name, issues))
        
        # Job details in report
        report_lines.append(f'### {name} (`{jid}`)')
        report_lines.append(f'- Enabled: {enabled}')
        report_lines.append(f'- Last run status: {last_run_status}')
        report_lines.append(f'- Consecutive errors: {consecutive_errors}')
        report_lines.append(f'- Last run duration: {last_duration_ms} ms ({last_duration_ms/1000:.2f} s)')
        report_lines.append(f'- Time since last run: {time_since_str}')
        if issues:
            report_lines.append(f'- **Issues**: {", ".join(issues)}')
        else:
            report_lines.append('- **Issues**: None')
        report_lines.append('')
    
    # Recommended actions
    report_lines.append('## Recommended Actions')
    if problematic_jobs:
        for jid, name, issues in problematic_jobs:
            report_lines.append(f'- **{name}** (`{jid}`): {", ".join(issues)}')
    else:
        report_lines.append('- No problematic jobs detected.')
    
    report_lines.append('')
    
    # Special check for SlashAI Daily Tool Check job
    daily_tool_id = '7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d'
    for job in jobs:
        if job['id'] == daily_tool_id:
            state = job.get('state', {})
            consecutive_errors = state.get('consecutiveErrors', 0)
            if consecutive_errors > 0:
                report_lines.append('## Manual Trigger Test')
                report_lines.append(f'The SlashAI Daily Tool Check job has {consecutive_errors} consecutive errors. According to instructions, we should manually trigger it to test if the underlying issue is resolved.')
                report_lines.append(f'Note: Manual triggering would require invoking the agentTurn payload via the cron tool or direct agent invocation. This step is logged but not executed in this automated health check.')
            break
    
    # Write report
    with open('/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md', 'w') as f:
        f.write('\n'.join(report_lines))
    
    print('Health report written to cron-health-report.md')

if __name__ == '__main__':
    main()