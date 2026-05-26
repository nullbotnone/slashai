# SlashAI Cron Health Report
Generated: 2026-05-26 11:02:00 UTC

## Summary
- Total jobs monitored: 6
- Healthy jobs: 1
- Jobs with issues: 5

## Issues Found
### SlashAI Cron Health Monitor (`ed00fb94-c5de-40ee-ae13-fbca13331cd2`)
- Not run in 564.0h (>12.0h threshold)

**Details:**
- Enabled: True
- Last run status: ok
- Consecutive errors: 0
- Last run duration: 3.1 minutes
- Time since last run: 564.0 hours
- Next run: 2026-05-03 05:02:19 UTC

### SlashAI Daily Tool Check (`7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d`)
- Not run in 574.0h (>48.0h threshold)

**Details:**
- Enabled: True
- Last run status: ok
- Consecutive errors: 0
- Last run duration: 12.0 minutes
- Time since last run: 574.0 hours
- Next run: 2026-05-03 13:00:00 UTC

### SlashAI: Add new AI tools to directory (`2bf75b2b-2b7c-4ef9-a6fe-0c9680a15670`)
- Not run in 572.0h (>48.0h threshold)

**Details:**
- Enabled: True
- Last run status: ok
- Consecutive errors: 0
- Last run duration: 8.8 minutes
- Time since last run: 572.0 hours
- Next run: 2026-05-03 15:00:00 UTC

### SlashAI Weekly Article (`c80f4c43-11b2-4ad7-a3c4-f71ff534ca85`)
- Not run in 691.9h (>336.0h threshold)
- Run time: 1.1h (threshold: >1h)

**Details:**
- Enabled: True
- Last run status: ok
- Consecutive errors: 0
- Last run duration: 64.0 minutes
- Time since last run: 691.9 hours
- Next run: 2026-05-04 15:00:00 UTC

### SlashAI Monthly What's New Roundup (`76dc4a93-9968-43b9-a383-cb00b7c0bf81`)
- Last run status: error

**Details:**
- Enabled: True
- Last run status: error
- Consecutive errors: 1
- Last run duration: 8.0 minutes
- Time since last run: 595.5 hours
- Next run: 2026-06-01 15:00:00 UTC

## Job Details
| Job Name | Enabled | Last Status | Errors | Duration (min) | Last Run (h ago) |
|----------|---------|-------------|--------|----------------|------------------|
| SlashAI Cron Health Monitor | True | ok | 0 | 3.1 | 564.0 |
| SlashAI Daily Tool Check | True | ok | 0 | 12.0 | 574.0 |
| SlashAI: Add new AI tools to directory | True | ok | 0 | 8.8 | 572.0 |
| SlashAI Weekly Article | True | ok | 0 | 64.0 | 691.9 |
| SlashAI Biweekly Tutorial | True | ok | 0 | 21.3 | 595.9 |
| SlashAI Monthly What's New Roundup | True | error | 1 | 8.0 | 595.5 |

## Recommended Actions
1. **Investigate long-running jobs**: The Weekly Article job takes over 1 hour to complete. Consider optimizing or checking for infinite loops.
2. **Fix failing job**: The Monthly What's New Roundup job has encountered an error. Check the error message: "⚠️ 📝 Edit: `in src/content/roundups/whats-new-ai-may-2026.md` failed"
3. **Monitor error counts**: While no jobs have >2 consecutive errors yet, keep an eye on the Monthly Roundup job.
4. **Consider alerts**: Set up notifications for jobs that fail or exceed expected run times.