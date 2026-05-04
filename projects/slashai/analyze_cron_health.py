#!/usr/bin/env python3
import json
import datetime
import os

def analyze_cron_jobs():
    # Load cron jobs data
    with open('/home/rpi/.openclaw/workspace/projects/slashai/cron_jobs.json', 'r') as f:
        data = json.load(f)
    
    jobs = data['jobs']
    # Use current time
    current_time = datetime.datetime.now(datetime.timezone.utc)
    current_time_ms = int(current_time.timestamp() * 1000)
    
    report = []
    report.append("# SlashAI Cron Health Report")
    report.append(f"Generated: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    report.append("")
    
    # Overall stats
    total_jobs = len(jobs)
    enabled_jobs = sum(1 for j in jobs if j['enabled'])
    disabled_jobs = total_jobs - enabled_jobs
    
    report.append("## Overall System Health")
    report.append(f"- Total Jobs: {total_jobs}")
    report.append(f"- Enabled Jobs: {enabled_jobs}")
    report.append(f"- Disabled Jobs: {disabled_jobs}")
    report.append("")
    
    # Analyze each job
    problematic_jobs = []
    
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
        time_since_last_run_ms = current_time_ms - last_run_at_ms if last_run_at_ms > 0 else float('inf')
        time_since_last_run_hours = time_since_last_run_ms / (1000 * 60 * 60) if time_since_last_run_ms != float('inf') else float('inf')
        
        # Get schedule interval (approximate)
        schedule_expr = job['schedule'].get('expr', '')
        interval_hours = None
        if schedule_expr:
            # Simple parsing for common schedules
            if '*/6 * * * *' in schedule_expr:  # Every 6 hours
                interval_hours = 6
            elif '0 8 * * *' in schedule_expr:  # Daily at 8 AM
                interval_hours = 24
            elif '0 10 * * *' in schedule_expr:  # Daily at 10 AM
                interval_hours = 24
            elif '0 10 */14 * *' in schedule_expr:  # Biweekly at 10 AM
                interval_hours = 24 * 14
            elif '0 10 1 * *' in schedule_expr:  # Monthly at 10 AM on day 1
                interval_hours = 24 * 30  # Approximate
            elif '0 10 * * 1' in schedule_expr:  # Weekly on Monday at 10 AM
                interval_hours = 24 * 7
        
        # Check for issues
        issues = []
        
        if not enabled:
            issues.append("Job is disabled")
        
        if consecutive_errors > 2:
            issues.append(f"Consecutive errors: {consecutive_errors} (>2)")
        
        if interval_hours and time_since_last_run_hours > (2 * interval_hours):
            issues.append(f"Not run in {time_since_last_run_hours:.1f}h (>{2*interval_hours}h expected)")
        
        if last_duration_ms > (60 * 60 * 1000):  # > 1 hour
            issues.append(f"Extremely long run time: {last_duration_ms/(60*60*1000):.1f}h")
        
        if issues:
            problematic_jobs.append({
                'id': job_id,
                'name': name,
                'enabled': enabled,
                'last_run_status': last_run_status,
                'consecutive_errors': consecutive_errors,
                'last_duration_hours': last_duration_ms/(60*60*1000) if last_duration_ms > 0 else 0,
                'time_since_last_run_hours': time_since_last_run_hours,
                'issues': issues
            })
        
        # Add to report details
        report.append(f"### {name} (ID: {job_id})")
        report.append(f"- **Enabled**: {enabled}")
        report.append(f"- **Last Run Status**: {last_run_status}")
        report.append(f"- **Consecutive Errors**: {consecutive_errors}")
        report.append(f"- **Last Run Duration**: {last_duration_ms/(60*60*1000):.2f} hours" if last_duration_ms > 0 else "- **Last Run Duration**: N/A")
        report.append(f"- **Time Since Last Run**: {time_since_last_run_hours:.1f} hours" if time_since_last_run_hours != float('inf') else "- **Time Since Last Run**: Never run")
        report.append(f"- **Next Scheduled Run**: {datetime.datetime.fromtimestamp(next_run_at_ms/1000, tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z') if next_run_at_ms > 0 else 'N/A'}")
        report.append("")
    
    # Summary of problematic jobs
    report.append("## Issues Identified")
    if problematic_jobs:
        report.append(f"Found {len(problematic_jobs)} problematic jobs:")
        report.append("")
        for job in problematic_jobs:
            report.append(f"### {job['name']}")
            for issue in job['issues']:
                report.append(f"- {issue}")
            report.append("")
    else:
        report.append("No issues found - all jobs are healthy!")
        report.append("")
    
    # Recommended actions
    report.append("## Recommended Actions")
    if problematic_jobs:
        report.append("1. Investigate and fix jobs with consecutive errors > 2")
        report.append("2. Enable any unexpectedly disabled jobs")
        report.append("3. Check jobs that haven't run in over 2x their scheduled interval")
        report.append("4. Investigate jobs with extremely long run times (> 1 hour)")
        
        # Special check for the Daily Tool Check job
        daily_tool_job = next((j for j in jobs if j['id'] == '7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d'), None)
        if daily_tool_job and daily_tool_job['state'].get('consecutiveErrors', 0) > 0:
            report.append("5. **MANUAL TRIGGER NEEDED**: SlashAI Daily Tool Check job has consecutive errors - manually trigger to test if issue is resolved")
    else:
        report.append("No actions needed - all jobs are healthy!")
    
    # Write report
    report_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md'
    with open(report_path, 'w') as f:
        f.write('\n'.join(report))
    
    print(f"Health report written to {report_path}")
    
    # Also create a JSON version for programmatic use
    json_report = {
        "generated_at": current_time_ms,
        "generated_at_iso": current_time.isoformat(),
        "total_jobs": total_jobs,
        "enabled_jobs": enabled_jobs,
        "disabled_jobs": disabled_jobs,
        "problematic_jobs": problematic_jobs,
        "overall_health": "healthy" if len(problematic_jobs) == 0 else "issues_found"
    }
    
    json_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.json'
    with open(json_path, 'w') as f:
        json.dump(json_report, f, indent=2)
    
    print(f"JSON report written to {json_path}")
    
    return len(problematic_jobs) == 0

if __name__ == "__main__":
    is_healthy = analyze_cron_jobs()
    exit(0 if is_healthy else 1)