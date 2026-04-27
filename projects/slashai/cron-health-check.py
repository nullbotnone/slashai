#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timezone

# Current time in milliseconds (from the system, but we can also pass as argument)
# We'll get it from the command line or use the system time.
# For consistency with the cron data, we'll use the system time in milliseconds.
def get_current_time_ms():
    return int(datetime.now(timezone.utc).timestamp() * 1000)

def analyze_cron_jobs(jobs_json, current_time_ms):
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "current_time_ms": current_time_ms,
        "total_jobs": len(jobs_json),
        "jobs": [],
        "summary": {
            "enabled_count": 0,
            "disabled_count": 0,
            "ok_status_count": 0,
            "error_status_count": 0,
            "jobs_with_consecutive_errors_gt_2": 0,
            "jobs_not_run_in_2x_interval": 0,
            "jobs_with_long_runtime_gt_1h": 0,
            "overall_health": "good"  # will update based on issues
        },
        "issues": [],
        "recommended_actions": []
    }

    for job in jobs_json:
        job_info = {
            "id": job["id"],
            "name": job["name"],
            "enabled": job["enabled"],
            "last_run_status": job["state"]["lastRunStatus"],
            "consecutive_errors": job["state"]["consecutiveErrors"],
            "last_duration_ms": job["state"]["lastDurationMs"],
            "last_run_at_ms": job["state"]["lastRunAtMs"],
            "next_run_at_ms": job["state"]["nextRunAtMs"],
            "time_since_last_run_ms": current_time_ms - job["state"]["lastRunAtMs"],
            "expected_interval_ms": job["state"]["nextRunAtMs"] - job["state"]["lastRunAtMs"],
            "issues": []
        }

        # Update summary counts
        if job["enabled"]:
            report["summary"]["enabled_count"] += 1
        else:
            report["summary"]["disabled_count"] += 1

        if job["state"]["lastRunStatus"] == "ok":
            report["summary"]["ok_status_count"] += 1
        else:
            report["summary"]["error_status_count"] += 1

        # Check for issues
        if not job["enabled"]:
            job_info["issues"].append("Job is disabled")
            # Already counted in disabled_count above

        if job["state"]["consecutiveErrors"] > 2:
            job_info["issues"].append(f"Consecutive errors > 2 ({job['state']['consecutiveErrors']})")
            report["summary"]["jobs_with_consecutive_errors_gt_2"] += 1

        # Check if haven't run in over 2x scheduled interval
        # Avoid division by zero or negative interval (if next run is in the past, which shouldn't happen)
        expected_interval = job_info["expected_interval_ms"]
        if expected_interval > 0:
            time_since = job_info["time_since_last_run_ms"]
            if time_since > 2 * expected_interval:
                job_info["issues"].append(f"Haven't run in over 2x interval ({time_since}ms > {2*expected_interval}ms)")
                report["summary"]["jobs_not_run_in_2x_interval"] += 1

        # Check for extremely long run times (> 1 hour)
        if job_info["last_duration_ms"] > 3600000:  # 1 hour in milliseconds
            job_info["issues"].append(f"Extremely long run time ({job_info['last_duration_ms']}ms > 3600000ms)")
            report["summary"]["jobs_with_long_runtime_gt_1h"] += 1

        # If any issues, add to the job's issues and overall issues list
        if job_info["issues"]:
            report["jobs"].append(job_info)
            for issue in job_info["issues"]:
                report["issues"].append({
                    "job_id": job["id"],
                    "job_name": job["name"],
                    "issue": issue
                })

    # Determine overall health
    total_issues = len(report["issues"])
    if total_issues == 0:
        report["summary"]["overall_health"] = "good"
    elif total_issues <= 2:
        report["summary"]["overall_health"] = "fair"
    else:
        report["summary"]["overall_health"] = "poor"

    # Generate recommended actions
    for issue in report["issues"]:
        job_id = issue["job_id"]
        job_name = issue["job_name"]
        issue_text = issue["issue"]
        if "Job is disabled" in issue_text:
            report["recommended_actions"].append(f"Enable job '{job_name}' (ID: {job_id})")
        elif "Consecutive errors" in issue_text:
            report["recommended_actions"].append(f"Investigate and fix recurring errors for job '{job_name}' (ID: {job_id})")
        elif "Haven't run in over 2x interval" in issue_text:
            report["recommended_actions"].append(f"Check scheduler and system time for job '{job_name}' (ID: {job_id})")
        elif "Extremely long run time" in issue_text:
            report["recommended_actions"].append(f"Review and optimize job '{job_name}' (ID: {job_id}) to reduce runtime")

    # Remove duplicate recommended actions
    report["recommended_actions"] = list(dict.fromkeys(report["recommended_actions"]))

    return report

def main():
    # Read the JSON from stdin or from a file?
    # We'll get the JSON from the previous command output, but for now we'll read from a file.
    # However, we are in a script that will be run after we have the JSON.
    # Let's assume we pass the JSON as the first argument or read from stdin.
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    # The data from `openclaw cron list --all --json` has a "jobs" key
    if "jobs" in data:
        jobs = data["jobs"]
    else:
        # Assume the input is the array of jobs
        jobs = data

    current_time_ms = get_current_time_ms()
    report = analyze_cron_jobs(jobs, current_time_ms)

    # Output the report as JSON to a file
    output_path = "/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.json"
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    # Also create a markdown report
    markdown_report = f"""# SlashAI Cron Health Report

**Generated at:** {report['timestamp']}
**Current Time (ms):** {report['current_time_ms']}
**Overall System Health:** {report['summary']['overall_health'].upper()}

## Summary
- Total Jobs: {report['total_jobs']}
- Enabled Jobs: {report['summary']['enabled_count']}
- Disabled Jobs: {report['summary']['disabled_count']}
- Last Run Status OK: {report['summary']['ok_status_count']}
- Last Run Status Error: {report['summary']['error_status_count']}
- Jobs with Consecutive Errors > 2: {report['summary']['jobs_with_consecutive_errors_gt_2']}
- Jobs Not Run in >2x Interval: {report['summary']['jobs_not_run_in_2x_interval']}
- Jobs with Runtime > 1 Hour: {report['summary']['jobs_with_long_runtime_gt_1h']}

## Issues Found ({len(report['issues'])} total)
"""
    if report['issues']:
        for issue in report['issues']:
            markdown_report += f"- **{issue['job_name']}** (ID: {issue['job_id']}): {issue['issue']}\n"
    else:
        markdown_report += "No issues found.\n"

    markdown_report += "\n## Recommended Actions\n"
    if report['recommended_actions']:
        for action in report['recommended_actions']:
            markdown_report += f"- {action}\n"
    else:
        markdown_report += "No actions recommended.\n"

    # Write markdown report
    md_path = "/home/rpi/.openclaw/workspace/projects/slashai/cron-health-report.md"
    with open(md_path, 'w') as f:
        f.write(markdown_report)

    print(f"Health report saved to {output_path} and {md_path}")

    # Check if the SlashAI Daily Tool Check job has consecutive errors and trigger it if needed
    daily_tool_job_id = "7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d"
    daily_tool_job = None
    for job in jobs:
        if job["id"] == daily_tool_job_id:
            daily_tool_job = job
            break

    if daily_tool_job:
        consecutive_errors = daily_tool_job["state"]["consecutiveErrors"]
        if consecutive_errors > 0:
            print(f"SlashAI Daily Tool Check job has {consecutive_errors} consecutive errors. Triggering manually...")
            # Trigger the job using openclaw cron run
            import subprocess
            result = subprocess.run(["openclaw", "cron", "run", "--id", daily_tool_job_id], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Successfully triggered job {daily_tool_job_id}")
                print(f"Output: {result.stdout}")
            else:
                print(f"Failed to trigger job {daily_tool_job_id}")
                print(f"Error: {result.stderr}")
        else:
            print(f"SlashAI Daily Tool Check job has no consecutive errors ({consecutive_errors}). No manual trigger needed.")
    else:
        print(f"SlashAI Daily Tool Check job (ID: {daily_tool_job_id}) not found.")

if __name__ == "__main__":
    main()