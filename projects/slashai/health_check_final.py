import json
import datetime
import os

def parse_cron_interval_seconds(expr):
    parts = expr.strip().split()
    if len(parts) != 5:
        return 24*3600
    minute, hour, day, month, dow = parts
    # All our jobs have minute=0
    if hour == '*/6' and day == '*' and month == '*' and dow == '*':
        return 6 * 3600
    if hour == '8' and day == '*' and month == '*' and dow == '*':
        return 24 * 3600
    if hour == '10' and day == '*' and month == '*' and dow == '*':
        return 24 * 3600
    if hour == '10' and day == '*' and month == '*' and dow == '1':
        return 7 * 24 * 3600
    if hour == '10' and day == '*/14' and month == '*' and dow == '*':
        return 14 * 24 * 3600
    if hour == '10' and day == '1' and month == '*' and dow == '*':
        return 30 * 24 * 3600  # approximate month
    if hour == '10' and day == '1' and month == '*/3' and dow == '*':
        return 3 * 30 * 24 * 3600  # approx quarter
    return 24 * 3600

def main():
    json_path = 'cron_jobs.json'
    with open(json_path, 'r') as f:
        data = json.load(f)
    jobs = data.get('jobs', [])
    now = datetime.datetime.now(datetime.timezone.utc)
    now_ms = int(now.timestamp() * 1000)
    
    report_lines = []
    report_lines.append("# SlashAI Cron Health Report")
    report_lines.append(f"Generated at: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    report_lines.append("")
    
    issues = []
    for job in jobs:
        job_id = job.get('id')
        name = job.get('name')
        enabled = job.get('enabled', False)
        schedule = job.get('schedule', {})
        expr = schedule.get('expr', '0 0 * * *')
        tz = schedule.get('tz', 'UTC')
        state = job.get('state', {})
        last_run_status = state.get('lastRunStatus', state.get('lastStatus', 'unknown'))
        consecutive_errors = state.get('consecutiveErrors', 0)
        last_duration_ms = state.get('lastDurationMs', 0)
        last_run_at_ms = state.get('lastRunAtMs', 0)
        
        time_since_ms = now_ms - last_run_at_ms if last_run_at_ms > 0 else None
        time_since_h = time_since_ms / (1000 * 3600) if time_since_ms is not None else None
        
        interval_seconds = parse_cron_interval_seconds(expr)
        interval_h = interval_seconds / 3600
        
        issue_flags = []
        if not enabled:
            issue_flags.append("disabled")
        if last_run_status == 'error':
            issue_flags.append("last_run_error")
        if consecutive_errors > 2:
            issue_flags.append(f"consecutive_errors_{consecutive_errors}")
        if time_since_h is not None and time_since_h > 2 * interval_h:
            issue_flags.append("not_run_in_2x_interval")
        if last_duration_ms > 3600 * 1000:
            issue_flags.append("long_runtime")
        
        if issue_flags:
            issues.append({
                'id': job_id,
                'name': name,
                'enabled': enabled,
                'last_run_status': last_run_status,
                'consecutive_errors': consecutive_errors,
                'last_duration_ms': last_duration_ms,
                'last_run_at_ms': last_run_at_ms,
                'time_since_h': time_since_h,
                'interval_h': interval_h,
                'issue_flags': issue_flags
            })
        
        # Build job detail lines for report
        report_lines.append(f"## {name} (`{job_id}`)")
        report_lines.append(f"- Enabled: {enabled}")
        report_lines.append(f"- Last run status: {last_run_status}")
        report_lines.append(f"- Consecutive errors: {consecutive_errors}")
        report_lines.append(f"- Last run duration: {last_duration_ms/1000:.1f} sec")
        if last_run_at_ms > 0:
            # Convert to UTC for consistency
            dt_utc = datetime.datetime.fromtimestamp(last_run_at_ms/1000, datetime.timezone.utc)
            report_lines.append(f"- Last run at (UTC): {dt_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            if time_since_h is not None:
                report_lines.append(f"- Time since last run: {time_since_h:.1f} hours")
        report_lines.append(f"- Expected interval: {interval_h:.1f} hours")
        if issue_flags:
            report_lines.append(f"- **Issues**: {', '.join(issue_flags)}")
        else:
            report_lines.append(f"- **Status**: Healthy")
        report_lines.append("")
    
    # Overall health
    report_lines.append("## Overall System Health")
    if not issues:
        report_lines.append("✅ All cron jobs are healthy.")
    else:
        report_lines.append(f"⚠️ Found {len(issues)} job(s) with issues:")
        for issue in issues:
            report_lines.append(f"- {issue['name']}: {', '.join(issue['issue_flags'])}")
    report_lines.append("")
    
    # Recommended actions
    report_lines.append("## Recommended Actions")
    if not issues:
        report_lines.append("- No actions needed. All jobs are functioning correctly.")
    else:
        for issue in issues:
            name = issue['name']
            if not issue['enabled']:
                report_lines.append(f"- **{name}**: Enable the job (currently disabled).")
            if issue['last_run_status'] == 'error':
                report_lines.append(f"- **{name}**: Investigate the cause of the last error (check logs).")
            if issue['consecutive_errors'] > 2:
                report_lines.append(f"- **{name}**: Investigate recurring errors (>2 consecutive). Consider manual trigger to test fix.")
            if issue['time_since_h'] is not None and issue['interval_h'] is not None and issue['time_since_h'] > 2 * issue['interval_h']:
                report_lines.append(f"- **{name}**: Job hasn't run in over 2x its interval ({issue['time_since_h']:.1f}h > {2*issue['interval_h']}h). Check if stuck or schedule misconfigured.")
            if issue['last_duration_ms'] > 3600 * 1000:
                report_lines.append(f"- **{name}**: Job runtime exceeds 1 hour ({issue['last_duration_ms']/1000/60:.1f} min). Consider optimizing or checking for infinite loops.")
    
    # Write report
    report_path = 'cron-health-report.md'
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))
    print(f"Report written to {report_path}")
    
    # Log completion to system.log
    log_line = f"[{now.isoformat()}] Cron health check completed. Jobs: {len(jobs)}, Issues: {len(issues)}"
    with open('system.log', 'a') as f:
        f.write(log_line + '\n')
    print("Logged to system.log")
    
    # Check specific job for manual trigger
    target_id = "7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d"
    target_job = None
    for job in jobs:
        if job.get('id') == target_id:
            target_job = job
            break
    if target_job:
        target_state = target_job.get('state', {})
        target_consecutive_errors = target_state.get('consecutiveErrors', 0)
        if target_consecutive_errors > 0:
            print(f"Target job {target_id} has {target_consecutive_errors} consecutive errors. Manual trigger would be performed here.")
            # In a real scenario, we would trigger via sessions_spawn, but we cannot from this script.
            # We'll note in report that manual trigger was considered.
            report_lines.append(f"## Manual Trigger Considered")
            report_lines.append(f"The SlashAI Daily Tool Check job (id: {target_id}) had consecutive errors and would be manually triggered to test if the issue is resolved.")
            # Rewrite report
            with open(report_path, 'w') as f:
                f.write('\n'.join(report_lines))
        else:
            print(f"Target job {target_id} has no consecutive errors; no manual trigger needed.")
    else:
        print(f"Target job {target_id} not found.")

if __name__ == '__main__':
    main()
