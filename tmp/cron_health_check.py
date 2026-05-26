#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone

# Current time from prompt: 2026-05-18 23:02:00 UTC
# We'll use this fixed time for consistency
CURRENT_TIME_MS = 1777783320000  # 2026-05-18 23:02:00 UTC in milliseconds

def load_cron_jobs():
    """Load cron jobs from the JSON file."""
    jobs_file = '/home/rpi/.openclaw/workspace/projects/slashai/cron_jobs.json'
    try:
        with open(jobs_file, 'r') as f:
            data = json.load(f)
            return data.get('jobs', [])
    except Exception as e:
        print(f"Error loading cron jobs: {e}")
        return []

def analyze_job(job):
    """Analyze a single cron job and return health status."""
    job_id = job.get('id', 'unknown')
    name = job.get('name', 'Unknown Job')
    enabled = job.get('enabled', False)
    
    state = job.get('state', {})
    last_run_at_ms = state.get('lastRunAtMs', 0)
    last_run_status = state.get('lastRunStatus', state.get('lastStatus', 'unknown'))
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_duration_ms = state.get('lastDurationMs', 0)
    
    # Calculate time since last run
    time_since_last_run_ms = CURRENT_TIME_MS - last_run_at_ms if last_run_at_ms > 0 else float('inf')
    time_since_last_run_hours = time_since_last_run_ms / (1000 * 3600) if time_since_last_run_ms != float('inf') else float('inf')
    
    # Calculate expected interval from schedule (nextRunAtMs - lastRunAtMs)
    next_run_at_ms = job.get('nextRunAtMs', 0)
    expected_interval_ms = next_run_at_ms - last_run_at_ms if next_run_at_ms > 0 and last_run_at_ms > 0 else 0
    expected_interval_hours = expected_interval_ms / (1000 * 3600) if expected_interval_ms > 0 else 0
    
    # Determine issues
    issues = []
    if not enabled:
        issues.append("Job is disabled")
    if consecutive_errors > 2:
        issues.append(f"Consecutive errors: {consecutive_errors} (>2 threshold)")
    if expected_interval_ms > 0 and time_since_last_run_ms > (2 * expected_interval_ms):
        issues.append(f"Hasn't run in {time_since_last_run_hours:.1f}h (>2x expected interval of {expected_interval_hours:.1f}h)")
    if last_duration_ms > 3600000:  # > 1 hour
        issues.append(f"Extremely long run time: {last_duration_ms/(1000*60):.1f} minutes (>1 hour)")
    
    return {
        'id': job_id,
        'name': name,
        'enabled': enabled,
        'last_run_status': last_run_status,
        'consecutive_errors': consecutive_errors,
        'last_run_duration_ms': last_duration_ms,
        'last_run_duration_formatted': format_duration(last_duration_ms),
        'time_since_last_run_ms': time_since_last_run_ms,
        'time_since_last_run_formatted': format_duration(time_since_last_run_ms) if time_since_last_run_ms != float('inf') else 'Never',
        'expected_interval_hours': expected_interval_hours,
        'issues': issues,
        'healthy': len(issues) == 0
    }

def format_duration(ms):
    """Format milliseconds into human readable string."""
    if ms == float('inf'):
        return 'Never'
    seconds = ms / 1000
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"

def generate_report(job_analyses):
    """Generate a health report from job analyses."""
    total_jobs = len(job_analyses)
    healthy_jobs = sum(1 for j in job_analyses if j['healthy'])
    unhealthy_jobs = total_jobs - healthy_jobs
    
    report = []
    report.append("# SlashAI Cron Health Report")
    report.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report.append(f"**Current Time (UTC):** 2026-05-18 23:02:00")
    report.append("")
    report.append("## Summary")
    report.append(f"- Total Jobs: {total_jobs}")
    report.append(f"- Healthy Jobs: {healthy_jobs}")
    report.append(f"- Unhealthy Jobs: {unhealthy_jobs}")
    report.append(f"- Overall Health: {'✅ Good' if unhealthy_jobs == 0 else '⚠️ Issues Detected'}")
    report.append("")
    
    if unhealthy_jobs > 0:
        report.append("## ⚠️ Problematic Jobs Needing Attention")
        for job in job_analyses:
            if not job['healthy']:
                report.append(f"### {job['name']} (`{job['id']}`)")
                report.append(f"- **Status:** {'Enabled' if job['enabled'] else 'Disabled'}")
                report.append(f"- **Last Run:** {job['last_run_status']} ({job['time_since_last_run_formatted']} ago)")
                report.append(f"- **Consecutive Errors:** {job['consecutive_errors']}")
                report.append(f"- **Last Duration:** {job['last_run_duration_formatted']}")
                if job['issues']:
                    report.append(f"- **Issues:**")
                    for issue in job['issues']:
                        report.append(f"  - {issue}")
                report.append("")
    
    report.append("## 📋 All Jobs Details")
    for job in job_analyses:
        status_emoji = "✅" if job['healthy'] else "❌"
        report.append(f"### {status_emoji} {job['name']} (`{job['id']}`)")
        report.append(f"- **Enabled:** {'Yes' if job['enabled'] else 'No'}")
        report.append(f"- **Last Run Status:** {job['last_run_status']}")
        report.append(f"- **Consecutive Errors:** {job['consecutive_errors']}")
        report.append(f"- **Last Run Duration:** {job['last_run_duration_formatted']}")
        report.append(f"- **Time Since Last Run:** {job['time_since_last_run_formatted']}")
        if job['expected_interval_hours'] > 0:
            report.append(f"- **Expected Interval:** {job['expected_interval_hours']:.1f}h")
        report.append("")
    
    report.append("## 🛠️ Recommended Actions")
    if unhealthy_jobs == 0:
        report.append("- No immediate actions required. All cron jobs are healthy.")
    else:
        report.append("1. **Investigate disabled jobs** - Enable them if they should be running.")
        report.append("2. **Check jobs with consecutive errors** - Examine logs and fix underlying issues.")
        report.append("3. **Review stalled jobs** - Ensure they are not stuck or missing dependencies.")
        report.append("4. **Monitor long-running jobs** - Optimize or investigate why they exceed 1 hour.")
        report.append("")
        report.append("### Specific Actions:")
        for job in job_analyses:
            if not job['healthy']:
                report.append(f"- **{job['name']}:**")
                if not job['enabled']:
                    report.append("  - Enable the job")
                if job['consecutive_errors'] > 2:
                    report.append("  - Check recent logs and fix error cause")
                if job['time_since_last_run_ms'] > (2 * (job.get('nextRunAtMs',0) - job.get('state',{}).get('lastRunAtMs',0))) and job['expected_interval_hours'] > 0:
                    report.append("  - Investigate why job missed scheduled runs")
                if job['last_run_duration_ms'] > 3600000:
                    report.append("  - Optimize job performance or check for infinite loops")
    
    return "\n".join(report)

def main():
    print("Loading cron jobs...")
    jobs = load_cron_jobs()
    if not jobs:
        print("No cron jobs found or error loading jobs.")
        sys.exit(1)
    
    print(f"Analyzing {len(jobs)} cron jobs...")
    job_analyses = [analyze_job(job) for job in jobs]
    
    print("Generating health report...")
    report = generate_report(job_analyses)
    
    # Ensure output directory exists
    output_dir = '/home/rpi/.openclaw/workspace/projects/slashai'
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'cron-health-report.md')
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"Health report saved to: {output_file}")
    
    # Log completion
    log_file = '/home/rpi/.openclaw/workspace/logs/cron-health.log'
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now(timezone.utc).isoformat()} - Cron health check completed. Report saved to {output_file}\n")
    
    # Check if Daily Tool Check job has consecutive errors and trigger if needed
    daily_tool_job_id = "7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d"
    daily_tool_job = None
    for job in job_analyses:
        if job['id'] == daily_tool_job_id:
            daily_tool_job = job
            break
    
    if daily_tool_job and daily_tool_job['consecutive_errors'] > 0:
        print(f"Daily Tool Check job has {daily_tool_job['consecutive_errors']} consecutive errors. Triggering manually...")
        # In a real implementation, we would trigger the job here
        # For now, we'll just log it
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now(timezone.utc).isoformat()} - Daily Tool Check job has consecutive errors. Manual trigger would be performed.\n")
        print("Note: Manual trigger would be performed in a full implementation.")
    else:
        print("Daily Tool Check job is healthy or has no consecutive errors.")
    
    print("Cron health check completed successfully!")

if __name__ == "__main__":
    main()