# SlashAI Cron Health Report
Generated: 2026-05-12 11:06:43 UTC

## Overall System Health
- Total Jobs: 6
- Enabled Jobs: 6
- Disabled Jobs: 0

### SlashAI Cron Health Monitor (ID: ed00fb94-c5de-40ee-ae13-fbca13331cd2)
- **Enabled**: True
- **Last Run Status**: ok
- **Consecutive Errors**: 0
- **Last Run Duration**: 0.05 hours
- **Time Since Last Run**: 228.1 hours
- **Next Scheduled Run**: 2026-05-03 05:02:19 UTC

### SlashAI Daily Tool Check (ID: 7cfdddb8-eddd-4e8b-8ca3-a0eb6763ef7d)
- **Enabled**: True
- **Last Run Status**: ok
- **Consecutive Errors**: 0
- **Last Run Duration**: 0.20 hours
- **Time Since Last Run**: 238.1 hours
- **Next Scheduled Run**: 2026-05-03 13:00:00 UTC

### SlashAI: Add new AI tools to directory (ID: 2bf75b2b-2b7c-4ef9-a6fe-0c9680a15670)
- **Enabled**: True
- **Last Run Status**: ok
- **Consecutive Errors**: 0
- **Last Run Duration**: 0.15 hours
- **Time Since Last Run**: 236.1 hours
- **Next Scheduled Run**: 2026-05-03 15:00:00 UTC

### SlashAI Weekly Article (ID: c80f4c43-11b2-4ad7-a3c4-f71ff534ca85)
- **Enabled**: True
- **Last Run Status**: ok
- **Consecutive Errors**: 0
- **Last Run Duration**: 1.07 hours
- **Time Since Last Run**: 355.9 hours
- **Next Scheduled Run**: 2026-05-04 15:00:00 UTC

### SlashAI Biweekly Tutorial (ID: 233a2ab3-45ac-4cc0-ac40-8e998f9f4d90)
- **Enabled**: True
- **Last Run Status**: ok
- **Consecutive Errors**: 0
- **Last Run Duration**: 0.35 hours
- **Time Since Last Run**: 259.9 hours
- **Next Scheduled Run**: 2026-05-15 15:00:00 UTC

### SlashAI Monthly What's New Roundup (ID: 76dc4a93-9968-43b9-a383-cb00b7c0bf81)
- **Enabled**: True
- **Last Run Status**: error
- **Consecutive Errors**: 1
- **Last Run Duration**: 0.13 hours
- **Time Since Last Run**: 259.6 hours
- **Next Scheduled Run**: 2026-06-01 15:00:00 UTC

## Issues Identified
Found 3 problematic jobs:

### SlashAI Daily Tool Check
- Not run in 238.1h (>48h expected)

### SlashAI: Add new AI tools to directory
- Not run in 236.1h (>48h expected)

### SlashAI Weekly Article
- Not run in 355.9h (>336h expected)
- Extremely long run time: 1.1h

## Recommended Actions
1. Investigate and fix jobs with consecutive errors > 2
2. Enable any unexpectedly disabled jobs
3. Check jobs that haven't run in over 2x their scheduled interval
4. Investigate jobs with extremely long run times (> 1 hour)