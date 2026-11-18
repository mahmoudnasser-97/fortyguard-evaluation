# Evidence

Request bodies (`*_request.json`) and submit / error responses (`*_submit.json`) from my test runs, 13 November 2026.

| Test | Expected | Observed |
|---|---|---|
| `docs_single_hour` | Completed | Completed, 150 tiles, 4,220 credits |
| `fc_single_hour` | Completed | Identical to the above |
| `outside_us` | 400, not charged | 400 `OUT_OF_COVERAGE`, not charged |
| `broken_polygon` | 400, not charged | 400 (no `code`), not charged |
| `granularity_10` | 400 | **422** (no `code`), not charged |
| `date_2018` | 400 (docs: earliest 2019-01-01) | 400 `NO_COVERAGE`, "earliest supported date (2021-01-01)" |
| `date_2019` | **Accepted** per the docs | 400, "earliest supported date (2021-01-01)" |
| `date_2020` | **Accepted** per the docs | 400, "earliest supported date (2021-01-01)" |
| `granularity_20` | Completed | Completed, 4,207 tiles, 4,220 credits |
| `time_of_measure` | Completed | Completed, `window_utc` 10:00–21:00, all tiles = 19 |

Full `*_final.json` results are left out of the repo (FortyGuard data). See `REPORT.md` for the statistics.
