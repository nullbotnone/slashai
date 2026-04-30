# SlashAI Cron Health Report

**Generated at:** 2026-04-29T11:08:22.411124+00:00
**Current Time (ms):** 1777460902411
**Overall System Health:** POOR

## Summary
- Total Jobs: 6
- Enabled Jobs: 6
- Disabled Jobs: 0
- Last Run Status OK: 6
- Last Run Status Error: 0
- Jobs with Consecutive Errors > 2: 0
- Jobs Not Run in >2x Interval: 2
- Jobs with Runtime > 1 Hour: 1

## Issues Found (3 total)
- **SlashAI Cron Health Monitor** (ID: ed00fb94-c5de-40ee-ae13-fbca13331cd2): Haven't run in over 2x interval (129962932ms > 43199926ms)
- **SlashAI: Add new AI tools to directory** (ID: 2bf75b2b-2b7c-4ef9-a6fe-0c9680a15670): Haven't run in over 2x interval (126070768ms > 107136714ms)
- **SlashAI Weekly Article** (ID: c80f4c43-11b2-4ad7-a3c4-f71ff534ca85): Extremely long run time (3842637ms > 3600000ms)

## Recommended Actions
- Check scheduler and system time for job 'SlashAI Cron Health Monitor' (ID: ed00fb94-c5de-40ee-ae13-fbca13331cd2)
- Check scheduler and system time for job 'SlashAI: Add new AI tools to directory' (ID: 2bf75b2b-2b7c-4ef9-a6fe-0c9680a15670)
- Review and optimize job 'SlashAI Weekly Article' (ID: c80f4c43-11b2-4ad7-a3c4-f71ff534ca85) to reduce runtime
