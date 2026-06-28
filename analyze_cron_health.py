#!/usr/bin/env python3
import json
import time
from datetime import datetime, timezone
import croniter  # Need to check if available

# Since croniter might not be installed, I'll implement a simple cron interval estimator
# for common patterns, or use the difference between nextRunAtMs and lastRunAtMs as approximate interval

def estimate_interval_from_cron(cron_expr):
    """Estimate interval in seconds from cron expression for common patterns"""
    # Simple mapping for common schedules
    # This is not comprehensive but works for typical SlashAI jobs
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        return None  # Unknown format
    
    minute, hour, day, month, dow = parts
    
    # If all fields are specific numbers (not * or */n), it's a specific time
    # For daily: * * * * * is every minute, but we want common patterns
    
    # Check for @yearly, @monthly etc but our format is standard 5-field
    
    # Simple heuristics:
    if minute == '0' and hour == '*' and day == '*' and month == '*' and dow == '*':
        # Actually this is every hour at minute 0
        return 3600  # hourly
    if minute == '0' and hour == '0' and day == '*' and month == '*' and dow == '*':
        return 24 * 3600  # daily at midnight
    if minute == '0' and hour == '10' and day == '*' and month == '*' and dow == '*':
        return 24 * 3600  # daily at 10am
    if minute == '0' and hour == '10' and day == '1' and month == '*' and dow == '*':
        # monthly on the 1st at 10am - approximate as 30 days
        return 30 * 24 * 3600
    if minute == '0' and hour == '10' and day == '*' and month == '*' and dow == '0':
        # weekly on Sunday at 10am
        return 7 * 24 * 3600
    if minute == '*/15' and hour == '*' and day == '*' and month == '*' and dow == '*':
        return 15 * 60  # every 15 minutes
    if minute == '*/30' and hour == '*' and day == '*' and month == '*' and dow == '*':
        return 30 * 60  # every 30 minutes
    if minute == '0' and hour == '*/2' and day == '*' and month == '*' and dow == '*':
        return 2 * 3600  # every 2 hours
    
    # Fallback: try to compute using croniter if available, else return None
    try:
        import croniter
        now = datetime.now(timezone.utc)
        itr = croniter.croniter(cron_expr, now)
        next1 = int(next(datetime.timestamp(itr.get_next(datetime))) * 1000)
        next2 = int(next(datetime.timestamp(itr.get_next(datetime))) * 1000)
        return (next2 - next1) / 1000.0  # seconds
    except ImportError:
        pass
    except Exception:
        pass
    
    return None

def main():
    # Read current time from prompt (2026-06-26 00:02:00 America/Chicago)
    # Convert to timestamp
    # Using: 2026-06-26 05:02:00 UTC
    current_time_ms = 1782450120000  # precomputed
    
    # Load cron jobs
    with open('/home/rpi/.openclaw/workspace/projects/slashai/slashai/tmp/cron.json', 'r') as f:
        data = json.load(f)
    
    jobs = data.get('jobs', [])
    
    print(f"Found {len(jobs)} cron jobs")
    print(f"Current time: {datetime.fromtimestamp(current_time_ms/1000, tz=timezone.utc)}")
    print("=" * 80)
    
    issues = []
    healthy_jobs = []
    
    for job in jobs:
        job_id = job.get('id')
        name = job.get('name', 'Unknown')
        enabled = job.get('enabled', False)
        state = job.get('state', {})
        schedule = job.get('schedule', {})
        
        last_run_status = state.get('lastRunStatus', state.get('lastStatus', 'unknown'))
        consecutive_errors = state.get('consecutiveErrors', 0)
        last_duration_ms = state.get('lastDurationMs', 0)
        last_run_at_ms = state.get('lastRunAtMs', 0)
        next_run_at_ms = state.get('nextRunAtMs', 0)
        
        # Convert ms to seconds for readability
        last_duration_sec = last_duration_ms / 1000.0 if last_duration_ms else 0
        hours_since_last_run = (current_time_ms - last_run_at_ms) / (1000 * 3600) if last_run_at_ms > 0 else float('inf')
        
        # Determine if job has issues
        job_issues = []
        
        # Check 1: Job disabled unexpectedly
        # We don't know expected enabled state, but if it's disabled and has recent runs, maybe it was disabled intentionally?
        # For now, flag if disabled and last run was recent (within last 2*interval) and had errors==0?
        # Actually, the requirement is "Jobs disabled unexpectedly" - we need to know expected state.
        # Since we don't have expected state, we'll skip this or note if disabled.
        if not enabled:
            job_issues.append("Job is disabled")
        
        # Check 2: Consecutive errors > 2
        if consecutive_errors > 2:
            job_issues.append(f"Consecutive errors: {consecutive_errors} (>2)")
        
        # Check 3: Haven't run in over 2x scheduled interval
        if last_run_at_ms > 0:
            # Estimate interval
            cron_expr = schedule.get('expr') if schedule else None
            tz = schedule.get('tz', 'America/Chicago') if schedule else 'America/Chicago'
            
            interval_seconds = None
            if cron_expr:
                interval_seconds = estimate_interval_from_cron(cron_expr)
            
            # Fallback: use difference between nextRunAtMs and lastRunAtMs if available and reasonable
            if interval_seconds is None and next_run_at_ms > 0 and last_run_at_ms > 0:
                interval_seconds = (next_run_at_ms - last_run_at_ms) / 1000.0
                # Sanity check: if interval is too small (<30s) or too large (>1 year), ignore
                if interval_seconds < 30 or interval_seconds > 365*24*3600:
                    interval_seconds = None
            
            if interval_seconds is not None:
                max_allowed_seconds = 2 * interval_seconds
                actual_seconds_since_last_run = (current_time_ms - last_run_at_ms) / 1000.0
                if actual_seconds_since_last_run > max_allowed_seconds:
                    job_issues.append(f"Not run for {actual_seconds_since_last_run/3600:.1f}h (> {2*interval_seconds/3600:.1f}h = 2x interval)")
            else:
                # Cannot determine interval, skip this check
                pass
        
        # Check 4: Extremely long run times (> 1 hour)
        if last_duration_ms > 3600 * 1000:  # more than 1 hour in ms
            job_issues.append(f"Last run duration: {last_duration_sec/3600:.2f} hours (>1 hour)")
        
        if job_issues:
            issues.append({
                'id': job_id,
                'name': name,
                'enabled': enabled,
                'last_run_status': last_run_status,
                'consecutive_errors': consecutive_errors,
                'last_duration_sec': last_duration_sec,
                'hours_since_last_run': hours_since_last_run,
                'issues': job_issues
            })
        else:
            healthy_jobs.append({
                'id': job_id,
                'name': name,
                'enabled': enabled,
                'last_run_status': last_run_status,
                'consecutive_errors': consecutive_errors,
                'last_duration_sec': last_duration_sec,
                'hours_since_last_run': hours_since_last_run
            })
    
    # Print report
    print(f"\nHEALTH CHECK REPORT")
    print(f"Total jobs: {len(jobs)}")
    print(f"Healthy jobs: {len(healthy_jobs)}")
    print(f"Jobs with issues: {len(issues)}")
    print("=" * 80)
    
    if issues:
        print("\nJOBS WITH ISSUES:")
        for job in issues:
            print(f"\nJob: {job['name']} (ID: {job['id']})")
            print(f"  Enabled: {job['enabled']}")
            print(f"  Last run status: {job['last_run_status']}")
            print(f"  Consecutive errors: {job['consecutive_errors']}")
            print(f"  Last run duration: {job['last_duration_sec']:.2f}s")
            print(f"  Hours since last run: {job['hours_since_last_run']:.2f}")
            print(f"  Issues:")
            for issue in job['issues']:
                print(f"    - {issue}")
    else:
        print("\nAll jobs are healthy!")
    
    print("\nHEALTHY JOBS SUMMARY:")
    for job in healthy_jobs:
        status = "✓" if job['enabled'] and job['last_run_status'] == 'ok' and job['consecutive_errors'] == 0 else "?"
        print(f"  {status} {job['name']} (enabled:{job['enabled']}, status:{job['last_run_status']}, errors:{job['consecutive_errors']})")
    
    # Determine overall system health
    if len(issues) == 0:
        overall_health = "HEALTHY"
    elif len(issues) <= len(jobs) * 0.2:  # Less than 20% problematic
        overall_health = "WARNING"
    else:
        overall_health = "CRITICAL"
    
    print(f"\nOVERALL SYSTEM HEALTH: {overall_health}")
    
    # Recommended actions
    print("\nRECOMMENDED ACTIONS:")
    recommendations = []
    
    # Check for the specific job mentioned: SlashAI Daily Tool Check (id: 7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d)
    daily_tool_job = None
    for job in jobs:
        if job.get('id') == '7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d':
            daily_tool_job = job
            break
    
    if daily_tool_job:
        state = daily_tool_job.get('state', {})
        consecutive_errors = state.get('consecutiveErrors', 0)
        if consecutive_errors > 2:
            recommendations.append("Manually trigger SlashAI Daily Tool Check job (ID: 7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d) to test if underlying issue is resolved")
        else:
            recommendations.append("SlashAI Daily Tool Check job is healthy (consecutive errors: {})".format(consecutive_errors))
    else:
        recommendations.append("SlashAI Daily Tool Check job not found")
    
    # Add recommendations based on issues
    disabled_jobs = [j for j in issues if not j['enabled']]
    if disabled_jobs:
        recommendations.append(f"Review {len(disabled_jobs)} disabled job(s): {[j['name'] for j in disabled_jobs]}")
    
    high_error_jobs = [j for j in issues if j['consecutive_errors'] > 2]
    if high_error_jobs:
        recommendations.append(f"Investigate {len(high_error_jobs)} job(s) with >2 consecutive errors: {[j['name'] for j in high_error_jobs]}")
    
    long_running_jobs = [j for j in issues if j['last_duration_sec'] > 3600]
    if long_running_jobs:
        recommendations.append(f"Investigate {len(long_running_jobs)} job(s) with run time >1 hour: {[j['name'] for j in long_running_jobs]}")
    
    infrequent_jobs = [j for j in issues if any('Not run for' in issue for issue in j['issues'])]
    if infrequent_jobs:
        recommendations.append(f"Investigate {len(infrequent_jobs)} job(s) not running on schedule: {[j['name'] for j in infrequent_jobs]}")
    
    if not recommendations:
        recommendations.append("No specific actions needed. System is healthy.")
    
    for rec in recommendations:
        print(f"  - {rec}")
    
    # Generate markdown report
    markdown_report = f"""# SlashAI Cron Health Report

**Generated:** {datetime.fromtimestamp(current_time_ms/1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}
**Overall Health:** {overall_health}

## Summary
- Total Jobs: {len(jobs)}
- Healthy Jobs: {len(healthy_jobs)}
- Jobs with Issues: {len(issues)}

## Issues Found
"""
    
    if issues:
        for job in issues:
            markdown_report += f"""
### {job['name']} (ID: {job['id']})
- **Enabled:** {job['enabled']}
- **Last Run Status:** {job['last_run_status']}
- **Consecutive Errors:** {job['consecutive_errors']}
- **Last Run Duration:** {job['last_duration_sec']:.2f} seconds
- **Hours Since Last Run:** {job['hours_since_last_run']:.2f}
- **Issues:**
"""
            for issue in job['issues']:
                markdown_report += f"  - {issue}\n"
    else:
        markdown_report += "\nNo issues found. All jobs are healthy.\n"
    
    markdown_report += """
## Recommended Actions
"""
    for rec in recommendations:
        markdown_report += f"- {rec}\n"
    
    markdown_report += """
## Healthy Jobs Summary
"""
    for job in healthy_jobs:
        status_emoji = "✅" if job['enabled'] and job['last_run_status'] == 'ok' and job['consecutive_errors'] == 0 else "⚠️"
        markdown_report += f"- {status_emoji} {job['name']} (Enabled: {job['enabled']}, Status: {job['last_run_status']}, Errors: {job['consecutive_errors']})\n"
    
    # Save report
    report_path = '/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md'
    with open(report_path, 'w') as f:
        f.write(markdown_report)
    
    print(f"\nReport saved to: {report_path}")
    
    # Log completion to system logs
    log_message = f"Cron health check completed at {datetime.fromtimestamp(current_time_ms/1000, tz=timezone.utc).isoformat()}. Health: {overall_health}. Issues: {len(issues)}."
    try:
        with open('/home/rpi/.openclaw/workspace/projects/slashai/slashai/logs/cron-health.log', 'a') as f:
            f.write(log_message + '\n')
        print(f"Logged to system logs.")
    except Exception as e:
        print(f"Failed to write to log file: {e}")
        # Try alternative log location
        try:
            with open('/home/rpi/.openclaw/workspace/projects/slashai/cron-health-check.log', 'a') as f:
                f.write(log_message + '\n')
            print(f"Logged to alternative log file.")
        except Exception as e2:
            print(f"Failed to log to alternative file: {e2}")

if __name__ == '__main__':
    main()