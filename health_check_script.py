import json
import datetime
import re
import subprocess
import os

def parse_cron_interval(cron_expr):
    """
    Approximate interval in seconds for common cron expressions.
    Supports:
      */n in minute, hour, day_of_month, month, day_of_week
      Fixed times with * for other fields.
    Returns seconds or None if cannot determine.
    """
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        return None
    minute, hour, day_of_month, month, day_of_week = parts

    def is_star(s):
        return s.strip() == '*'

    def get_step(field):
        m = re.match(r'\*/(\d+)', field)
        if m:
            return int(m.group(1))
        return None

    # minute step
    if not is_star(minute):
        step = get_step(minute)
        if step:
            return step * 60
    # hour step
    if not is_star(hour):
        step = get_step(hour)
        if step:
            return step * 3600
    # day of month step
    if not is_star(day_of_month):
        step = get_step(day_of_month)
        if step:
            return step * 86400
    # month step
    if not is_star(month):
        step = get_step(month)
        if step:
            # approximate month as 30 days
            return step * 30 * 86400
    # day of week step
    if not is_star(day_of_week):
        step = get_step(day_of_week)
        if step:
            return step * 7 * 86400

    # Fixed patterns
    # minute and hour fixed, others *
    if (minute.isdigit() and hour.isdigit() and
            is_star(day_of_month) and is_star(month) and is_star(day_of_week)):
        return 24 * 3600  # daily
    # minute, hour, day_of_week fixed, others *
    if (minute.isdigit() and hour.isdigit() and day_of_week.isdigit() and
            is_star(day_of_month) and is_star(month)):
        return 7 * 24 * 3600  # weekly
    # minute, hour, day_of_month fixed, month *, day_of_week *
    if (minute.isdigit() and hour.isdigit() and day_of_month.isdigit() and
            is_star(month) and is_star(day_of_week)):
        return 30 * 24 * 3600  # monthly approx
    # minute, hour fixed, day_of_month */n
    if (minute.isdigit() and hour.isdigit() and
            not is_star(day_of_month) and day_of_month.startswith('*/') and
            is_star(month) and is_star(day_of_week)):
        step = get_step(day_of_month)
        if step:
            return step * 86400
    return None

def main():
    # Load cron jobs live data
    json_path = 'cron_jobs_live.json'
    with open(json_path, 'r') as f:
        data = json.load(f)
    jobs = data.get('jobs', [])

    # Current time in America/Chicago (UTC-5)
    # Assuming offset -5 hours (DST) as per problem statement
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    offset = datetime.timedelta(hours=-5)  # America/Chicago summer time
    now_local = now_utc + offset
    now_ms = int(now_local.timestamp() * 1000)

    report_lines = []
    report_lines.append("# SlashAI Cron Health Report")
    report_lines.append(f"Generated: {now_local.isoformat()}")
    report_lines.append("")
    report_lines.append("## Summary")
    total_jobs = len(jobs)
    enabled_count = sum(1 for j in j if j.get('enabled'))
    # We'll compute issues per job
    issue_counts = {
        'disabled': 0,
        'errors_gt_2': 0,
        'overdue': 0,
        'long_runtime': 0
    }
    job_details = []

    for job in jobs:
        jid = job.get('id')
        name = job.get('name')
        enabled = job.get('enabled', False)
        schedule = job.get('schedule', {})
        expr = schedule.get('expr', '')
        state = job.get('state', {})
        last_run_status = state.get('lastRunStatus', 'unknown')
        last_status = state.get('lastStatus', 'unknown')
        last_duration_ms = state.get('lastDurationMs', 0)
        consecutive_errors = state.get('consecutiveErrors', 0)
        last_run_at_ms = state.get('lastRunAtMs', 0)
        next_run_at_ms = state.get('nextRunAtMs', 0)

        # Compute interval seconds
        interval_sec = parse_cron_interval(expr)
        # Time since last run
        if last_run_at_ms > 0:
            time_since_last_ms = now_ms - last_run_at_ms
        else:
            time_since_last_ms = float('inf')
        overdue = False
        if interval_sec is not None and last_run_at_ms > 0:
            if time_since_last_ms > 2 * interval_sec * 1000:
                overdue = True
        long_runtime = last_duration_ms > 3600000  # 1 hour
        excessive_errors = consecutive_errors > 2
        disabled = not enabled

        issues = []
        if disabled:
            issues.append("DISABLED")
            issue_counts['disabled'] += 1
        if excessive_errors:
            issues.append(f"Consecutive errors: {consecutive_errors}")
            issue_counts['errors_gt_2'] += 1
        if overdue:
            issues.append(f"Not run in >2x interval ({time_since_last_ms/1000:.0f}s > {2*interval_sec if interval_sec else 0}s)")
            issue_counts['overdue'] += 1
        if long_runtime:
            issues.append(f"Long runtime: {last_duration_ms/1000:.0f}s")
            issue_counts['long_runtime'] += 1

        job_details.append({
            'id': jid,
            'name': name,
            'enabled': enabled,
            'last_run_status': last_run_status,
            'last_duration_ms': last_duration_ms,
            'consecutive_errors': consecutive_errors,
            'last_run_at_ms': last_run_at_ms,
            'issues': issues,
            'expr': expr,
            'next_run_at_ms': next_run_at_ms
        })

    # Determine overall health
    total_issues = sum(issue_counts.values())
    if total_issues == 0:
        health = "HEALTHY - No issues detected"
    else:
        health = f"ISSUES DETECTED: {total_issues} problem(s) across {len([j for j in job_details if j['issues']])} job(s)"

    report_lines.append(f"- **Overall Health**: {health}")
    report_lines.append(f"- Total Jobs: {total_jobs}")
    report_lines.append(f"- Enabled Jobs: {enabled_count}")
    report_lines.append(f"- Disabled Jobs: {issue_counts['disabled']}")
    report_lines.append(f"- Jobs with >2 consecutive errors: {issue_counts['errors_gt_2']}")
    report_lines.append(f"- Jobs overdue (>2x interval): {issue_counts['overdue']}")
    report_lines.append(f"- Jobs with runtime >1 hour: {issue_counts['long_runtime']}")
    report_lines.append("")
    report_lines.append("## Job Details")
    for jd in job_details:
        report_lines.append(f"### {jd['name']} (`{jid}`)")
        report_lines.append(f"- ID: {jd['id']}")
        report_lines.append(f"- Enabled: {jd['enabled']}")
        report_lines.append(f"- Schedule: {jd['expr']} (America/Chicago)")
        report_lines.append(f"- Last Run: {jd['last_run_status']} ({jd['last_duration_ms']//1000}s ago) at {datetime.datetime.fromtimestamp(jd['last_run_at_ms']/1000, datetime.timezone.utc).isoformat() if jd['last_run_at_ms'] else 'Never'}")
        report_lines.append(f"- Consecutive Errors: {jd['consecutive_errors']}")
        report_lines.append(f"- Next Run: {datetime.datetime.fromtimestamp(jd['next_run_at_ms']/1000, datetime.timezone.utc).isoformat() if jd['next_run_at_ms'] else 'N/A'}")
        if jd['issues']:
            report_lines.append(f"- **ISSUES**: {', '.join(jd['issues'])}")
        else:
            report_lines.append("- **ISSUES**: None")
        report_lines.append("")

    # Check if we need to trigger the Daily Tool Check job
    target_id = "7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d"
    target_job = next((j for j in job_details if j['id'] == target_id), None)
    if target_job and target_job['consecutive_errors'] > 2:
        report_lines.append("## Action Taken")
        report_lines.append(f"The job '{target_job['name']}' has {target_job['consecutive_errors']} consecutive errors (>2). Triggering manual run...")
        # Execute the trigger command
        try:
            subprocess.run(["openclaw", "cron", "run", "--id", target_id], check=True, capture_output=True, text=True)
            report_lines.append("Trigger command executed successfully.")
        except subprocess.CalledProcessError as e:
            report_lines.append(f"Failed to trigger job: {e}")
            report_lines.append(f"stderr: {e.stderr}")
        except Exception as e:
            report_lines.append(f"Unexpected error: {e}")

    # Write report
    report_path = "cron-health-report.md"
    with open(report_path, 'w') as f:
        f.write("\n".join(report_lines))
    print(f"Report written to {report_path}")

    # Log completion to system.log (in workspace root)
    log_path = "/home/rpi/.openclaw/workspace/system.log"
    timestamp = datetime.datetime.now().isoformat()
    status_msg = f"[{timestamp}] Cron health check completed. Health: {health}"
    try:
        with open(log_path, 'a') as f:
            f.write(status_msg + "\n")
        print(f"Logged to {log_path}")
    except Exception as e:
        print(f"Failed to write to system log: {e}")

if __name__ == "__main__":
    main()
