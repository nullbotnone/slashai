import json
import re
from datetime import datetime, timezone
import sys

def parse_cron_interval(cron_expr):
    """
    Approximate interval in seconds for common cron expressions.
    Supports:
      - */n in minute/hour/day/month fields
      - fixed times with * for day/month/day-of-week
    Returns interval in seconds, or None if cannot determine.
    """
    # Split into fields
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        return None
    minute, hour, day_of_month, month, day_of_week = parts

    # Helper to check if field is '*'
    def is_star(s):
        return s.strip() == '*'

    # Helper to get step value from */n
    def get_step(field):
        match = re.match(r'\*/(\d+)', field)
        if match:
            return int(match.group(1))
        return None

    # Case: minute step
    if not is_star(minute):
        step = get_step(minute)
        if step:
            return step * 60  # minutes to seconds
    # Case: hour step
    if not is_star(hour):
        step = get_step(hour)
        if step:
            return step * 3600  # hours to seconds
    # Case: day-of-month step
    if not is_star(day_of_month):
        step = get_step(day_of_month)
        if step:
            return step * 86400  # days to seconds
    # Case: month step
    if not is_star(month):
        step = get_step(month)
        if step:
            return step * 30 * 86400  # approximate month
    # Case: day-of-week step
    if not is_star(day_of_week):
        step = get_step(day_of_week)
        if step:
            return step * 7 * 86400  # weeks

    # Fixed patterns:
    # If minute and hour are fixed, and day-of-month, month, day-of-week are '*'
    if (minute.isdigit() and hour.isdigit() and
        is_star(day_of_month) and is_star(month) and is_star(day_of_week)):
        # daily at specific hour:minute
        return 24 * 3600
    # If minute fixed, hour fixed, day-of-week fixed, others '*'
    if (minute.isdigit() and hour.isdigit() and day_of_week.isdigit() and
        is_star(day_of_month) and is_star(month)):
        # weekly on specific day-of-week at hour:minute
        return 7 * 24 * 3600
    # If minute fixed, hour fixed, day-of-month fixed, month '*', day-of-week '*'
    if (minute.isdigit() and hour.isdigit() and day_of_month.isdigit() and
        is_star(month) and is_star(day_of_week)):
        # monthly on specific day at hour:minute
        return 30 * 24 * 3600  # approximate
    # If minute fixed, hour fixed, day-of-month */14 (every 14 days)
    if (minute.isdigit() and hour.isdigit() and
        not is_star(day_of_month) and day_of_month.startswith('*/') and
        is_star(month) and is_star(day_of_week)):
        step = get_step(day_of_month)
        if step:
            return step * 24 * 3600
    # Fallback: cannot determine
    return None

def main():
    with open('cron_jobs_current.json', 'r') as f:
        data = json.load(f)
    jobs = data.get('jobs', [])
    # Get current time in milliseconds since epoch
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    print(f"Current time (UTC): {datetime.now(timezone.utc).isoformat()}")
    print(f"Current time ms: {now_ms}")
    print()
    report_lines = []
    report_lines.append("# SlashAI Cron Health Report")
    report_lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    report_lines.append("")
    report_lines.append("## Summary")
    # Initialize counters
    total_jobs = len(jobs)
    enabled_count = sum(1 for j in jobs if j.get('enabled'))
    disabled_count = total_jobs - enabled_count
    error_jobs = [j for j in jobs if j.get('state', {}).get('consecutiveErrors', 0) > 2]
    long_running_jobs = [j for j in jobs if j.get('state', {}).get('lastDurationMs', 0) > 3600000]
    # For overdue jobs, we need interval
    overdue_jobs = []
    for job in jobs:
        state = job.get('state', {})
        last_run_ms = state.get('lastRunAtMs', 0)
        if last_run_ms == 0:
            continue
        interval_sec = parse_cron_interval(job.get('schedule', {}).get('expr', ''))
        if interval_sec is None:
            continue
        interval_ms = interval_sec * 1000
        if (now_ms - last_run_ms) > 2 * interval_ms:
            overdue_jobs.append(job)
    # Overall health
    if not disabled_count and not error_jobs and not long_running_jobs and not overdue_jobs:
        health = "HEALTHY"
    else:
        health = "ISSUES DETECTED"
    report_lines.append(f"- **Overall Health**: {health}")
    report_lines.append(f"- Total Jobs: {total_jobs}")
    report_lines.append(f"- Enabled Jobs: {enabled_count}")
    report_lines.append(f"- Disabled Jobs: {disabled_count}")
    report_lines.append(f"- Jobs with >2 consecutive errors: {len(error_jobs)}")
    report_lines.append(f"- Jobs with run time >1 hour: {len(long_running_jobs)}")
    report_lines.append(f"- Jobs not run in >2x interval: {len(overdue_jobs)}")
    report_lines.append("")
    # Details per job
    report_lines.append("## Job Details")
    for job in jobs:
        jid = job.get('id')
        name = job.get('name')
        enabled = job.get('enabled')
        state = job.get('state', {})
        last_run_ms = state.get('lastRunAtMs')
        last_run_status = state.get('lastRunStatus', 'unknown')
        last_status = state.get('lastStatus', 'unknown')
        last_duration_ms = state.get('lastDurationMs', 0)
        consecutive_errors = state.get('consecutiveErrors', 0)
        next_run_ms = state.get('nextRunAtMs')
        # Compute derived
        time_since_last_ms = now_ms - last_run_ms if last_run_ms else None
        time_since_last_str = f"{time_since_last_ms // 1000} seconds" if time_since_last_ms is not None else "never"
        next_run_str = f"{next_run_ms}" if next_run_ms else "N/A"
        # Determine issues
        issues = []
        if not enabled:
            issues.append("DISABLED")
        if consecutive_errors > 2:
            issues.append(f"Consecutive errors: {consecutive_errors}")
        if last_duration_ms > 3600000:
            issues.append(f"Long run time: {last_duration_ms // 1000}s")
        interval_sec = parse_cron_interval(job.get('schedule', {}).get('expr', ''))
        if interval_sec and time_since_last_ms is not None:
            if time_since_last_ms > 2 * interval_sec * 1000:
                issues.append(f"Not run in >2x interval ({time_since_last_ms//1000}s > {2*interval_sec*1000//1000}s)")
        # Next run in past?
        if next_run_ms and next_run_ms < now_ms:
            overdue_by = (now_ms - next_run_ms) // 1000
            issues.append(f"Overdue by {overdue_by}s")
        report_lines.append(f"### {name} (`{jid}`)")
        report_lines.append(f"- Enabled: {enabled}")
        report_lines.append(f"- Schedule: {job.get('schedule', {}).get('expr', 'N/A')} (TZ: {job.get('schedule', {}).get('tz', 'N/A')})")
        report_lines.append(f"- Last Run: {time_since_last_str} ago (status: {last_run_status})")
        report_lines.append(f"- Last Duration: {last_duration_ms // 1000} seconds")
        report_lines.append(f"- Consecutive Errors: {consecutive_errors}")
        report_lines.append(f"- Next Run: {next_run_ms} (epoch ms)")
        if issues:
            report_lines.append(f"- **Issues**: {', '.join(issues)}")
        else:
            report_lines.append(f"- **Issues**: None")
        report_lines.append("")
    # Recommendations
    report_lines.append("## Recommendations")
    if disabled_count:
        report_lines.append("- Investigate why any jobs are disabled unexpectedly.")
    if error_jobs:
        report_lines.append("- Investigate jobs with repeated errors: " + ", ".join(j['name'] for j in error_jobs))
    if long_running_jobs:
        report_lines.append("- Review jobs with excessively long run times: " + ", ".join(j['name'] for j in long_running_jobs))
    if overdue_jobs:
        report_lines.append("- Check jobs that haven't run as expected: " + ", ".join(j['name'] for j in overdue_jobs))
    if not (disabled_count or error_jobs or long_running_jobs or overdue_jobs):
        report_lines.append("- No immediate action required. System appears healthy.")
    report_lines.append("")
    # Write to file
    output_path = "/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md"
    with open(output_path, 'w') as f:
        f.write("\n".join(report_lines))
    print(f"Report written to {output_path}")
    # Also print to stdout for logging
    print("\n".join(report_lines))

if __name__ == '__main__':
    main()
