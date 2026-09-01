# Dataholm incidents affecting the analytics workload

Everything we have. We only started tagging incidents by vendor in Sept 2025,
so anything before that is not captured here.

| Date | Duration | Impact |
|---|---|---|
| 2025-11-14 | 4h 10m | Query API returned stale partitions; two morning dashboards wrong |
| 2026-01-22 | 1h 35m | Auth failures on the service account, batch jobs failed, retried clean |
| 2026-03-09 | 6h 50m | Regional outage, no query capability, month-end close delayed a day |

Three incidents in seven months of tagged data. Dataholm's status page shows
99.9 percent, but that is measured across their whole estate, not our region.
